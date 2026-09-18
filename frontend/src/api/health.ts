import { apiRequest } from './client';
import { DataResponse, HealthData } from '../types';

export async function getHealth(): Promise<HealthData> {
  const res = await apiRequest<DataResponse<HealthData>>('/health');
  return res.data;
}
