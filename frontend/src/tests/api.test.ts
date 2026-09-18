import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiRequest, ApiError } from '../api/client';
import { listClients, getClient } from '../api/clients';
import { listAppointments } from '../api/appointments';

describe('API Client Layer', () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it('successfully makes GET request and returns json data', async () => {
    const mockData = {
      data: [{ id: 'client-1', preferred_name: 'Test Patient', enrollment_status: 'active' }],
      pagination: { page: 1, page_size: 10, total: 1 },
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockData,
    } as unknown as Response);

    const res = await listClients({ page: 1, page_size: 10 });
    expect(res.data).toHaveLength(1);
    expect(res.data[0].preferred_name).toBe('Test Patient');
  });

  it('normalizes API error responses into ApiError', async () => {
    const errorPayload = {
      error: {
        code: 'NOT_FOUND',
        message: 'Client record not found',
      },
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => errorPayload,
    } as unknown as Response);

    await expect(getClient('invalid-id')).rejects.toThrow('Client record not found');
  });

  it('correctly builds query parameters for appointments list', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ data: [], pagination: { page: 1, page_size: 20, total: 0 } }),
    } as unknown as Response);

    globalThis.fetch = fetchMock;

    await listAppointments({
      client_id: 'client-123',
      status: 'scheduled',
      page: 2,
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const calledUrl = fetchMock.mock.calls[0][0] as string;
    expect(calledUrl).toContain('client_id=client-123');
    expect(calledUrl).toContain('status=scheduled');
    expect(calledUrl).toContain('page=2');
  });
});
