import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertTriangle,
  PlusCircle,
  CheckCircle2,
  Clock,
  Filter,
  RefreshCw,
  Search,
  ShieldAlert,
  User,
  AlertCircle,
  Eye,
} from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Pagination } from '../components/common/Pagination';
import { CreateEscalationModal } from '../components/modals/CreateEscalationModal';
import { listEscalations, updateEscalation, listClients } from '../api';
import { Escalation, Client, EscalationStatus } from '../types';

export const EscalationsPage: React.FC = () => {
  const [escalations, setEscalations] = useState<Escalation[]>([]);
  const [clientsMap, setClientsMap] = useState<Record<string, Client>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('open');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [eRes, cRes] = await Promise.all([
        listEscalations({ page: 1, page_size: 100 }),
        listClients({ page: 1, page_size: 100 }),
      ]);

      setEscalations(eRes.data);

      const map: Record<string, Client> = {};
      cRes.data.forEach((c) => {
        map[c.id] = c;
      });
      setClientsMap(map);
    } catch (err) {
      console.error('Failed to load escalations:', err);
      setError('Unable to load human review queue. Please check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleUpdateStatus = async (id: string, status: EscalationStatus) => {
    try {
      const updated = await updateEscalation(id, {
        status,
        resolved_at: status === 'resolved' ? new Date().toISOString() : null,
      });
      setEscalations((prev) => prev.map((e) => (e.id === id ? updated : e)));
    } catch (err) {
      console.error('Failed to update escalation status:', err);
      alert('Could not update escalation status.');
    }
  };

  // Filter & Search
  const filteredEscalations = useMemo(() => {
    return escalations.filter((e) => {
      const client = clientsMap[e.client_id];
      const clientName = client ? client.preferred_name.toLowerCase() : '';
      const clientRef = client && client.external_reference ? client.external_reference.toLowerCase() : '';
      const reasonStr = e.reason.toLowerCase();
      const q = searchQuery.toLowerCase().trim();

      const matchesSearch =
        q === '' || clientName.includes(q) || clientRef.includes(q) || reasonStr.includes(q);

      const matchesStatus =
        statusFilter === 'all' ||
        (statusFilter === 'open'
          ? e.status === 'open' || e.status === 'in_review'
          : e.status.toLowerCase() === statusFilter.toLowerCase());

      const matchesCategory =
        categoryFilter === 'all' || e.category.toLowerCase() === categoryFilter.toLowerCase();

      return matchesSearch && matchesStatus && matchesCategory;
    });
  }, [escalations, clientsMap, searchQuery, statusFilter, categoryFilter]);

  // Sort: open/in_review first, urgent priority first
  const sortedEscalations = useMemo(() => {
    const priorityWeight: Record<string, number> = { urgent: 3, high: 2, normal: 1 };
    return [...filteredEscalations].sort((a, b) => {
      const pDiff = (priorityWeight[b.priority] || 0) - (priorityWeight[a.priority] || 0);
      if (pDiff !== 0) return pDiff;
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });
  }, [filteredEscalations]);

  // Pagination
  const totalPages = Math.ceil(sortedEscalations.length / pageSize) || 1;
  const paginatedEscalations = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedEscalations.slice(start, start + pageSize);
  }, [sortedEscalations, currentPage, pageSize]);

  // Counters
  const activeCount = escalations.filter((e) => e.status === 'open' || e.status === 'in_review').length;
  const urgentCount = escalations.filter(
    (e) => (e.status === 'open' || e.status === 'in_review') && e.priority === 'urgent'
  ).length;
  const resolvedCount = escalations.filter((e) => e.status === 'resolved').length;

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
              background: 'var(--status-danger-bg)',
              color: 'var(--status-danger)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <ShieldAlert size={22} />
          </div>
          <div>
            <h1 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, margin: 0 }}>
              Clinical & Support Escalations
            </h1>
            <p style={{ margin: 0, fontSize: 'var(--font-size-sm)', color: 'var(--text-muted)' }}>
              Human-in-the-loop review queue for clinical safety, triage, and sensitive situations
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
            variant="danger"
            size="md"
            icon={<PlusCircle size={18} />}
            onClick={() => setIsCreateModalOpen(true)}
          >
            Log Escalation
          </Button>
        </div>
      </div>

      {/* Human Review Oversight Banner */}
      <div
        style={{
          padding: '16px 20px',
          background: 'var(--status-warning-bg)',
          border: '1px solid var(--status-warning-border)',
          borderRadius: 'var(--radius-md)',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '14px',
        }}
      >
        <AlertTriangle size={22} color="var(--status-warning)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-main)', lineHeight: 1.5 }}>
          <strong>Safety & Governance Directive:</strong> CareFlow AI does not diagnose, prescribe, adjust
          medication, or provide emergency interventions. When client messages indicate clinical symptoms,
          adverse drug events, distress, or express desire to speak with human staff, the platform
          routes the item here for qualified healthcare staff evaluation.
        </div>
      </div>

      {/* KPI Counters Bar */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
        }}
      >
        <Card>
          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', fontWeight: 600 }}>
            REQUIRING STAFF REVIEW
          </div>
          <div
            style={{
              fontSize: 'var(--font-size-3xl)',
              fontWeight: 700,
              color: activeCount > 0 ? 'var(--status-danger)' : 'var(--text-secondary)',
              marginTop: '4px',
            }}
          >
            {activeCount}
          </div>
        </Card>

        <Card>
          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', fontWeight: 600 }}>
            URGENT TRIAGE PRIORITY
          </div>
          <div
            style={{
              fontSize: 'var(--font-size-3xl)',
              fontWeight: 700,
              color: urgentCount > 0 ? 'var(--status-danger)' : 'var(--text-secondary)',
              marginTop: '4px',
            }}
          >
            {urgentCount}
          </div>
        </Card>

        <Card>
          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', fontWeight: 600 }}>
            RESOLVED BY STAFF
          </div>
          <div
            style={{
              fontSize: 'var(--font-size-3xl)',
              fontWeight: 700,
              color: 'var(--status-success)',
              marginTop: '4px',
            }}
          >
            {resolvedCount}
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
              placeholder="Search escalation reason or client..."
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

          {/* Status Pills */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <Filter size={16} color="var(--text-muted)" style={{ marginRight: '4px' }} />
            {[
              { key: 'open', label: 'Open / In Review' },
              { key: 'resolved', label: 'Resolved' },
              { key: 'all', label: 'All Items' },
            ].map((st) => (
              <button
                key={st.key}
                onClick={() => {
                  setStatusFilter(st.key);
                  setCurrentPage(1);
                }}
                style={{
                  padding: '6px 12px',
                  borderRadius: 'var(--radius-full)',
                  fontSize: 'var(--font-size-xs)',
                  fontWeight: 600,
                  border:
                    statusFilter === st.key
                      ? '1px solid var(--status-danger)'
                      : '1px solid var(--border-color)',
                  background: statusFilter === st.key ? 'var(--status-danger)' : 'var(--bg-surface)',
                  color: statusFilter === st.key ? 'var(--text-inverse)' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                {st.label}
              </button>
            ))}

            <div style={{ borderLeft: '1px solid var(--border-color)', height: '20px', margin: '0 4px' }} />

            {/* Category Select */}
            <select
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value);
                setCurrentPage(1);
              }}
              style={{
                padding: '6px 10px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-color)',
                fontSize: 'var(--font-size-xs)',
                outline: 'none',
              }}
            >
              <option value="all">All Categories</option>
              <option value="clinical_concern">Clinical Concern</option>
              <option value="medication_concern">Medication Concern</option>
              <option value="sensitive_concern">Sensitive Concern</option>
              <option value="human_request">Human Request</option>
              <option value="emergency_related">Emergency Related</option>
              <option value="unknown_intent">Unknown Intent</option>
              <option value="ai_uncertainty">AI Uncertainty</option>
              <option value="system_failure">System Failure</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Escalations List */}
      <Card>
        {loading ? (
          <LoadingSpinner message="Loading escalation queue..." />
        ) : error ? (
          <div style={{ padding: '24px', textAlign: 'center', color: 'var(--status-danger)' }}>
            <p>{error}</p>
            <Button variant="outline" size="sm" onClick={fetchData} style={{ marginTop: '12px' }}>
              Retry
            </Button>
          </div>
        ) : paginatedEscalations.length === 0 ? (
          <EmptyState
            icon={<CheckCircle2 size={36} />}
            title="No escalations in queue"
            description={
              searchQuery || statusFilter !== 'open' || categoryFilter !== 'all'
                ? 'Try adjusting your filters or search terms.'
                : 'The human review queue is currently empty. No urgent clinical flags detected.'
            }
          />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {paginatedEscalations.map((esc) => {
              const client = clientsMap[esc.client_id];
              const isResolved = esc.status === 'resolved';

              return (
                <div
                  key={esc.id}
                  style={{
                    padding: '16px',
                    borderRadius: 'var(--radius-md)',
                    border: `1px solid ${
                      isResolved
                        ? 'var(--border-color)'
                        : esc.priority === 'urgent'
                        ? 'var(--status-danger-border)'
                        : 'var(--status-warning-border)'
                    }`,
                    background: isResolved
                      ? 'var(--bg-subtle)'
                      : esc.priority === 'urgent'
                      ? 'var(--status-danger-bg)'
                      : 'var(--status-warning-bg)',
                    display: 'flex',
                    flexWrap: 'wrap',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '16px',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div style={{ flex: '1 1 400px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px', flexWrap: 'wrap' }}>
                      <Badge
                        variant={
                          esc.priority === 'urgent'
                            ? 'danger'
                            : esc.priority === 'high'
                            ? 'warning'
                            : 'neutral'
                        }
                        size="sm"
                      >
                        {esc.priority.toUpperCase()} PRIORITY
                      </Badge>

                      <Badge variant="neutral" size="sm">
                        {esc.category.replace(/_/g, ' ').toUpperCase()}
                      </Badge>

                      <Badge
                        variant={isResolved ? 'success' : esc.status === 'in_review' ? 'info' : 'warning'}
                        size="sm"
                      >
                        {esc.status.toUpperCase()}
                      </Badge>

                      {esc.assigned_to && (
                        <span
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            fontSize: 'var(--font-size-xs)',
                            color: 'var(--text-secondary)',
                          }}
                        >
                          <User size={13} />
                          Reviewer: {esc.assigned_to}
                        </span>
                      )}
                    </div>

                    <div
                      style={{
                        fontSize: 'var(--font-size-sm)',
                        fontWeight: 600,
                        color: 'var(--text-main)',
                        lineHeight: 1.4,
                      }}
                    >
                      {esc.reason}
                    </div>

                    <div style={{ marginTop: '8px', fontSize: 'var(--font-size-xs)', color: 'var(--text-secondary)' }}>
                      Client:{' '}
                      <Link
                        to={`/clients/${esc.client_id}`}
                        style={{
                          textDecoration: 'none',
                          color: 'var(--primary-700)',
                          fontWeight: 600,
                        }}
                      >
                        {client ? client.preferred_name : 'Client Profile'}{' '}
                        <span style={{ color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                          ({client?.external_reference || esc.client_id.substring(0, 8)})
                        </span>
                      </Link>{' '}
                      • Reported: {new Date(esc.created_at).toLocaleString()}
                      {esc.resolved_at && ` • Resolved: ${new Date(esc.resolved_at).toLocaleString()}`}
                    </div>
                  </div>

                  {/* Actions */}
                  <div>
                    {!isResolved ? (
                      <div style={{ display: 'flex', gap: '8px' }}>
                        {esc.status === 'open' && (
                          <Button
                            size="sm"
                            variant="outline"
                            icon={<Eye size={14} />}
                            onClick={() => handleUpdateStatus(esc.id, 'in_review')}
                          >
                            Mark In-Review
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="primary"
                          icon={<CheckCircle2 size={14} />}
                          onClick={() => handleUpdateStatus(esc.id, 'resolved')}
                        >
                          Resolve
                        </Button>
                      </div>
                    ) : (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <CheckCircle2 size={16} color="var(--status-success)" />
                        <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--status-success)', fontWeight: 600 }}>
                          Resolved by Staff
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

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

      {/* Log Escalation Modal */}
      <CreateEscalationModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={() => fetchData()}
      />
    </div>
  );
};
