import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  Users,
  Search,
  PlusCircle,
  Shield,
  Filter,
  ExternalLink,
  PhoneCall,
  Globe,
  RefreshCw,
} from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Pagination } from '../components/common/Pagination';
import { AddClientModal } from '../components/modals/AddClientModal';
import { listClients } from '../api';
import { Client } from '../types';

export const ClientsPage: React.FC = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const fetchClients = async () => {
    try {
      setLoading(true);
      setError(null);
      // Fetch list of clients
      const res = await listClients({ page: 1, page_size: 100 });
      setClients(res.data);
    } catch (err: unknown) {
      console.error('Failed to load clients:', err);
      setError('Unable to load client records. Please verify backend connectivity.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClients();
  }, []);

  // Filter and search clients client-side for smooth UX
  const filteredClients = useMemo(() => {
    return clients.filter((c) => {
      const matchesSearch =
        searchQuery.trim() === '' ||
        (c.external_reference &&
          c.external_reference.toLowerCase().includes(searchQuery.toLowerCase())) ||
        c.preferred_name.toLowerCase().includes(searchQuery.toLowerCase());

      const clientStatus = c.status || c.enrollment_status || 'active';
      const matchesStatus =
        statusFilter === 'all' || clientStatus.toLowerCase() === statusFilter.toLowerCase();

      return matchesSearch && matchesStatus;
    });
  }, [clients, searchQuery, statusFilter]);

  // Pagination calculation
  const totalPages = Math.ceil(filteredClients.length / pageSize) || 1;
  const paginatedClients = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredClients.slice(start, start + pageSize);
  }, [filteredClients, currentPage, pageSize]);

  // Handle client creation success
  const handleClientCreated = () => {
    fetchClients();
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'success';
      case 'inactive':
        return 'warning';
      case 'completed':
        return 'info';
      case 'withdrawn':
        return 'danger';
      default:
        return 'neutral';
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Controls Bar */}
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
            <Users size={22} />
          </div>
          <div>
            <h1 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, margin: 0 }}>
              Client Directory
            </h1>
            <p style={{ margin: 0, fontSize: 'var(--font-size-sm)', color: 'var(--text-muted)' }}>
              {clients.length} synthetic client retention profile{clients.length === 1 ? '' : 's'}{' '}
              enrolled
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchClients}
            title="Refresh clients list"
            icon={<RefreshCw size={16} />}
          >
            Refresh
          </Button>
          <Button
            variant="primary"
            size="md"
            icon={<PlusCircle size={18} />}
            onClick={() => setIsAddModalOpen(true)}
          >
            Enroll New Client
          </Button>
        </div>
      </div>

      {/* Privacy Notice Banner */}
      <div
        style={{
          padding: '12px 18px',
          background: 'var(--primary-50)',
          border: '1px solid var(--primary-200)',
          borderRadius: 'var(--radius-md)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
        }}
      >
        <Shield size={20} color="var(--primary-700)" style={{ flexShrink: 0 }} />
        <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--primary-900)' }}>
          <strong>Privacy & Dignity Standard:</strong> Real names, clinical diagnoses, and contact
          numbers are protected. Staff view external pseudonym references (e.g.{' '}
          <code>SYNTH-PAT-XXXX</code>) and preferred names only.
        </span>
      </div>

      {/* Search and Filters Card */}
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
          <div
            style={{
              position: 'relative',
              flex: '1 1 320px',
              maxWidth: '450px',
            }}
          >
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
              placeholder="Search by reference (SYNTH-...) or preferred name..."
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

          {/* Status Filter Buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <Filter size={16} color="var(--text-muted)" style={{ marginRight: '4px' }} />
            {(['all', 'active', 'inactive', 'completed', 'withdrawn'] as const).map((st) => (
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

      {/* Main Table Card */}
      <Card>
        {loading ? (
          <LoadingSpinner message="Loading client directory..." />
        ) : error ? (
          <div
            style={{
              padding: '24px',
              textAlign: 'center',
              color: 'var(--status-danger)',
              fontSize: 'var(--font-size-sm)',
            }}
          >
            <p>{error}</p>
            <Button variant="outline" size="sm" onClick={fetchClients} style={{ marginTop: '12px' }}>
              Retry
            </Button>
          </div>
        ) : paginatedClients.length === 0 ? (
          <EmptyState
            icon={<Users size={36} />}
            title="No client records match"
            description={
              searchQuery || statusFilter !== 'all'
                ? 'Try adjusting your search criteria or resetting status filters.'
                : 'No client records have been registered yet. Add the first synthetic client to get started.'
            }
            action={
              <Button
                variant="primary"
                size="sm"
                icon={<PlusCircle size={16} />}
                onClick={() => setIsAddModalOpen(true)}
              >
                Enroll New Client
              </Button>
            }
          />
        ) : (
          <div>
            <div style={{ overflowX: 'auto' }}>
              <table
                style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  textAlign: 'left',
                }}
              >
                <thead>
                  <tr
                    style={{
                      borderBottom: '1px solid var(--border-color)',
                      background: 'var(--bg-subtle)',
                      color: 'var(--text-secondary)',
                      fontSize: 'var(--font-size-xs)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}
                  >
                    <th style={{ padding: '12px 16px', fontWeight: 600 }}>External Reference</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600 }}>Preferred Name</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600 }}>Language</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600 }}>Enrollment Status</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600 }}>Enrolled Date</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600, textAlign: 'right' }}>
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedClients.map((client) => {
                    const status = client.status || client.enrollment_status || 'active';
                    return (
                      <tr
                        key={client.id}
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
                        {/* Reference */}
                        <td style={{ padding: '14px 16px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <Shield size={15} color="var(--primary-600)" />
                            <span
                              style={{
                                fontFamily: 'monospace',
                                fontWeight: 600,
                                fontSize: 'var(--font-size-xs)',
                                color: 'var(--text-main)',
                              }}
                            >
                              {client.external_reference || 'SYNTH-UNKNOWN'}
                            </span>
                          </div>
                        </td>

                        {/* Preferred Name */}
                        <td style={{ padding: '14px 16px' }}>
                          <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                            {client.preferred_name}
                          </div>
                        </td>

                        {/* Language */}
                        <td style={{ padding: '14px 16px' }}>
                          <div
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '6px',
                              fontSize: 'var(--font-size-xs)',
                              color: 'var(--text-secondary)',
                            }}
                          >
                            <Globe size={14} color="var(--text-muted)" />
                            <span style={{ textTransform: 'uppercase' }}>
                              {client.preferred_language || 'EN'}
                            </span>
                          </div>
                        </td>

                        {/* Status */}
                        <td style={{ padding: '14px 16px' }}>
                          <Badge variant={getStatusBadgeVariant(status)} size="sm">
                            {status}
                          </Badge>
                        </td>

                        {/* Created Date */}
                        <td
                          style={{
                            padding: '14px 16px',
                            fontSize: 'var(--font-size-xs)',
                            color: 'var(--text-muted)',
                          }}
                        >
                          {client.created_at
                            ? new Date(client.created_at).toLocaleDateString(undefined, {
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric',
                              })
                            : '—'}
                        </td>

                        {/* Actions */}
                        <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                          <Link
                            to={`/clients/${client.id}`}
                            style={{ textDecoration: 'none' }}
                          >
                            <Button
                              variant="outline"
                              size="sm"
                              icon={<ExternalLink size={14} />}
                            >
                              View Profile
                            </Button>
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div
                style={{
                  marginTop: '16px',
                  display: 'flex',
                  justifyContent: 'center',
                }}
              >
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

      {/* Add Client Modal */}
      <AddClientModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSuccess={handleClientCreated}
      />
    </div>
  );
};
