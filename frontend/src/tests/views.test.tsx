import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { DashboardPage } from '../pages/DashboardPage';
import { ClientsPage } from '../pages/ClientsPage';
import { AppointmentsPage } from '../pages/AppointmentsPage';
import { FollowUpsPage } from '../pages/FollowUpsPage';
import { EscalationsPage } from '../pages/EscalationsPage';
import { InteractionsPage } from '../pages/InteractionsPage';
import { ApprovedInfoPage } from '../pages/ApprovedInfoPage';

// Mock API module
vi.mock('../api', () => ({
  getHealth: vi.fn().mockResolvedValue({
    status: 'ok',
    database: 'ok',
    service: 'careflow-api',
    version: '1.0.0',
  }),
  listClients: vi.fn().mockResolvedValue({
    data: [
      {
        id: 'c1111111-1111-1111-1111-111111111111',
        external_reference: 'SYNTH-CLI-001',
        preferred_name: 'Alex Morgan',
        preferred_language: 'en',
        enrollment_status: 'active',
        is_active: true,
        created_at: '2026-03-01T10:00:00Z',
      },
    ],
    pagination: { page: 1, page_size: 100, total: 1 },
  }),
  listAppointments: vi.fn().mockResolvedValue({
    data: [
      {
        id: 'a1111111-1111-1111-1111-111111111111',
        client_id: 'c1111111-1111-1111-1111-111111111111',
        appointment_type: 'viral_load',
        scheduled_at: '2026-04-10T09:30:00Z',
        status: 'scheduled',
        location_label: 'Clinic Alpha',
      },
    ],
    pagination: { page: 1, page_size: 100, total: 1 },
  }),
  listFollowUps: vi.fn().mockResolvedValue({
    data: [
      {
        id: 'f1111111-1111-1111-1111-111111111111',
        client_id: 'c1111111-1111-1111-1111-111111111111',
        reason: 'Reported bus transit fare barrier',
        priority: 'high',
        status: 'pending',
        created_at: '2026-03-15T12:00:00Z',
      },
    ],
    pagination: { page: 1, page_size: 100, total: 1 },
  }),
  listEscalations: vi.fn().mockResolvedValue({
    data: [
      {
        id: 'e1111111-1111-1111-1111-111111111111',
        client_id: 'c1111111-1111-1111-1111-111111111111',
        category: 'clinical_concern',
        priority: 'urgent',
        reason: 'Client inquired about severe medication side effects',
        status: 'open',
        created_at: '2026-03-18T14:00:00Z',
      },
    ],
    pagination: { page: 1, page_size: 100, total: 1 },
  }),
  listInteractions: vi.fn().mockResolvedValue({
    data: [
      {
        id: 'i1111111-1111-1111-1111-111111111111',
        client_id: 'c1111111-1111-1111-1111-111111111111',
        channel: 'sms',
        direction: 'incoming',
        interaction_type: 'client_query',
        intent_category: 'appointment_inquiry',
        content: 'When is my next lab visit scheduled?',
        created_at: '2026-03-18T08:00:00Z',
      },
    ],
    pagination: { page: 1, page_size: 20, total: 1 },
  }),
  listApprovedInformation: vi.fn().mockResolvedValue({
    data: [
      {
        id: 'info1111-1111-1111-1111-111111111111',
        category: 'clinic_hours',
        title: 'Central Outpatient Operating Hours',
        content: 'The clinic is open Monday to Friday from 8:00 AM to 4:30 PM.',
        is_active: true,
      },
    ],
    pagination: { page: 1, page_size: 100, total: 1 },
  }),
  createClient: vi.fn().mockResolvedValue({}),
  createAppointment: vi.fn().mockResolvedValue({}),
  createFollowUp: vi.fn().mockResolvedValue({}),
  createEscalation: vi.fn().mockResolvedValue({}),
}));

describe('Frontend Feature Views & User Flow Testing', () => {
  it('renders DashboardPage with operational summary cards and action buttons', async () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    // Await async data resolution
    await waitFor(() => {
      expect(screen.getByText(/Care Retention Overview/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Add Client/i })).toBeInTheDocument();
      expect(screen.getByText(/Active Clients/i)).toBeInTheDocument();
      expect(screen.getByText(/Pending Tasks/i)).toBeInTheDocument();
    });
  });

  it('renders ClientsPage and displays client record in table', async () => {
    render(
      <MemoryRouter>
        <ClientsPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Client Directory/i })).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/Search by reference/i)).toBeInTheDocument();
      expect(screen.getByText('Alex Morgan')).toBeInTheDocument();
      expect(screen.getByText('SYNTH-CLI-001')).toBeInTheDocument();
    });
  });

  it('renders AppointmentsPage and displays scheduled appointment', async () => {
    render(
      <MemoryRouter>
        <AppointmentsPage />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { name: /Care Appointments/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/Clinic Alpha/i)).toBeInTheDocument();
      expect(screen.getByText(/viral load/i)).toBeInTheDocument();
    });
  });

  it('renders FollowUpsPage and shows barrier task with priority label', async () => {
    render(
      <MemoryRouter>
        <FollowUpsPage />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { name: /Care Navigation & Outreach Tasks/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/Reported bus transit fare barrier/i)).toBeInTheDocument();
    });
  });

  it('renders EscalationsPage and displays open clinical escalation', async () => {
    render(
      <MemoryRouter>
        <EscalationsPage />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { name: /Clinical & Support Escalations/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/severe medication side effects/i)).toBeInTheDocument();
    });
  });

  it('renders InteractionsPage and shows communication log entry', async () => {
    render(
      <MemoryRouter>
        <InteractionsPage />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { name: /Interactions & Communication Ledger/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/When is my next lab visit scheduled/i)).toBeInTheDocument();
    });
  });

  it('renders ApprovedInfoPage and displays knowledge repository item', async () => {
    render(
      <MemoryRouter>
        <ApprovedInfoPage />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { name: /Approved Information & AI Knowledge Base/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/Central Outpatient Operating Hours/i)).toBeInTheDocument();
      expect(screen.getByText(/8:00 AM to 4:30 PM/i)).toBeInTheDocument();
    });
  });
});
