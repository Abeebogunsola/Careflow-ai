import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  ClipboardList,
  PlusCircle,
  CheckCircle2,
  Clock,
  Filter,
  RefreshCw,
  Search,
  User,
  AlertCircle,
  Calendar,
} from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Pagination } from '../components/common/Pagination';
import { CreateFollowUpModal } from '../components/modals/CreateFollowUpModal';
import { listFollowUps, updateFollowUp, listClients } from '../api';
import { FollowUpTask, Client, FollowUpStatus } from '../types';

export const FollowUpsPage: React.FC = () => {
  const [tasks, setTasks] = useState<FollowUpTask[]>([]);
  const [clientsMap, setClientsMap] = useState<Record<string, Client>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('pending');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [fRes, cRes] = await Promise.all([
        listFollowUps({ page: 1, page_size: 100 }),
        listClients({ page: 1, page_size: 100 }),
      ]);

      setTasks(fRes.data);

      const map: Record<string, Client> = {};
      cRes.data.forEach((c) => {
        map[c.id] = c;
      });
      setClientsMap(map);
    } catch (err) {
      console.error('Failed to load follow-up tasks:', err);
      setError('Unable to load follow-up tasks. Please check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleUpdateStatus = async (
    id: string,
    status: FollowUpStatus
  ) => {
    try {
      const updated = await updateFollowUp(id, {
        status,
        completed_at: status === 'completed' ? new Date().toISOString() : null,
      });
      setTasks((prev) => prev.map((t) => (t.id === id ? updated : t)));
    } catch (err) {
      console.error('Failed to update task status:', err);
      alert('Could not update task status.');
    }
  };

  // Filter & Search
  const filteredTasks = useMemo(() => {
    return tasks.filter((t) => {
      const client = clientsMap[t.client_id];
      const clientName = client ? client.preferred_name.toLowerCase() : '';
      const clientRef = client && client.external_reference ? client.external_reference.toLowerCase() : '';
      const reasonStr = t.reason.toLowerCase();
      const q = searchQuery.toLowerCase().trim();

      const matchesSearch =
        q === '' || clientName.includes(q) || clientRef.includes(q) || reasonStr.includes(q);

      const matchesStatus =
        statusFilter === 'all' ||
        (statusFilter === 'pending'
          ? t.status === 'pending' || t.status === 'in_progress'
          : t.status.toLowerCase() === statusFilter.toLowerCase());

      const matchesPriority =
        priorityFilter === 'all' || t.priority.toLowerCase() === priorityFilter.toLowerCase();

      return matchesSearch && matchesStatus && matchesPriority;
    });
  }, [tasks, clientsMap, searchQuery, statusFilter, priorityFilter]);

  // Sort: urgent priority first, then due date
  const sortedTasks = useMemo(() => {
    const priorityWeight: Record<string, number> = { urgent: 3, high: 2, normal: 1 };
    return [...filteredTasks].sort((a, b) => {
      const pDiff = (priorityWeight[b.priority] || 0) - (priorityWeight[a.priority] || 0);
      if (pDiff !== 0) return pDiff;
      if (a.due_at && b.due_at) return new Date(a.due_at).getTime() - new Date(b.due_at).getTime();
      return 0;
    });
  }, [filteredTasks]);

  // Pagination
  const totalPages = Math.ceil(sortedTasks.length / pageSize) || 1;
  const paginatedTasks = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedTasks.slice(start, start + pageSize);
  }, [sortedTasks, currentPage, pageSize]);

  // Counters
  const pendingCount = tasks.filter((t) => t.status === 'pending' || t.status === 'in_progress').length;
  const urgentCount = tasks.filter(
    (t) => (t.status === 'pending' || t.status === 'in_progress') && t.priority === 'urgent'
  ).length;
  const completedCount = tasks.filter((t) => t.status === 'completed').length;

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
            <ClipboardList size={22} />
          </div>
          <div>
            <h1 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, margin: 0 }}>
              Care Navigation & Outreach Tasks
            </h1>
            <p style={{ margin: 0, fontSize: 'var(--font-size-sm)', color: 'var(--text-muted)' }}>
              Proactive follow-up worklist to prevent disengagement and support adherence
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
            onClick={() => setIsCreateModalOpen(true)}
          >
            Create Follow-Up
          </Button>
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
            OPEN TASKS (PENDING / IN PROGRESS)
          </div>
          <div
            style={{
              fontSize: 'var(--font-size-3xl)',
              fontWeight: 700,
              color: 'var(--primary-700)',
              marginTop: '4px',
            }}
          >
            {pendingCount}
          </div>
        </Card>

        <Card>
          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', fontWeight: 600 }}>
            URGENT OUTREACH REQUIRED
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
            RESOLVED / COMPLETED
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
              placeholder="Search outreach reason or client..."
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

          {/* Status & Priority Pills */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <Filter size={16} color="var(--text-muted)" style={{ marginRight: '4px' }} />
            {[
              { key: 'pending', label: 'Open Tasks' },
              { key: 'completed', label: 'Completed' },
              { key: 'all', label: 'All Statuses' },
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
                      ? '1px solid var(--primary-700)'
                      : '1px solid var(--border-color)',
                  background: statusFilter === st.key ? 'var(--primary-700)' : 'var(--bg-surface)',
                  color: statusFilter === st.key ? 'var(--text-inverse)' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                {st.label}
              </button>
            ))}

            <div style={{ borderLeft: '1px solid var(--border-color)', height: '20px', margin: '0 4px' }} />

            <select
              value={priorityFilter}
              onChange={(e) => {
                setPriorityFilter(e.target.value);
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
              <option value="all">All Priorities</option>
              <option value="urgent">Urgent</option>
              <option value="high">High</option>
              <option value="normal">Normal</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Task List */}
      <Card>
        {loading ? (
          <LoadingSpinner message="Loading outreach tasks..." />
        ) : error ? (
          <div style={{ padding: '24px', textAlign: 'center', color: 'var(--status-danger)' }}>
            <p>{error}</p>
            <Button variant="outline" size="sm" onClick={fetchData} style={{ marginTop: '12px' }}>
              Retry
            </Button>
          </div>
        ) : paginatedTasks.length === 0 ? (
          <EmptyState
            icon={<ClipboardList size={36} />}
            title="No follow-up tasks match"
            description={
              searchQuery || statusFilter !== 'pending' || priorityFilter !== 'all'
                ? 'Try adjusting your filters or search terms.'
                : 'All care retention follow-up tasks have been addressed! Great work.'
            }
            action={
              <Button
                variant="primary"
                size="sm"
                icon={<PlusCircle size={16} />}
                onClick={() => setIsCreateModalOpen(true)}
              >
                Create Follow-Up
              </Button>
            }
          />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {paginatedTasks.map((task) => {
              const client = clientsMap[task.client_id];
              const isCompleted = task.status === 'completed';

              return (
                <div
                  key={task.id}
                  style={{
                    padding: '16px',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-color)',
                    background: isCompleted ? 'var(--bg-subtle)' : 'var(--bg-surface)',
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
                        variant={isCompleted ? 'success' : task.status === 'in_progress' ? 'warning' : 'info'}
                        size="sm"
                      >
                        {task.status.toUpperCase()}
                      </Badge>

                      {task.due_at && (
                        <span
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            fontSize: 'var(--font-size-xs)',
                            color: 'var(--text-muted)',
                          }}
                        >
                          <Calendar size={13} />
                          Due: {new Date(task.due_at).toLocaleDateString()}
                        </span>
                      )}

                      {task.assigned_to && (
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
                          Assigned: {task.assigned_to}
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
                      {task.reason}
                    </div>

                    <div style={{ marginTop: '6px', fontSize: 'var(--font-size-xs)' }}>
                      Client:{' '}
                      <Link
                        to={`/clients/${task.client_id}`}
                        style={{
                          textDecoration: 'none',
                          color: 'var(--primary-700)',
                          fontWeight: 600,
                        }}
                      >
                        {client ? client.preferred_name : 'Client Profile'}{' '}
                        <span style={{ color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                          ({client?.external_reference || task.client_id.substring(0, 8)})
                        </span>
                      </Link>
                    </div>
                  </div>

                  {/* Actions */}
                  <div>
                    {!isCompleted ? (
                      <div style={{ display: 'flex', gap: '8px' }}>
                        {task.status === 'pending' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleUpdateStatus(task.id, 'in_progress')}
                          >
                            In Progress
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="primary"
                          icon={<CheckCircle2 size={14} />}
                          onClick={() => handleUpdateStatus(task.id, 'completed')}
                        >
                          Mark Done
                        </Button>
                      </div>
                    ) : (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <CheckCircle2 size={16} color="var(--status-success)" />
                        <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--status-success)', fontWeight: 600 }}>
                          Resolved
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

      {/* Create Modal */}
      <CreateFollowUpModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={() => fetchData()}
      />
    </div>
  );
};
