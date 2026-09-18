import { apiRequest } from './client';
import {
  Client,
  ClientCreate,
  ClientUpdate,
  CommunicationPreference,
  CommunicationPreferenceCreate,
  DataResponse,
  PaginatedResponse,
} from '../types';

export interface ListClientsParams {
  page?: number;
  page_size?: number;
  status?: string;
  preferred_language?: string;
}

export async function listClients(
  params: ListClientsParams = {}
): Promise<PaginatedResponse<Client>> {
  const query = new URLSearchParams();
  if (params.page) query.append('page', String(params.page));
  if (params.page_size) query.append('page_size', String(params.page_size));
  if (params.status) query.append('status', params.status);
  if (params.preferred_language) query.append('preferred_language', params.preferred_language);

  const qs = query.toString();
  return apiRequest<PaginatedResponse<Client>>(`/clients${qs ? `?${qs}` : ''}`);
}

export async function getClient(id: string): Promise<Client> {
  const res = await apiRequest<DataResponse<Client>>(`/clients/${id}`);
  return res.data;
}

export async function createClient(payload: ClientCreate): Promise<Client> {
  const res = await apiRequest<DataResponse<Client>>('/clients', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return res.data;
}

export async function updateClient(id: string, payload: ClientUpdate): Promise<Client> {
  const res = await apiRequest<DataResponse<Client>>(`/clients/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
  return res.data;
}

export async function getCommunicationPreference(
  clientId: string
): Promise<CommunicationPreference | null> {
  try {
    const res = await apiRequest<DataResponse<CommunicationPreference>>(
      `/clients/${clientId}/communication-preference`
    );
    return res.data;
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'statusCode' in err && (err as { statusCode: number }).statusCode === 404) {
      return null;
    }
    throw err;
  }
}

export async function setCommunicationPreference(
  clientId: string,
  payload: CommunicationPreferenceCreate
): Promise<CommunicationPreference> {
  const res = await apiRequest<DataResponse<CommunicationPreference>>(
    `/clients/${clientId}/communication-preference`,
    {
      method: 'PUT',
      body: JSON.stringify(payload),
    }
  );
  return res.data;
}
