import { apiRequest } from './client';
import {
  Interaction,
  InteractionCreate,
  DataResponse,
  PaginatedResponse,
} from '../types';

export interface ListInteractionsParams {
  page?: number;
  page_size?: number;
  client_id?: string;
  channel?: string;
  direction?: string;
  interaction_type?: string;
  intent_category?: string;
}

export async function listInteractions(
  params: ListInteractionsParams = {}
): Promise<PaginatedResponse<Interaction>> {
  const query = new URLSearchParams();
  if (params.page) query.append('page', String(params.page));
  if (params.page_size) query.append('page_size', String(params.page_size));
  if (params.client_id) query.append('client_id', params.client_id);
  if (params.channel) query.append('channel', params.channel);
  if (params.direction) query.append('direction', params.direction);
  if (params.interaction_type) query.append('interaction_type', params.interaction_type);
  if (params.intent_category) query.append('intent_category', params.intent_category);

  const qs = query.toString();
  return apiRequest<PaginatedResponse<Interaction>>(`/interactions${qs ? `?${qs}` : ''}`);
}

export async function getInteraction(id: string): Promise<Interaction> {
  const res = await apiRequest<DataResponse<Interaction>>(`/interactions/${id}`);
  return res.data;
}

export async function createInteraction(payload: InteractionCreate): Promise<Interaction> {
  const res = await apiRequest<DataResponse<Interaction>>('/interactions', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return res.data;
}
