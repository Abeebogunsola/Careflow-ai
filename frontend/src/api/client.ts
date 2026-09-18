/**
 * CareFlow AI — Typed Base API Client
 * Wraps Fetch with base URL routing, envelope unwrapping, and safe error normalization.
 */

const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export class ApiError extends Error {
  public statusCode: number;
  public details?: unknown;

  constructor(message: string, statusCode: number, details?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.details = details;
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    ...(options.headers as Record<string, string>),
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 204) {
      return {} as T;
    }

    const json = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMessage =
        json?.detail ||
        json?.error?.message ||
        `Request failed with status ${response.status}`;
      throw new ApiError(errorMessage, response.status, json?.error?.details || json?.detail);
    }

    return json as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    const msg = error instanceof Error ? error.message : 'Network error or service unavailable';
    throw new ApiError(msg, 0);
  }
}
