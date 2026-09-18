import { apiRequest } from './client';
import {
  FollowUpTask,
  FollowUpCreate,
  FollowUpUpdate,
  DataResponse,
  PaginatedResponse,
} from '../types';

export interface ListFollowUpsParams {
  page?: number;
  page_size?: number;
  client_id?: string;
  status?: string;
  priority?: string;
  assigned_to?: string;
}

export async function listFollowUps(
  params: ListFollowUpsParams = {}
): Promise<PaginatedResponse<FollowUpTask>> {
  const query = new URLSearchParams();
  if (params.page) query.append('page', String(params.page));
  if (params.page_size) query.append('page_size', String(params.page_size));
  if (params.client_id) query.append('client_id', params.client_id);
  if (params.status) query.append('status', params.status);
  if (params.priority) query.append('priority', params.priority);
  if (params.assigned_to) query.append('assigned_to', params.assigned_to);

  const qs = query.toString();
  return apiRequest<PaginatedResponse<FollowUpTask>>(`/followups${qs ? `?${qs}` : ''}`);
}

export async function getFollowUp(id: string): Promise<FollowUpTask> {
  const res = await apiRequest<DataResponse<FollowUpTask>>(`/followups/${id}`);
  return res.data;
}

export async function createFollowUp(payload: FollowUpCreate): Promise<FollowUpTask> {
  const res = await apiRequest<DataResponse<FollowUpTask>>('/followups', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return res.data;
}

export async function updateFollowUp(
  id: string,
  payload: FollowUpUpdate
): Promise<FollowUpTask> {
  const res = await apiRequest<DataResponse<FollowUpTask>>(`/followups/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
  return res.data;
}
