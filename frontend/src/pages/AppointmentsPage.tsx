import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  Calendar,
  PlusCircle,
  CheckCircle2,
  XCircle,
  Clock,
  MapPin,
  Filter,
  RefreshCw,
  Search,
  User,
  AlertCircle,
} from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Pagination } from '../components/common/Pagination';
import { ScheduleAppointmentModal } from '../components/modals/ScheduleAppointmentModal';
import { listAppointments, updateAppointment, listClients } from '../api';
import { Appointment, Client } from '../types';

export const AppointmentsPage: React.FC = () => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [clientsMap, setClientsMap] = useState<Record<string, Client>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;
  const [isScheduleModalOpen, setIsScheduleModalOpen] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [apptsRes, clientsRes] = await Promise.all([
        listAppointments({ page: 1, page_size: 100 }),
        listClients({ page: 1, page_size: 100 }),
      ]);

      setAppointments(apptsRes.data);

      const map: Record<string, Client> = {};
      clientsRes.data.forEach((c) => {
        map[c.id] = c;
      });
      setClientsMap(map);
    } catch (err) {
      console.error('Failed to load appointments:', err);
      setError('Unable to load appointments. Please check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleUpdateStatus = async (
    id: string,
    status: 'completed' | 'missed' | 'cancelled'
  ) => {
    try {
      const updated = await updateAppointment(id, { status });
      setAppointments((prev) => prev.map((a) => (a.id === id ? updated : a)));
    } catch (err) {
      console.error('Failed to update status:', err);
      alert('Could not update appointment status.');
    }
  };

  // Filter and search
  const filteredAppointments = useMemo(() => {
    return appointments.filter((a) => {
      const client = clientsMap[a.client_id];
      const clientName = client ? client.preferred_name.toLowerCase() : '';
      const clientRef = client && client.external_reference ? client.external_reference.toLowerCase() : '';
      const typeStr = a.appointment_type.toLowerCase();
      const locStr = (a.location_label || '').toLowerCase();
      const q = searchQuery.toLowerCase().trim();

      const matchesSearch =
        q === '' ||
        clientName.includes(q) ||
        clientRef.includes(q) ||
        typeStr.includes(q) ||
        locStr.includes(q);

      const matchesStatus =
        statusFilter === 'all' || a.status.toLowerCase() === statusFilter.toLowerCase();

      return matchesSearch && matchesStatus;
    });
  }, [appointments, clientsMap, searchQuery, statusFilter]);

  // Sort by scheduled_at ascending for upcoming, descending for past
  const sortedAppointments = useMemo(() => {
    return [...filteredAppointments].sort(
      (a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime()
    );
  }, [filteredAppointments]);

  // Pagination
  const totalPages = Math.ceil(sortedAppointments.length / pageSize) || 1;
  const paginatedAppointments = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedAppointments.slice(start, start + pageSize);
  }, [sortedAppointments, currentPage, pageSize]);

  // Quick metrics
  const scheduledCount = appointments.filter((a) => a.status === 'scheduled').length;
  const completedCount = appointments.filter((a) => a.status === 'completed').length;
  const missedCount = appointments.filter((a) => a.status === 'missed').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header Bar */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '16px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--primary-100)',
              color: 'var(--primary-700)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Calendar size={22} />
          </div>
          <div>
            <h1 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, margin: 0 }}>
              Care Appointments & Medication Refills
            </h1>
            <p style={{ margin: 0, fontSize: 'var(--font-size-sm)', color: 'var(--text-muted)' }}>
              Schedule, track attendance, and log clinical visits to prevent care lapses
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchData}
            icon={<RefreshCw size={16} />}
          >
            Refresh
          </Button>
          <Button
            variant="primary"
            size="md"
            icon={<PlusCircle size={18} />}
            onClick={() => setIsScheduleModalOpen(true)}
          >
            Schedule Appointment
          </Button>
        </div>
      </div>

      {/* KPI Highlights Bar */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
        }}
      >
        <Card>
          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', fontWeight: 600 }}>
            SCHEDULED / UPCOMING
          </div>
          <div
            style={{
              fontSize: 'var(--font-size-3xl)',
              fontWeight: 700,
              color: 'var(--primary-700)',
              marginTop: '4px',
            }}
          >
            {scheduledCount}
          </div>
        </Card>

        <Card>
          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', fontWeight: 600 }}>
            ATTENDED & COMPLETED
          </div>
          <div
            style={{
              fontSize: 'var(--font-size-3xl)',
              fontWeight: 700,
              color: 'var(--status-success)',
              marginTop: '4px',
            }}
          >
            {completedCount}
          </div>
        </Card>

        <Card>
          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', fontWeight: 600 }}>
            MISSED APPOINTMENTS
          </div>
          <div
            style={{
              fontSize: 'var(--font-size-3xl)',
              fontWeight: 700,
              color: missedCount > 0 ? 'var(--status-danger)' : 'var(--text-secondary)',
              marginTop: '4px',
            }}
          >
            {missedCount}
          </div>
        </Card>
      </div>

      {/* Filters Bar */}
      <Card>
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '16px',
          }}
        >
          {/* Search Box */}
          <div style={{ position: 'relative', flex: '1 1 300px', maxWidth: '400px' }}>
            <Search
              size={18}
              style={{
                position: 'absolute',
                left: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--text-muted)',
              }}
            />
            <input
              type="text"
              placeholder="Search by client, ref, type, or location..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              style={{
                width: '100%',
                padding: '9px 12px 9px 38px',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                fontSize: 'var(--font-size-sm)',
                outline: 'none',
              }}
            />
          </div>

          {/* Status Filter Tabs */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <Filter size={16} color="var(--text-muted)" style={{ marginRight: '4px' }} />
            {(['all', 'scheduled', 'completed', 'missed', 'cancelled'] as const).map((st) => (
              <button
                key={st}
                onClick={() => {
                  setStatusFilter(st);
                  setCurrentPage(1);
                }}
                style={{
                  padding: '6px 12px',
                  borderRadius: 'var(--radius-full)',
                  fontSize: 'var(--font-size-xs)',
                  fontWeight: 600,
                  border:
                    statusFilter === st
                      ? '1px solid var(--primary-700)'
                      : '1px solid var(--border-color)',
                  background: statusFilter === st ? 'var(--primary-700)' : 'var(--bg-surface)',
                  color: statusFilter === st ? 'var(--text-inverse)' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  textTransform: 'capitalize',
                  transition: 'all 0.15s ease',
                }}
              >
                {st}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Appointments Table */}
      <Card>
        {loading ? (
          <LoadingSpinner message="Loading appointment records..." />
        ) : error ? (
          <div style={{ padding: '24px', textAlign: 'center', color: 'var(--status-danger)' }}>
            <p>{error}</p>
            <Button variant="outline" size="sm" onClick={fetchData} style={{ marginTop: '12px' }}>
              Retry
            </Button>
          </div>
        ) : paginatedAppointments.length === 0 ? (
          <EmptyState
            icon={<Calendar size={36} />}
            title="No appointments found"
            description={
              searchQuery || statusFilter !== 'all'
                ? 'Try adjusting your search criteria or resetting the status filter.'
                : 'No appointments scheduled. Create a new appointment to get started.'
            }
            action={
              <Button
                variant="primary"
                size="sm"
                icon={<PlusCircle size={16} />}
                onClick={() => setIsScheduleModalOpen(true)}
              >
                Schedule Appointment
              </Button>
            }
          />
        ) : (
          <div>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr
                    style={{
                      borderBottom: '1px solid var(--border-color)',
                      background: 'var(--bg-subtle)',
                      color: 'var(--text-secondary)',
                      fontSize: 'var(--font-size-xs)',
                      textTransform: 'uppercase',
                    }}
                  >
                    <th style={{ padding: '12px 16px', fontWeight: 600 }}>Client Profile</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600 }}>Appointment Type</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600 }}>Scheduled For</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600 }}>Location</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600 }}>Status</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600, textAlign: 'right' }}>
                      Staff Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedAppointments.map((appt) => {
                    const client = clientsMap[appt.client_id];
                    return (
                      <tr
                        key={appt.id}
                        style={{
                          borderBottom: '1px solid var(--border-light)',
                          transition: 'background-color 0.15s ease',
                        }}
                        onMouseEnter={(e) =>
                          (e.currentTarget.style.backgroundColor = 'var(--bg-subtle)')
                        }
                        onMouseLeave={(e) =>
                          (e.currentTarget.style.backgroundColor = 'transparent')
                        }
                      >
                        {/* Client Info */}
                        <td style={{ padding: '14px 16px' }}>
                          <Link
                            to={`/clients/${appt.client_id}`}
                            style={{
                              textDecoration: 'none',
                              color: 'inherit',
                              display: 'flex',
                              flexDirection: 'column',
                            }}
                          >
                            <span
                              style={{
                                fontWeight: 600,
                                fontSize: 'var(--font-size-sm)',
                                color: 'var(--primary-700)',
                              }}
                            >
                              {client ? client.preferred_name : 'Unknown Client'}
                            </span>
                            <span
                              style={{
                                fontSize: 'var(--font-size-xs)',
                                color: 'var(--text-muted)',
                                fontFamily: 'monospace',
                              }}
                            >
                              {client?.external_reference || appt.client_id.substring(0, 8)}
                            </span>
                          </Link>
                        </td>

                        {/* Type */}
                        <td style={{ padding: '14px 16px', fontSize: 'var(--font-size-sm)' }}>
                          <span style={{ textTransform: 'capitalize', fontWeight: 500 }}>
                            {appt.appointment_type.replace(/_/g, ' ')}
                          </span>
                        </td>

                        {/* Scheduled At */}
                        <td style={{ padding: '14px 16px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <Clock size={14} color="var(--primary-600)" />
                            <span style={{ fontWeight: 600, fontSize: 'var(--font-size-xs)' }}>
                              {new Date(appt.scheduled_at).toLocaleString(undefined, {
                                weekday: 'short',
                                month: 'short',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </span>
                          </div>
                        </td>

                        {/* Location */}
                        <td
                          style={{
                            padding: '14px 16px',
                            fontSize: 'var(--font-size-xs)',
                            color: 'var(--text-secondary)',
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <MapPin size={13} color="var(--text-muted)" />
                            <span>{appt.location_label || 'Central Wellness Center'}</span>
                          </div>
                        </td>

                        {/* Status */}
                        <td style={{ padding: '14px 16px' }}>
                          <Badge
                            variant={
                              appt.status === 'completed'
                                ? 'success'
                                : appt.status === 'scheduled'
                                ? 'info'
                                : appt.status === 'missed'
                                ? 'danger'
                                : 'neutral'
                            }
                            size="sm"
                          >
                            {appt.status.toUpperCase()}
                          </Badge>
                        </td>

                        {/* Actions */}
                        <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                          {appt.status === 'scheduled' ? (
                            <div style={{ display: 'inline-flex', gap: '6px' }}>
                              <Button
                                size="sm"
                                variant="outline"
                                icon={<CheckCircle2 size={13} />}
                                onClick={() => handleUpdateStatus(appt.id, 'completed')}
                                title="Mark Attended"
                              >
                                Attended
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                icon={<XCircle size={13} />}
                                onClick={() => handleUpdateStatus(appt.id, 'missed')}
                                title="Mark Missed"
                              >
                                Missed
                              </Button>
                            </div>
                          ) : (
                            <span
                              style={{
                                fontSize: 'var(--font-size-xs)',
                                color: 'var(--text-muted)',
                              }}
                            >
                              Logged
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'center' }}>
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={setCurrentPage}
                />
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Schedule Modal */}
      <ScheduleAppointmentModal
        isOpen={isScheduleModalOpen}
        onClose={() => setIsScheduleModalOpen(false)}
        onSuccess={() => fetchData()}
      />
    </div>
  );
};
