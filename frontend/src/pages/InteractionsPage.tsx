import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  MessageSquare,
  Send,
  ArrowDownLeft,
  ArrowUpRight,
  Filter,
  RefreshCw,
  Search,
  Shield,
  Bot,
  User,
  Phone,
  Globe,
} from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Pagination } from '../components/common/Pagination';
import { RecordInteractionModal } from '../components/modals/RecordInteractionModal';
import { listInteractions, listClients } from '../api';
import { Interaction, Client } from '../types';

export const InteractionsPage: React.FC = () => {
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [clientsMap, setClientsMap] = useState<Record<string, Client>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [channelFilter, setChannelFilter] = useState<string>('all');
  const [directionFilter, setDirectionFilter] = useState<string>('all');
  const [intentFilter, setIntentFilter] = useState<string>('all');

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;
  const [isRecordModalOpen, setIsRecordModalOpen] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [intRes, clientsRes] = await Promise.all([
        listInteractions({ page: 1, page_size: 100 }),
        listClients({ page: 1, page_size: 100 }),
      ]);

      setInteractions(intRes.data);

      const map: Record<string, Client> = {};
      clientsRes.data.forEach((c) => {
        map[c.id] = c;
      });
      setClientsMap(map);
    } catch (err) {
      console.error('Failed to load interactions:', err);
      setError('Unable to load interactions ledger. Please check backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Filtered interactions
  const filteredInteractions = useMemo(() => {
    return interactions.filter((i) => {
      const client = clientsMap[i.client_id];
      const clientName = client ? client.preferred_name.toLowerCase() : '';
      const clientRef = client && client.external_reference ? client.external_reference.toLowerCase() : '';
      const contentStr = (i.content || '').toLowerCase();
      const q = searchQuery.toLowerCase().trim();

      const matchesSearch =
        q === '' || clientName.includes(q) || clientRef.includes(q) || contentStr.includes(q);

      const matchesChannel =
        channelFilter === 'all' || i.channel.toLowerCase() === channelFilter.toLowerCase();

      const matchesDirection =
        directionFilter === 'all' || i.direction.toLowerCase() === directionFilter.toLowerCase();

      const matchesIntent =
        intentFilter === 'all' || (i.intent_category && i.intent_category.toLowerCase() === intentFilter.toLowerCase());

      return matchesSearch && matchesChannel && matchesDirection && matchesIntent;
    });
  }, [interactions, clientsMap, searchQuery, channelFilter, directionFilter, intentFilter]);

  // Sort latest first
  const sortedInteractions = useMemo(() => {
    return [...filteredInteractions].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  }, [filteredInteractions]);

  // Pagination
  const totalPages = Math.ceil(sortedInteractions.length / pageSize) || 1;
  const paginatedInteractions = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedInteractions.slice(start, start + pageSize);
  }, [sortedInteractions, currentPage, pageSize]);

  // Counters
  const incomingCount = interactions.filter((i) => i.direction === 'incoming').length;
  const outgoingCount = interactions.filter((i) => i.direction === 'outgoing').length;

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
            <MessageSquare size={22} />
          </div>
          <div>
            <h1 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, margin: 0 }}>
              Interactions & Communication Ledger
            </h1>
            <p style={{ margin: 0, fontSize: 'var(--font-size-sm)', color: 'var(--text-muted)' }}>
              Complete audit ledger of client inquiries, reminders, and AI-categorized intents
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
            icon={<Send size={18} />}
            onClick={() => setIsRecordModalOpen(true)}
          >
            Record Interaction
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
            TOTAL COMMUNICATIONS LOGGED
          </div>
          <div
            style={{
              fontSize: 'var(--font-size-3xl)',
              fontWeight: 700,
              color: 'var(--primary-700)',
              marginTop: '4px',
            }}
          >
            {interactions.length}
          </div>
        </Card>

        <Card>
          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', fontWeight: 600 }}>
            INCOMING CLIENT MESSAGES
          </div>
          <div
            style={{
              fontSize: 'var(--font-size-3xl)',
              fontWeight: 700,
              color: 'var(--accent-600)',
              marginTop: '4px',
            }}
          >
            {incomingCount}
          </div>
        </Card>

        <Card>
          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', fontWeight: 600 }}>
            OUTGOING REMINDERS / STAFF REPLIES
          </div>
          <div
            style={{
              fontSize: 'var(--font-size-3xl)',
              fontWeight: 700,
              color: 'var(--status-success)',
              marginTop: '4px',
            }}
          >
            {outgoingCount}
          </div>
        </Card>
      </div>

      {/* Filter Controls Card */}
      <Card>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {/* Top Row: Search & Direction */}
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '12px',
            }}
          >
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
                placeholder="Search message text, client, or ref..."
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

            {/* Direction Filter */}
            <div style={{ display: 'flex', gap: '8px' }}>
              {(['all', 'incoming', 'outgoing'] as const).map((dir) => (
                <button
                  key={dir}
                  onClick={() => {
                    setDirectionFilter(dir);
                    setCurrentPage(1);
                  }}
                  style={{
                    padding: '6px 12px',
                    borderRadius: 'var(--radius-full)',
                    fontSize: 'var(--font-size-xs)',
                    fontWeight: 600,
                    border:
                      directionFilter === dir
                        ? '1px solid var(--primary-700)'
                        : '1px solid var(--border-color)',
                    background: directionFilter === dir ? 'var(--primary-700)' : 'var(--bg-surface)',
                    color: directionFilter === dir ? 'var(--text-inverse)' : 'var(--text-secondary)',
                    cursor: 'pointer',
                    textTransform: 'capitalize',
                  }}
                >
                  {dir}
                </button>
              ))}
            </div>
          </div>

          {/* Bottom Row: Channel & Intent Filters */}
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              alignItems: 'center',
              gap: '12px',
              fontSize: 'var(--font-size-xs)',
              color: 'var(--text-secondary)',
              borderTop: '1px solid var(--border-light)',
              paddingTop: '12px',
            }}
          >
            <span style={{ fontWeight: 600 }}>Channel:</span>
            {(['all', 'whatsapp', 'sms', 'web', 'email'] as const).map((ch) => (
              <button
                key={ch}
                onClick={() => {
                  setChannelFilter(ch);
                  setCurrentPage(1);
                }}
                style={{
                  padding: '4px 10px',
                  borderRadius: 'var(--radius-sm)',
                  border: channelFilter === ch ? '1px solid var(--primary-700)' : '1px solid var(--border-color)',
                  background: channelFilter === ch ? 'var(--primary-50)' : 'var(--bg-surface)',
                  color: channelFilter === ch ? 'var(--primary-800)' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontWeight: channelFilter === ch ? 700 : 500,
                  fontSize: 'var(--font-size-xs)',
                  textTransform: 'uppercase',
                }}
              >
                {ch}
              </button>
            ))}

            <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontWeight: 600 }}>Intent:</span>
              <select
                value={intentFilter}
                onChange={(e) => {
                  setIntentFilter(e.target.value);
                  setCurrentPage(1);
                }}
                style={{
                  padding: '5px 10px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-color)',
                  fontSize: 'var(--font-size-xs)',
                  outline: 'none',
                }}
              >
                <option value="all">All Intents</option>
                <option value="appointment_inquiry">Appointment Inquiry</option>
                <option value="rescheduling">Rescheduling</option>
                <option value="clinic_info">Clinic Info</option>
                <option value="general_support">General Support</option>
                <option value="clinical_concern">Clinical Concern (Flagged)</option>
                <option value="emergency_escalation">Emergency Concern (Escalated)</option>
                <option value="medication_concern">Medication Concern</option>
              </select>
            </div>
          </div>
        </div>
      </Card>

      {/* Interactions Feed */}
      <Card>
        {loading ? (
          <LoadingSpinner message="Loading communications feed..." />
        ) : error ? (
          <div style={{ padding: '24px', textAlign: 'center', color: 'var(--status-danger)' }}>
            <p>{error}</p>
            <Button variant="outline" size="sm" onClick={fetchData} style={{ marginTop: '12px' }}>
              Retry
            </Button>
          </div>
        ) : paginatedInteractions.length === 0 ? (
          <EmptyState
            icon={<MessageSquare size={36} />}
            title="No interactions match your filter"
            description="Adjust your search criteria, channel filters, or log a new interaction."
            action={
              <Button
                variant="primary"
                size="sm"
                icon={<Send size={16} />}
                onClick={() => setIsRecordModalOpen(true)}
              >
                Record Interaction
              </Button>
            }
          />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {paginatedInteractions.map((item) => {
              const client = clientsMap[item.client_id];
              const isIncoming = item.direction === 'incoming';

              return (
                <div
                  key={item.id}
                  style={{
                    padding: '16px',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-color)',
                    background: isIncoming ? 'var(--bg-surface)' : 'var(--primary-50)',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: '8px',
                      marginBottom: '10px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                      {/* Direction Badge */}
                      <Badge
                        variant={isIncoming ? 'info' : 'success'}
                        size="sm"
                      >
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          {isIncoming ? <ArrowDownLeft size={12} /> : <ArrowUpRight size={12} />}
                          {item.direction.toUpperCase()}
                        </span>
                      </Badge>

                      {/* Channel Badge */}
                      <Badge variant="neutral" size="sm">
                        {item.channel.toUpperCase()}
                      </Badge>

                      {/* Type Badge */}
                      <span
                        style={{
                          fontSize: 'var(--font-size-xs)',
                          color: 'var(--text-secondary)',
                          textTransform: 'capitalize',
                          fontWeight: 500,
                        }}
                      >
                        {item.interaction_type.replace(/_/g, ' ')}
                      </span>

                      {/* AI Intent Badge */}
                      {item.intent_category && (
                        <Badge
                          variant={
                            item.intent_category.includes('clinical') ||
                            item.intent_category.includes('emergency')
                              ? 'danger'
                              : 'warning'
                          }
                          size="sm"
                        >
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                            <Bot size={12} />
                            {item.intent_category.replace(/_/g, ' ')}
                          </span>
                        </Badge>
                      )}
                    </div>

                    {/* Client & Timestamp */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <Link
                        to={`/clients/${item.client_id}`}
                        style={{
                          textDecoration: 'none',
                          fontSize: 'var(--font-size-xs)',
                          color: 'var(--primary-700)',
                          fontWeight: 600,
                        }}
                      >
                        {client ? client.preferred_name : 'Client'}{' '}
                        <span style={{ color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                          ({client?.external_reference || item.client_id.substring(0, 8)})
                        </span>
                      </Link>

                      <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                        {new Date(item.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>

                  {/* Message Body */}
                  <p
                    style={{
                      margin: 0,
                      fontSize: 'var(--font-size-sm)',
                      color: 'var(--text-main)',
                      lineHeight: 1.5,
                      whiteSpace: 'pre-wrap',
                    }}
                  >
                    {item.content || 'No text content attached.'}
                  </p>
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

      {/* Record Interaction Modal */}
      <RecordInteractionModal
        isOpen={isRecordModalOpen}
        onClose={() => setIsRecordModalOpen(false)}
        onSuccess={() => fetchData()}
      />
    </div>
  );
};
