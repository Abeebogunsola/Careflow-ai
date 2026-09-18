import { apiRequest } from './client';
import {
  Appointment,
  AppointmentCreate,
  AppointmentUpdate,
  DataResponse,
  PaginatedResponse,
} from '../types';

export interface ListAppointmentsParams {
  page?: number;
  page_size?: number;
  client_id?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
}

export async function listAppointments(
  params: ListAppointmentsParams = {}
): Promise<PaginatedResponse<Appointment>> {
  const query = new URLSearchParams();
  if (params.page) query.append('page', String(params.page));
  if (params.page_size) query.append('page_size', String(params.page_size));
  if (params.client_id) query.append('client_id', params.client_id);
  if (params.status) query.append('status', params.status);
  if (params.start_date) query.append('start_date', params.start_date);
  if (params.end_date) query.append('end_date', params.end_date);

  const qs = query.toString();
  return apiRequest<PaginatedResponse<Appointment>>(`/appointments${qs ? `?${qs}` : ''}`);
}

export async function getAppointment(id: string): Promise<Appointment> {
  const res = await apiRequest<DataResponse<Appointment>>(`/appointments/${id}`);
  return res.data;
}

export async function createAppointment(payload: AppointmentCreate): Promise<Appointment> {
  const res = await apiRequest<DataResponse<Appointment>>('/appointments', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return res.data;
}

export async function updateAppointment(
  id: string,
  payload: AppointmentUpdate
): Promise<Appointment> {
  const res = await apiRequest<DataResponse<Appointment>>(`/appointments/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
  return res.data;
}
