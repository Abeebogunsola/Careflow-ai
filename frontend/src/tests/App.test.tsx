import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { App } from '../App';

// Mock API calls made on mount
vi.mock('../api', () => ({
  getHealth: vi.fn().mockResolvedValue({
    status: 'ok',
    database: 'ok',
    service: 'careflow-api',
    version: '1.0.0',
  }),
  listClients: vi.fn().mockResolvedValue({
    data: [],
    pagination: { page: 1, page_size: 100, total: 0 },
  }),
  listAppointments: vi.fn().mockResolvedValue({
    data: [],
    pagination: { page: 1, page_size: 100, total: 0 },
  }),
  listFollowUps: vi.fn().mockResolvedValue({
    data: [],
    pagination: { page: 1, page_size: 100, total: 0 },
  }),
  listEscalations: vi.fn().mockResolvedValue({
    data: [],
    pagination: { page: 1, page_size: 100, total: 0 },
  }),
  listInteractions: vi.fn().mockResolvedValue({
    data: [],
    pagination: { page: 1, page_size: 20, total: 0 },
  }),
  listApprovedInformation: vi.fn().mockResolvedValue({
    data: [],
    pagination: { page: 1, page_size: 100, total: 0 },
  }),
}));

describe('CareFlow AI Application Shell & Navigation', () => {
  it('renders application brand, sidebar navigation links, and header', async () => {
    render(<App />);

    // Brand title in sidebar
    expect(screen.getByText(/CareFlow/i)).toBeInTheDocument();
    expect(screen.getByText(/HIV Care Retention Platform/i)).toBeInTheDocument();

    // Key navigation links
    expect(screen.getByRole('link', { name: /^dashboard$/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^clients$/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^appointments$/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^interactions$/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^follow-ups$/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^escalations$/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^approved info$/i })).toBeInTheDocument();

    // Synthetic data notice
    expect(screen.getByText(/SYNTHETIC DEMO DATA/i)).toBeInTheDocument();

    // Wait for async state resolution
    await waitFor(() => {
      expect(screen.getByText(/CARE RETENTION METRICS/i)).toBeInTheDocument();
    });
  });
});
