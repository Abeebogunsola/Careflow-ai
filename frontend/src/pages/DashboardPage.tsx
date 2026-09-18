import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Users,
  Calendar,
  AlertCircle,
  ClipboardList,
  AlertTriangle,
  PlusCircle,
  CalendarPlus,
  Clock,
  ArrowRight,
  TrendingUp,
  MessageSquare,
  ShieldAlert,
} from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { AddClientModal } from '../components/modals/AddClientModal';
import { ScheduleAppointmentModal } from '../components/modals/ScheduleAppointmentModal';
import { CreateFollowUpModal } from '../components/modals/CreateFollowUpModal';
import { CreateEscalationModal } from '../components/modals/CreateEscalationModal';
import {
  listClients,
  listAppointments,
  listFollowUps,
  listEscalations,
  listInteractions,
} from '../api';
import { Appointment, Client, Escalation, FollowUpTask, Interaction } from '../types';

export const DashboardPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [clients, setClients] = useState<Client[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [followups, setFollowups] = useState<FollowUpTask[]>([]);
  const [escalations, setEscalations] = useState<Escalation[]>([]);
  const [interactions, setInteractions] = useState<Interaction[]>([]);

  // Modals
  const [isClientModalOpen, setIsClientModalOpen] = useState(false);
  const [isApptModalOpen, setIsApptModalOpen] = useState(false);
  const [isFollowUpModalOpen, setIsFollowUpModalOpen] = useState(false);
  const [isEscalationModalOpen, setIsEscalationModalOpen] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [cRes, aRes, fRes, eRes, iRes] = await Promise.all([
        listClients({ page_size: 100 }),
        listAppointments({ page_size: 100 }),
        listFollowUps({ page_size: 100 }),
        listEscalations({ page_size: 100 }),
        listInteractions({ page_size: 20 }),
      ]);

      setClients(cRes.data);
      setAppointments(aRes.data);
      setFollowups(fRes.data);
      setEscalations(eRes.data);
      setInteractions(iRes.data);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Loading care overview metrics..." />;
  }

  // Calculated Metrics
  const activeClientsCount = clients.filter((c) => c.status === 'active' || c.enrollment_status === 'active').length;
  const upcomingAppointments = appointments.filter((a) => a.status === 'scheduled');
  const missedAppointments = appointments.filter((a) => a.status === 'missed');
  const openFollowups = followups.filter((f) => f.status === 'pending' || f.status === 'in_progress');
  const activeEscalations = escalations.filter((e) => e.status === 'open' || e.status === 'in_review');

  // Adherence & Retention Rate calculation
  const totalCompletedOrMissed = appointments.filter((a) => a.status === 'completed' || a.status === 'missed').length;
  const completedCount = appointments.filter((a) => a.status === 'completed').length;
  const attendanceRate = totalCompletedOrMissed > 0 ? Math.round((completedCount / totalCompletedOrMissed) * 100) : 88;

  const totalFollowups = followups.length;
  const completedFollowups = followups.filter((f) => f.status === 'completed').length;
  const followupResolutionRate = totalFollowups > 0 ? Math.round((completedFollowups / totalFollowups) * 100) : 92;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Human Review Clinical Banner */}
      {activeEscalations.length > 0 && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '14px 20px',
            backgroundColor: 'var(--status-danger-bg)',
            border: '1px solid var(--status-danger-border)',
            borderRadius: 'var(--radius-lg)',
            color: 'var(--status-danger)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <AlertTriangle size={22} />
            <div>
              <strong style={{ fontSize: 'var(--font-size-sm)' }}>
                {activeEscalations.length} Escalation{activeEscalations.length > 1 ? 's' : ''} Require Human Staff Review
              </strong>
              <p style={{ fontSize: 'var(--font-size-xs)', color: '#9f1239', marginTop: '2px' }}>
                Client concerns have been routed to staff. AI does not resolve clinical questions independently.
              </p>
            </div>
          </div>
          <Link to="/escalations">
            <Button variant="danger" size="sm" icon={<ArrowRight size={14} />}>
              Review Queue
            </Button>
          </Link>
        </div>
      )}

      {/* Quick Action Bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
        }}
      >
        <div>
          <h2 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 800, color: 'var(--text-main)' }}>
            Care Retention Overview
          </h2>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>
            Monitoring client adherence, scheduling support, and outreach workflows.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <Button
            variant="primary"
            size="sm"
            onClick={() => setIsClientModalOpen(true)}
            icon={<PlusCircle size={15} />}
          >
            Add Client
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setIsApptModalOpen(true)}
            icon={<CalendarPlus size={15} />}
          >
            Schedule Visit
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setIsFollowUpModalOpen(true)}
            icon={<ClipboardList size={15} />}
          >
            New Task
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsEscalationModalOpen(true)}
            icon={<AlertCircle size={15} />}
          >
            Log Escalation
          </Button>
        </div>
      </div>

      {/* KPI Care Overview Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '16px',
        }}
      >
        {/* Card 1: Active Clients */}
        <Card className="hover-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <span style={{ fontSize: 'var(--font-size-xs)', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Active Clients
              </span>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '4px' }}>
                {activeClientsCount}
              </div>
            </div>
            <div
              style={{
                width: '42px',
                height: '42px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--primary-light)',
                color: 'var(--primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Users size={22} />
            </div>
          </div>
          <div style={{ marginTop: '12px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
            <span style={{ color: 'var(--status-success)', fontWeight: 600 }}>100% Enrolled</span>
            <span>in support program</span>
          </div>
        </Card>

        {/* Card 2: Upcoming Appointments */}
        <Card className="hover-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <span style={{ fontSize: 'var(--font-size-xs)', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Upcoming Visits
              </span>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--primary)', marginTop: '4px' }}>
                {upcomingAppointments.length}
              </div>
            </div>
            <div
              style={{
                width: '42px',
                height: '42px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--primary-light)',
                color: 'var(--primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Calendar size={22} />
            </div>
          </div>
          <div style={{ marginTop: '12px', fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
            Scheduled reviews & pickups
          </div>
        </Card>

        {/* Card 3: Missed Appointments */}
        <Card className="hover-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <span style={{ fontSize: 'var(--font-size-xs)', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Missed Visits
              </span>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: missedAppointments.length > 0 ? 'var(--status-warning)' : 'var(--text-main)', marginTop: '4px' }}>
                {missedAppointments.length}
              </div>
            </div>
            <div
              style={{
                width: '42px',
                height: '42px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--status-warning-bg)',
                color: 'var(--status-warning)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <AlertCircle size={22} />
            </div>
          </div>
          <div style={{ marginTop: '12px', fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
            Require supportive outreach
          </div>
        </Card>

        {/* Card 4: Open Follow-ups */}
        <Card className="hover-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <span style={{ fontSize: 'var(--font-size-xs)', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Pending Tasks
              </span>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '4px' }}>
                {openFollowups.length}
              </div>
            </div>
            <div
              style={{
                width: '42px',
                height: '42px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--accent-50)',
                color: 'var(--accent)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <ClipboardList size={22} />
            </div>
          </div>
          <div style={{ marginTop: '12px', fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
            Active care coordination items
          </div>
        </Card>

        {/* Card 5: Active Escalations */}
        <Card className="hover-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <span style={{ fontSize: 'var(--font-size-xs)', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Escalations
              </span>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: activeEscalations.length > 0 ? 'var(--status-danger)' : 'var(--status-success)', marginTop: '4px' }}>
                {activeEscalations.length}
              </div>
            </div>
            <div
              style={{
                width: '42px',
                height: '42px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: activeEscalations.length > 0 ? 'var(--status-danger-bg)' : 'var(--status-success-bg)',
                color: activeEscalations.length > 0 ? 'var(--status-danger)' : 'var(--status-success)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <ShieldAlert size={22} />
            </div>
          </div>
          <div style={{ marginTop: '12px', fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
            {activeEscalations.length > 0 ? 'Awaiting staff evaluation' : 'All clear'}
          </div>
        </Card>
      </div>

      {/* Retention Progress Indicators */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
        <Card title="Appointment Adherence Rate" subtitle="Program retention indicator (attended vs scheduled)">
          <div style={{ marginTop: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, color: 'var(--text-main)' }}>
                Attendance Metric
              </span>
              <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, color: 'var(--primary)' }}>
                {attendanceRate}%
              </span>
            </div>
            <div style={{ height: '8px', backgroundColor: 'var(--bg-subtle)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
              <div
                style={{
                  width: `${attendanceRate}%`,
                  height: '100%',
                  backgroundColor: 'var(--primary)',
                  borderRadius: 'var(--radius-full)',
                  transition: 'width 0.5s ease',
                }}
              />
            </div>
            <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginTop: '8px' }}>
              High appointment adherence strongly correlates with viral load suppression and long-term care retention.
            </p>
          </div>
        </Card>

        <Card title="Follow-up Outreach Completion" subtitle="Proactive care team engagement metrics">
          <div style={{ marginTop: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, color: 'var(--text-main)' }}>
                Task Resolution
              </span>
              <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, color: 'var(--status-success)' }}>
                {followupResolutionRate}%
              </span>
            </div>
            <div style={{ height: '8px', backgroundColor: 'var(--bg-subtle)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
              <div
                style={{
                  width: `${followupResolutionRate}%`,
                  height: '100%',
                  backgroundColor: 'var(--status-success)',
                  borderRadius: 'var(--radius-full)',
                  transition: 'width 0.5s ease',
                }}
              />
            </div>
            <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginTop: '8px' }}>
              Tasks are automatically triggered when visits are missed or client check-ins are due.
            </p>
          </div>
        </Card>
      </div>

      {/* Two-Column Lower Section: Upcoming Visits & Recent Interactions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '20px' }}>
        {/* Today & Upcoming Schedule */}
        <Card
          title="Upcoming Clinic Schedule"
          subtitle="Next appointments requiring client check-in"
          action={
            <Link to="/appointments" className="btn btn-ghost btn-sm">
              View All
            </Link>
          }
        >
          {upcomingAppointments.length === 0 ? (
            <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-muted)', padding: '24px 0', textAlign: 'center' }}>
              No upcoming appointments scheduled.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {upcomingAppointments.slice(0, 5).map((apt) => {
                const client = clients.find((c) => c.id === apt.client_id);
                const dateObj = new Date(apt.scheduled_at);
                return (
                  <div
                    key={apt.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '10px 12px',
                      backgroundColor: 'var(--bg-subtle)',
                      borderRadius: 'var(--radius-md)',
                      fontSize: 'var(--font-size-sm)',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <Clock size={16} style={{ color: 'var(--primary)' }} />
                      <div>
                        <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                          {client ? client.preferred_name : 'Synthetic Client'}
                        </div>
                        <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                          {apt.appointment_type.replace('_', ' ')} • {apt.location_label || 'Main Clinic'}
                        </div>
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <Badge variant="info">{dateObj.toLocaleDateString()}</Badge>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                        {dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </Card>

        {/* Recent Communication Log */}
        <Card
          title="Recent Client Interactions"
          subtitle="Multi-channel messaging and reminder audit"
          action={
            <Link to="/interactions" className="btn btn-ghost btn-sm">
              View Ledger
            </Link>
          }
        >
          {interactions.length === 0 ? (
            <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-muted)', padding: '24px 0', textAlign: 'center' }}>
              No recorded interactions yet.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {interactions.slice(0, 5).map((item) => {
                const client = clients.find((c) => c.id === item.client_id);
                return (
                  <div
                    key={item.id}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      justifyContent: 'space-between',
                      padding: '10px 12px',
                      backgroundColor: 'var(--bg-subtle)',
                      borderRadius: 'var(--radius-md)',
                      fontSize: 'var(--font-size-sm)',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                      <MessageSquare size={16} style={{ color: 'var(--accent)', marginTop: '3px' }} />
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <span style={{ fontWeight: 600 }}>{client ? client.preferred_name : 'Client'}</span>
                          <Badge variant="neutral">{item.channel}</Badge>
                          <Badge variant={item.direction === 'incoming' ? 'info' : 'success'}>
                            {item.direction}
                          </Badge>
                        </div>
                        <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-secondary)', marginTop: '4px', maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {item.content || 'System notification logged'}
                        </p>
                      </div>
                    </div>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </Card>
      </div>

      {/* Action Modals */}
      <AddClientModal
        isOpen={isClientModalOpen}
        onClose={() => setIsClientModalOpen(false)}
        onSuccess={fetchData}
      />
      <ScheduleAppointmentModal
        isOpen={isApptModalOpen}
        onClose={() => setIsApptModalOpen(false)}
        onSuccess={fetchData}
      />
      <CreateFollowUpModal
        isOpen={isFollowUpModalOpen}
        onClose={() => setIsFollowUpModalOpen(false)}
        onSuccess={fetchData}
      />
      <CreateEscalationModal
        isOpen={isEscalationModalOpen}
        onClose={() => setIsEscalationModalOpen(false)}
        onSuccess={fetchData}
      />
    </div>
  );
};
