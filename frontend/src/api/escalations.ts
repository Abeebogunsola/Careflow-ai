import { apiRequest } from './client';
import {
  Escalation,
  EscalationCreate,
  EscalationUpdate,
  DataResponse,
  PaginatedResponse,
} from '../types';

export interface ListEscalationsParams {
  page?: number;
  page_size?: number;
  client_id?: string;
  status?: string;
  category?: string;
  priority?: string;
  assigned_to?: string;
}

export async function listEscalations(
  params: ListEscalationsParams = {}
): Promise<PaginatedResponse<Escalation>> {
  const query = new URLSearchParams();
  if (params.page) query.append('page', String(params.page));
  if (params.page_size) query.append('page_size', String(params.page_size));
  if (params.client_id) query.append('client_id', params.client_id);
  if (params.status) query.append('status', params.status);
  if (params.category) query.append('category', params.category);
  if (params.priority) query.append('priority', params.priority);
  if (params.assigned_to) query.append('assigned_to', params.assigned_to);

  const qs = query.toString();
  return apiRequest<PaginatedResponse<Escalation>>(`/escalations${qs ? `?${qs}` : ''}`);
}

export async function getEscalation(id: string): Promise<Escalation> {
  const res = await apiRequest<DataResponse<Escalation>>(`/escalations/${id}`);
  return res.data;
}

export async function createEscalation(payload: EscalationCreate): Promise<Escalation> {
  const res = await apiRequest<DataResponse<Escalation>>('/escalations', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return res.data;
}

export async function updateEscalation(
  id: string,
  payload: EscalationUpdate
): Promise<Escalation> {
  const res = await apiRequest<DataResponse<Escalation>>(`/escalations/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
  return res.data;
}
