import { apiRequest } from './client';
import {
  ApprovedInformation,
  ApprovedInformationCreate,
  ApprovedInformationUpdate,
  DataResponse,
  PaginatedResponse,
} from '../types';

export interface ListApprovedInfoParams {
  page?: number;
  page_size?: number;
  category?: string;
  is_active?: boolean;
}

export async function listApprovedInformation(
  params: ListApprovedInfoParams = {}
): Promise<PaginatedResponse<ApprovedInformation>> {
  const query = new URLSearchParams();
  if (params.page) query.append('page', String(params.page));
  if (params.page_size) query.append('page_size', String(params.page_size));
  if (params.category) query.append('category', params.category);
  if (params.is_active !== undefined) query.append('is_active', String(params.is_active));

  const qs = query.toString();
  return apiRequest<PaginatedResponse<ApprovedInformation>>(
    `/approved-information${qs ? `?${qs}` : ''}`
  );
}

export async function getApprovedInformation(id: string): Promise<ApprovedInformation> {
  const res = await apiRequest<DataResponse<ApprovedInformation>>(`/approved-information/${id}`);
  return res.data;
}

export async function createApprovedInformation(
  payload: ApprovedInformationCreate
): Promise<ApprovedInformation> {
  const res = await apiRequest<DataResponse<ApprovedInformation>>('/approved-information', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return res.data;
}

export async function updateApprovedInformation(
  id: string,
  payload: ApprovedInformationUpdate
): Promise<ApprovedInformation> {
  const res = await apiRequest<DataResponse<ApprovedInformation>>(`/approved-information/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
  return res.data;
}
