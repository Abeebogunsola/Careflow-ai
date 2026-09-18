import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Calendar,
  MessageSquare,
  ClipboardList,
  AlertTriangle,
  User,
  Shield,
  Clock,
  Phone,
  Globe,
  Settings,
  PlusCircle,
  CheckCircle2,
  XCircle,
  RefreshCw,
  AlertCircle,
  Send,
} from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { ScheduleAppointmentModal } from '../components/modals/ScheduleAppointmentModal';
import { RecordInteractionModal } from '../components/modals/RecordInteractionModal';
import { CreateFollowUpModal } from '../components/modals/CreateFollowUpModal';
import { CreateEscalationModal } from '../components/modals/CreateEscalationModal';
import {
  getClient,
  updateClient,
  getCommunicationPreference,
  setCommunicationPreference,
  listAppointments,
  updateAppointment,
  listInteractions,
  listFollowUps,
  updateFollowUp,
  listEscalations,
  updateEscalation,
} from '../api';
import {
  Client,
  CommunicationPreference,
  CommunicationChannel,
  Appointment,
  Interaction,
  FollowUpTask,
  Escalation,
  EnrollmentStatus,
} from '../types';

type TabKey = 'overview' | 'appointments' | 'interactions' | 'followups' | 'escalations';

export const ClientDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Client Data
  const [client, setClient] = useState<Client | null>(null);
  const [pref, setPref] = useState<CommunicationPreference | null>(null);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [followups, setFollowups] = useState<FollowUpTask[]>([]);
  const [escalations, setEscalations] = useState<Escalation[]>([]);

  // Navigation & UI States
  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [updatingPref, setUpdatingPref] = useState(false);
  const [statusChangeMsg, setStatusChangeMsg] = useState<string | null>(null);

  // Modals
  const [isApptModalOpen, setIsApptModalOpen] = useState(false);
  const [isInteractionModalOpen, setIsInteractionModalOpen] = useState(false);
  const [isFollowUpModalOpen, setIsFollowUpModalOpen] = useState(false);
  const [isEscalationModalOpen, setIsEscalationModalOpen] = useState(false);

  const fetchClientDetails = useCallback(async () => {
    if (!id) return;
    try {
      setLoading(true);
      setError(null);

      const [cData, pData, aData, iData, fData, eData] = await Promise.all([
        getClient(id),
        getCommunicationPreference(id),
        listAppointments({ client_id: id, page_size: 50 }),
        listInteractions({ client_id: id, page_size: 50 }),
        listFollowUps({ client_id: id, page_size: 50 }),
        listEscalations({ client_id: id, page_size: 50 }),
      ]);

      setClient(cData);
      setPref(pData);
      setAppointments(aData.data);
      setInteractions(iData.data);
      setFollowups(fData.data);
      setEscalations(eData.data);
    } catch (err: unknown) {
      console.error('Failed to fetch client details:', err);
      setError('Could not find or load this client profile.');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchClientDetails();
  }, [fetchClientDetails]);

  // Handle updating enrollment status
  const handleUpdateStatus = async (newStatus: EnrollmentStatus) => {
    if (!client) return;
    try {
      const updated = await updateClient(client.id, {
        status: newStatus,
        enrollment_status: newStatus,
      });
      setClient(updated);
      setStatusChangeMsg(`Status updated to ${newStatus}`);
      setTimeout(() => setStatusChangeMsg(null), 3000);
    } catch (err) {
      console.error('Failed to update client status:', err);
      alert('Failed to update status. Please check backend.');
    }
  };

  // Handle updating communication preference
  const handleSavePref = async (newChannel: CommunicationChannel, enabled: boolean) => {
    if (!client) return;
    try {
      setUpdatingPref(true);
      const updated = await setCommunicationPreference(client.id, {
        channel: newChannel,
        preferred_channel: newChannel,
        is_enabled: enabled,
      });
      setPref(updated);
    } catch (err) {
      console.error('Failed to update preference:', err);
      alert('Failed to save communication preference.');
    } finally {
      setUpdatingPref(false);
    }
  };

  // Handle appointment status change
  const handleAppointmentStatus = async (apptId: string, status: 'completed' | 'missed' | 'cancelled') => {
    try {
      const updated = await updateAppointment(apptId, { status });
      setAppointments((prev) => prev.map((a) => (a.id === apptId ? updated : a)));
    } catch (err) {
      console.error('Failed to update appointment:', err);
      alert('Could not update appointment status.');
    }
  };

  // Handle follow up status change
  const handleFollowUpStatus = async (taskId: string, status: 'completed' | 'cancelled') => {
    try {
      const updated = await updateFollowUp(taskId, {
        status,
        completed_at: status === 'completed' ? new Date().toISOString() : null,
      });
      setFollowups((prev) => prev.map((f) => (f.id === taskId ? updated : f)));
    } catch (err) {
      console.error('Failed to update follow-up task:', err);
      alert('Could not update follow-up task status.');
    }
  };

  // Handle escalation status change
  const handleEscalationStatus = async (escId: string, status: 'in_review' | 'resolved') => {
    try {
      const updated = await updateEscalation(escId, {
        status,
        resolved_at: status === 'resolved' ? new Date().toISOString() : null,
      });
      setEscalations((prev) => prev.map((e) => (e.id === escId ? updated : e)));
    } catch (err) {
      console.error('Failed to update escalation:', err);
      alert('Could not update escalation status.');
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading client care record..." />;
  }

  if (error || !client) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <AlertCircle size={48} color="var(--status-danger)" style={{ marginBottom: '16px' }} />
        <h2 style={{ marginBottom: '8px' }}>Client Not Found</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>{error}</p>
        <Link to="/clients">
          <Button variant="outline" icon={<ArrowLeft size={16} />}>
            Return to Client Directory
          </Button>
        </Link>
      </div>
    );
  }

  const clientStatus = client.status || client.enrollment_status || 'active';

  // Metrics
  const completedAppts = appointments.filter((a) => a.status === 'completed').length;
  const missedAppts = appointments.filter((a) => a.status === 'missed').length;
  const scheduledAppts = appointments.filter((a) => a.status === 'scheduled').length;
  const openFollowups = followups.filter((f) => f.status === 'pending' || f.status === 'in_progress').length;
  const activeEscalations = escalations.filter((e) => e.status === 'open' || e.status === 'in_review').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Breadcrumb & Actions */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '16px',
        }}
      >
        <Link
          to="/clients"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            color: 'var(--primary-700)',
            textDecoration: 'none',
            fontSize: 'var(--font-size-sm)',
            fontWeight: 600,
          }}
        >
          <ArrowLeft size={16} /> Back to Directory
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <Button
            variant="outline"
            size="sm"
            icon={<RefreshCw size={15} />}
            onClick={fetchClientDetails}
          >
            Refresh
          </Button>
          <Button
            variant="outline"
            size="sm"
            icon={<Calendar size={15} />}
            onClick={() => setIsApptModalOpen(true)}
          >
            Schedule Appt
          </Button>
          <Button
            variant="outline"
            size="sm"
            icon={<Send size={15} />}
            onClick={() => setIsInteractionModalOpen(true)}
          >
            Log Interaction
          </Button>
          <Button
            variant="outline"
            size="sm"
            icon={<ClipboardList size={15} />}
            onClick={() => setIsFollowUpModalOpen(true)}
          >
            Add Follow-Up
          </Button>
          <Button
            variant="danger"
            size="sm"
            icon={<AlertTriangle size={15} />}
            onClick={() => setIsEscalationModalOpen(true)}
          >
            Raise Escalation
          </Button>
        </div>
      </div>

      {/* Client Identity Header Card */}
      <Card>
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '20px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div
              style={{
                width: '56px',
                height: '56px',
                borderRadius: 'var(--radius-lg)',
                background: 'var(--primary-100)',
                color: 'var(--primary-700)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.5rem',
                fontWeight: 700,
              }}
            >
              {client.preferred_name.charAt(0).toUpperCase()}
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, margin: 0 }}>
                  {client.preferred_name}
                </h1>
                <Badge
                  variant={
                    clientStatus === 'active'
                      ? 'success'
                      : clientStatus === 'inactive'
                      ? 'warning'
                      : 'neutral'
                  }
                  size="md"
                >
                  {clientStatus.toUpperCase()}
                </Badge>
                {activeEscalations > 0 && (
                  <Badge variant="danger" size="md">
                    {activeEscalations} ACTIVE ESCALATION{activeEscalations > 1 ? 'S' : ''}
                  </Badge>
                )}
              </div>

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  marginTop: '6px',
                  fontSize: 'var(--font-size-xs)',
                  color: 'var(--text-secondary)',
                  flexWrap: 'wrap',
                }}
              >
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  <Shield size={14} color="var(--primary-600)" />
                  Reference:{' '}
                  <code style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                    {client.external_reference || 'SYNTH-PAT-XXXX'}
                  </code>
                </span>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  <Globe size={14} color="var(--text-muted)" />
                  Language: <strong>{(client.preferred_language || 'en').toUpperCase()}</strong>
                </span>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  <Clock size={14} color="var(--text-muted)" />
                  Enrolled:{' '}
                  {client.created_at
                    ? new Date(client.created_at).toLocaleDateString()
                    : 'Recent'}
                </span>
              </div>
            </div>
          </div>

          {/* Quick Metrics Bar */}
          <div
            style={{
              display: 'flex',
              gap: '16px',
              padding: '10px 16px',
              background: 'var(--bg-subtle)',
              borderRadius: 'var(--radius-md)',
              fontSize: 'var(--font-size-xs)',
            }}
          >
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontWeight: 700, fontSize: 'var(--font-size-base)', color: 'var(--primary-700)' }}>
                {scheduledAppts}
              </div>
              <div style={{ color: 'var(--text-muted)' }}>Upcoming</div>
            </div>
            <div style={{ width: '1px', background: 'var(--border-color)' }} />
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontWeight: 700, fontSize: 'var(--font-size-base)', color: 'var(--status-success)' }}>
                {completedAppts}
              </div>
              <div style={{ color: 'var(--text-muted)' }}>Completed</div>
            </div>
            <div style={{ width: '1px', background: 'var(--border-color)' }} />
            <div style={{ textAlign: 'center' }}>
              <div
                style={{
                  fontWeight: 700,
                  fontSize: 'var(--font-size-base)',
                  color: missedAppts > 0 ? 'var(--status-danger)' : 'var(--text-secondary)',
                }}
              >
                {missedAppts}
              </div>
              <div style={{ color: 'var(--text-muted)' }}>Missed</div>
            </div>
            <div style={{ width: '1px', background: 'var(--border-color)' }} />
            <div style={{ textAlign: 'center' }}>
              <div
                style={{
                  fontWeight: 700,
                  fontSize: 'var(--font-size-base)',
                  color: openFollowups > 0 ? 'var(--status-warning)' : 'var(--text-secondary)',
                }}
              >
                {openFollowups}
              </div>
              <div style={{ color: 'var(--text-muted)' }}>Tasks</div>
            </div>
          </div>
        </div>

        {statusChangeMsg && (
          <div
            style={{
              marginTop: '12px',
              padding: '8px 12px',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--status-success-bg)',
              color: 'var(--status-success)',
              fontSize: 'var(--font-size-xs)',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <CheckCircle2 size={14} /> {statusChangeMsg}
          </div>
        )}
      </Card>

      {/* Tabs Navigation Bar */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          borderBottom: '1px solid var(--border-color)',
          paddingBottom: '2px',
          overflowX: 'auto',
        }}
      >
        {[
          { key: 'overview', label: 'Care Overview & Preferences', icon: <User size={16} /> },
          {
            key: 'appointments',
            label: `Appointments (${appointments.length})`,
            icon: <Calendar size={16} />,
          },
          {
            key: 'interactions',
            label: `Interactions (${interactions.length})`,
            icon: <MessageSquare size={16} />,
          },
          {
            key: 'followups',
            label: `Follow-Ups (${openFollowups} Open)`,
            icon: <ClipboardList size={16} />,
          },
          {
            key: 'escalations',
            label: `Escalations (${escalations.length})`,
            icon: <AlertTriangle size={16} />,
          },
        ].map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key as TabKey)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 18px',
              border: 'none',
              borderBottom:
                activeTab === t.key ? '3px solid var(--primary-700)' : '3px solid transparent',
              background: 'transparent',
              color: activeTab === t.key ? 'var(--primary-700)' : 'var(--text-secondary)',
              fontWeight: activeTab === t.key ? 700 : 500,
              fontSize: 'var(--font-size-sm)',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.15s ease',
            }}
          >
            {t.icon}
            {t.label}
          </button>
        ))}
      </div>

      {/* TAB 1: Care Overview & Preferences */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
          {/* Card 1: Communication Preferences */}
          <Card title="Communication Channels & Consent">
            <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginBottom: '16px' }}>
              Manage channel preference and consent flags. Automated reminders require opt-in consent.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label
                  style={{
                    display: 'block',
                    fontSize: 'var(--font-size-xs)',
                    fontWeight: 600,
                    marginBottom: '6px',
                    color: 'var(--text-secondary)',
                  }}
                >
                  Preferred Channel
                </label>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {(['whatsapp', 'sms', 'web', 'email'] as const).map((ch) => {
                    const isSelected = (pref?.channel || pref?.preferred_channel || 'whatsapp') === ch;
                    return (
                      <button
                        key={ch}
                        disabled={updatingPref}
                        onClick={() => handleSavePref(ch, pref?.is_enabled ?? true)}
                        style={{
                          padding: '8px 14px',
                          borderRadius: 'var(--radius-md)',
                          fontSize: 'var(--font-size-xs)',
                          fontWeight: 600,
                          border: isSelected ? '2px solid var(--primary-700)' : '1px solid var(--border-color)',
                          background: isSelected ? 'var(--primary-50)' : 'var(--bg-surface)',
                          color: isSelected ? 'var(--primary-800)' : 'var(--text-secondary)',
                          cursor: 'pointer',
                          textTransform: 'uppercase',
                        }}
                      >
                        {ch}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Messaging Toggle */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px 16px',
                  background: 'var(--bg-subtle)',
                  borderRadius: 'var(--radius-md)',
                }}
              >
                <div>
                  <div style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600 }}>
                    Automated Outreach Enabled
                  </div>
                  <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                    Client has confirmed consent to receive appointment notifications
                  </div>
                </div>
                <Button
                  size="sm"
                  variant={pref?.is_enabled ?? true ? 'primary' : 'outline'}
                  disabled={updatingPref}
                  onClick={() =>
                    handleSavePref(
                      (pref?.channel as CommunicationChannel) || 'whatsapp',
                      !(pref?.is_enabled ?? true)
                    )
                  }
                >
                  {pref?.is_enabled ?? true ? 'Enabled' : 'Disabled'}
                </Button>
              </div>

              <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                Last preference update:{' '}
                {pref?.updated_at ? new Date(pref.updated_at).toLocaleString() : 'Not yet modified'}
              </div>
            </div>
          </Card>

          {/* Card 2: Enrollment & Status Controls */}
          <Card title="Retention Status & Profile Controls">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label
                  style={{
                    display: 'block',
                    fontSize: 'var(--font-size-xs)',
                    fontWeight: 600,
                    marginBottom: '6px',
                    color: 'var(--text-secondary)',
                  }}
                >
                  Current Enrollment Status
                </label>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {(['active', 'inactive', 'completed', 'withdrawn'] as const).map((st) => (
                    <button
                      key={st}
                      onClick={() => handleUpdateStatus(st)}
                      style={{
                        padding: '6px 12px',
                        borderRadius: 'var(--radius-md)',
                        fontSize: 'var(--font-size-xs)',
                        fontWeight: 600,
                        border:
                          clientStatus === st ? '2px solid var(--primary-700)' : '1px solid var(--border-color)',
                        background: clientStatus === st ? 'var(--primary-50)' : 'var(--bg-surface)',
                        color: clientStatus === st ? 'var(--primary-800)' : 'var(--text-secondary)',
                        cursor: 'pointer',
                        textTransform: 'capitalize',
                      }}
                    >
                      {st}
                    </button>
                  ))}
                </div>
              </div>

              <div
                style={{
                  padding: '12px',
                  background: 'var(--bg-subtle)',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                  fontSize: 'var(--font-size-xs)',
                }}
              >
                <div>
                  <strong>Internal Identifier (UUID):</strong>{' '}
                  <span style={{ fontFamily: 'monospace', color: 'var(--text-secondary)' }}>
                    {client.id}
                  </span>
                </div>
                <div>
                  <strong>Protected Pseudonym:</strong>{' '}
                  <span style={{ fontFamily: 'monospace', color: 'var(--text-secondary)' }}>
                    {client.external_reference || 'SYNTH-PAT-XXXX'}
                  </span>
                </div>
                <div>
                  <strong>Account Active Flag:</strong>{' '}
                  <span>{client.is_active ? 'True' : 'False'}</span>
                </div>
                <div>
                  <strong>Created At:</strong>{' '}
                  <span>{client.created_at ? new Date(client.created_at).toLocaleString() : '—'}</span>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* TAB 2: Appointments */}
      {activeTab === 'appointments' && (
        <Card
          title="Appointments & Refill Schedule"
          action={
            <Button
              variant="primary"
              size="sm"
              icon={<PlusCircle size={15} />}
              onClick={() => setIsApptModalOpen(true)}
            >
              Schedule Appointment
            </Button>
          }
        >
          {appointments.length === 0 ? (
            <EmptyState
              icon={<Calendar size={36} />}
              title="No Appointments Recorded"
              description="This client does not have any scheduled or past appointments."
              action={
                <Button
                  variant="primary"
                  size="sm"
                  icon={<PlusCircle size={15} />}
                  onClick={() => setIsApptModalOpen(true)}
                >
                  Schedule First Appointment
                </Button>
              }
            />
          ) : (
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
                    <th style={{ padding: '10px 14px' }}>Scheduled Date & Time</th>
                    <th style={{ padding: '10px 14px' }}>Type</th>
                    <th style={{ padding: '10px 14px' }}>Location</th>
                    <th style={{ padding: '10px 14px' }}>Status</th>
                    <th style={{ padding: '10px 14px', textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {appointments.map((appt) => (
                    <tr
                      key={appt.id}
                      style={{ borderBottom: '1px solid var(--border-light)' }}
                    >
                      <td style={{ padding: '12px 14px', fontWeight: 600, fontSize: 'var(--font-size-sm)' }}>
                        {new Date(appt.scheduled_at).toLocaleString(undefined, {
                          weekday: 'short',
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </td>
                      <td style={{ padding: '12px 14px', fontSize: 'var(--font-size-sm)', textTransform: 'capitalize' }}>
                        {appt.appointment_type.replace(/_/g, ' ')}
                      </td>
                      <td style={{ padding: '12px 14px', fontSize: 'var(--font-size-xs)', color: 'var(--text-secondary)' }}>
                        {appt.location_label || 'Main Clinic'}
                      </td>
                      <td style={{ padding: '12px 14px' }}>
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
                          {appt.status}
                        </Badge>
                      </td>
                      <td style={{ padding: '12px 14px', textAlign: 'right' }}>
                        {appt.status === 'scheduled' && (
                          <div style={{ display: 'inline-flex', gap: '6px' }}>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleAppointmentStatus(appt.id, 'completed')}
                            >
                              Attended
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleAppointmentStatus(appt.id, 'missed')}
                            >
                              Missed
                            </Button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {/* TAB 3: Interactions */}
      {activeTab === 'interactions' && (
        <Card
          title="Communication Ledger & Message Audit"
          action={
            <Button
              variant="primary"
              size="sm"
              icon={<Send size={15} />}
              onClick={() => setIsInteractionModalOpen(true)}
            >
              Record Interaction
            </Button>
          }
        >
          {interactions.length === 0 ? (
            <EmptyState
              icon={<MessageSquare size={36} />}
              title="No Interactions Logged"
              description="No incoming or outgoing messages have been recorded for this client."
              action={
                <Button
                  variant="primary"
                  size="sm"
                  icon={<Send size={15} />}
                  onClick={() => setIsInteractionModalOpen(true)}
                >
                  Record First Interaction
                </Button>
              }
            />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {interactions.map((msg) => (
                <div
                  key={msg.id}
                  style={{
                    padding: '14px',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-color)',
                    background: msg.direction === 'outgoing' ? 'var(--primary-50)' : 'var(--bg-surface)',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '8px',
                      flexWrap: 'wrap',
                      gap: '8px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Badge
                        variant={msg.direction === 'incoming' ? 'info' : 'success'}
                        size="sm"
                      >
                        {msg.direction.toUpperCase()}
                      </Badge>
                      <Badge variant="neutral" size="sm">
                        {msg.channel.toUpperCase()}
                      </Badge>
                      {msg.intent_category && (
                        <Badge variant="warning" size="sm">
                          {msg.intent_category.replace(/_/g, ' ')}
                        </Badge>
                      )}
                    </div>
                    <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                      {new Date(msg.created_at).toLocaleString()}
                    </span>
                  </div>

                  <p
                    style={{
                      margin: 0,
                      fontSize: 'var(--font-size-sm)',
                      color: 'var(--text-main)',
                      lineHeight: 1.5,
                    }}
                  >
                    {msg.content || 'No message content stored.'}
                  </p>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}

      {/* TAB 4: Follow-Ups */}
      {activeTab === 'followups' && (
        <Card
          title="Care Navigation Outreach Tasks"
          action={
            <Button
              variant="primary"
              size="sm"
              icon={<PlusCircle size={15} />}
              onClick={() => setIsFollowUpModalOpen(true)}
            >
              Add Follow-Up
            </Button>
          }
        >
          {followups.length === 0 ? (
            <EmptyState
              icon={<ClipboardList size={36} />}
              title="No Follow-Up Tasks"
              description="All outreach activities for this client are currently clear."
              action={
                <Button
                  variant="primary"
                  size="sm"
                  icon={<PlusCircle size={15} />}
                  onClick={() => setIsFollowUpModalOpen(true)}
                >
                  Create Follow-Up Task
                </Button>
              }
            />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {followups.map((task) => (
                <div
                  key={task.id}
                  style={{
                    padding: '14px',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-color)',
                    background: task.status === 'completed' ? 'var(--bg-subtle)' : 'var(--bg-surface)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '16px',
                    flexWrap: 'wrap',
                  }}
                >
                  <div style={{ flex: '1 1 300px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                      <Badge
                        variant={
                          task.priority === 'urgent'
                            ? 'danger'
                            : task.priority === 'high'
                            ? 'warning'
                            : 'neutral'
                        }
                        size="sm"
                      >
                        {task.priority.toUpperCase()}
                      </Badge>
                      <Badge
                        variant={task.status === 'completed' ? 'success' : 'info'}
                        size="sm"
                      >
                        {task.status.toUpperCase()}
                      </Badge>
                      {task.due_at && (
                        <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                          Due: {new Date(task.due_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, color: 'var(--text-main)' }}>
                      {task.reason}
                    </div>
                  </div>

                  <div>
                    {task.status !== 'completed' ? (
                      <Button
                        size="sm"
                        variant="outline"
                        icon={<CheckCircle2 size={14} />}
                        onClick={() => handleFollowUpStatus(task.id, 'completed')}
                      >
                        Mark Completed
                      </Button>
                    ) : (
                      <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--status-success)', fontWeight: 600 }}>
                        Completed {task.completed_at ? new Date(task.completed_at).toLocaleDateString() : ''}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}

      {/* TAB 5: Escalations */}
      {activeTab === 'escalations' && (
        <Card
          title="Clinical & Support Human Review Queue"
          action={
            <Button
              variant="danger"
              size="sm"
              icon={<AlertTriangle size={15} />}
              onClick={() => setIsEscalationModalOpen(true)}
            >
              Raise Escalation
            </Button>
          }
        >
          <div
            style={{
              padding: '12px 16px',
              background: 'var(--status-warning-bg)',
              border: '1px solid var(--status-warning-border)',
              borderRadius: 'var(--radius-md)',
              marginBottom: '16px',
              fontSize: 'var(--font-size-xs)',
              color: 'var(--text-main)',
            }}
          >
            <strong>Human Clinical Oversight Mandatory:</strong> AI provides support routing and intake
            summaries only. All diagnostic or clinical judgment requires review by qualified healthcare
            practitioners.
          </div>

          {escalations.length === 0 ? (
            <EmptyState
              icon={<CheckCircle2 size={36} />}
              title="No Escalations Active"
              description="No clinical or support escalations are flagged for this client."
            />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {escalations.map((esc) => (
                <div
                  key={esc.id}
                  style={{
                    padding: '16px',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-color)',
                    background:
                      esc.status === 'resolved'
                        ? 'var(--bg-subtle)'
                        : 'var(--status-danger-bg)',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '8px',
                      flexWrap: 'wrap',
                      gap: '8px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Badge variant="danger" size="sm">
                        {esc.priority.toUpperCase()} PRIORITY
                      </Badge>
                      <Badge variant="neutral" size="sm">
                        {esc.category.replace(/_/g, ' ').toUpperCase()}
                      </Badge>
                      <Badge
                        variant={esc.status === 'resolved' ? 'success' : 'warning'}
                        size="sm"
                      >
                        {esc.status.toUpperCase()}
                      </Badge>
                    </div>

                    <div style={{ display: 'flex', gap: '6px' }}>
                      {esc.status === 'open' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEscalationStatus(esc.id, 'in_review')}
                        >
                          Mark In-Review
                        </Button>
                      )}
                      {esc.status !== 'resolved' && (
                        <Button
                          size="sm"
                          variant="primary"
                          onClick={() => handleEscalationStatus(esc.id, 'resolved')}
                        >
                          Resolve
                        </Button>
                      )}
                    </div>
                  </div>

                  <p
                    style={{
                      margin: '6px 0 0',
                      fontSize: 'var(--font-size-sm)',
                      fontWeight: 600,
                      color: 'var(--text-main)',
                    }}
                  >
                    {esc.reason}
                  </p>
                  <div style={{ marginTop: '8px', fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                    Reported on {new Date(esc.created_at).toLocaleString()}
                    {esc.resolved_at && ` • Resolved on ${new Date(esc.resolved_at).toLocaleString()}`}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}

      {/* Modals with clientId pre-populated */}
      <ScheduleAppointmentModal
        isOpen={isApptModalOpen}
        onClose={() => setIsApptModalOpen(false)}
        onSuccess={() => fetchClientDetails()}
        initialClientId={client.id}
      />

      <RecordInteractionModal
        isOpen={isInteractionModalOpen}
        onClose={() => setIsInteractionModalOpen(false)}
        onSuccess={() => fetchClientDetails()}
        initialClientId={client.id}
      />

      <CreateFollowUpModal
        isOpen={isFollowUpModalOpen}
        onClose={() => setIsFollowUpModalOpen(false)}
        onSuccess={() => fetchClientDetails()}
        initialClientId={client.id}
      />

      <CreateEscalationModal
        isOpen={isEscalationModalOpen}
        onClose={() => setIsEscalationModalOpen(false)}
        onSuccess={() => fetchClientDetails()}
        initialClientId={client.id}
      />
    </div>
  );
};
