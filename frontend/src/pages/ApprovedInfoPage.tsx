import React, { useEffect, useState, useMemo } from 'react';
import {
  BookOpen,
  PlusCircle,
  Filter,
  RefreshCw,
  Search,
  ShieldCheck,
  CheckCircle,
  XCircle,
  Calendar,
  Layers,
  FileText,
} from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Pagination } from '../components/common/Pagination';
import { AddApprovedInfoModal } from '../components/modals/AddApprovedInfoModal';
import { listApprovedInformation, updateApprovedInformation } from '../api';
import { ApprovedInformation, ApprovedInfoCategory } from '../types';

export const ApprovedInfoPage: React.FC = () => {
  const [items, setItems] = useState<ApprovedInformation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState<string>('all');

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 8;
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await listApprovedInformation({ page: 1, page_size: 100 });
      setItems(res.data);
    } catch (err) {
      console.error('Failed to load approved info:', err);
      setError('Unable to load approved reference knowledge base. Please check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleToggleActive = async (item: ApprovedInformation) => {
    try {
      const updated = await updateApprovedInformation(item.id, {
        is_active: !item.is_active,
      });
      setItems((prev) => prev.map((i) => (i.id === item.id ? updated : i)));
    } catch (err) {
      console.error('Failed to toggle status:', err);
      alert('Could not update status.');
    }
  };

  // Filter & Search
  const filteredItems = useMemo(() => {
    return items.filter((i) => {
      const titleStr = i.title.toLowerCase();
      const contentStr = i.content.toLowerCase();
      const q = searchQuery.toLowerCase().trim();

      const matchesSearch = q === '' || titleStr.includes(q) || contentStr.includes(q);

      const matchesCategory =
        categoryFilter === 'all' || i.category.toLowerCase() === categoryFilter.toLowerCase();

      const matchesActive =
        activeFilter === 'all' ||
        (activeFilter === 'active' ? i.is_active : !i.is_active);

      return matchesSearch && matchesCategory && matchesActive;
    });
  }, [items, searchQuery, categoryFilter, activeFilter]);

  // Sort by updated_at descending
  const sortedItems = useMemo(() => {
    return [...filteredItems].sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    );
  }, [filteredItems]);

  // Pagination
  const totalPages = Math.ceil(sortedItems.length / pageSize) || 1;
  const paginatedItems = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedItems.slice(start, start + pageSize);
  }, [sortedItems, currentPage, pageSize]);

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
            <BookOpen size={22} />
          </div>
          <div>
            <h1 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, margin: 0 }}>
              Approved Information & AI Knowledge Base
            </h1>
            <p style={{ margin: 0, fontSize: 'var(--font-size-sm)', color: 'var(--text-muted)' }}>
              Program-authorized reference content for client education and logistics support
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
            onClick={() => setIsAddModalOpen(true)}
          >
            Add Approved Info
          </Button>
        </div>
      </div>

      {/* Strict Reference Boundary Banner */}
      <div
        style={{
          padding: '16px 20px',
          background: 'var(--primary-50)',
          border: '1px solid var(--primary-200)',
          borderRadius: 'var(--radius-md)',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '14px',
        }}
      >
        <ShieldCheck size={22} color="var(--primary-700)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--primary-900)', lineHeight: 1.5 }}>
          <strong>Grounding & Verification Safety Rule:</strong> CareFlow AI conversational responses
          are strictly grounded in this validated repository. The agent cannot invent medical facts,
          alter appointment requirements, or advise on drug regimens outside this verified public health library.
        </div>
      </div>

      {/* Filters Bar */}
      <Card>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {/* Top Search */}
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '12px',
            }}
          >
            <div style={{ position: 'relative', flex: '1 1 300px', maxWidth: '450px' }}>
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
                placeholder="Search approved topic, title, or keywords..."
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

            {/* Active / Inactive filter */}
            <div style={{ display: 'flex', gap: '8px' }}>
              {[
                { key: 'all', label: 'All Items' },
                { key: 'active', label: 'Active Only' },
                { key: 'inactive', label: 'Inactive' },
              ].map((f) => (
                <button
                  key={f.key}
                  onClick={() => {
                    setActiveFilter(f.key);
                    setCurrentPage(1);
                  }}
                  style={{
                    padding: '6px 12px',
                    borderRadius: 'var(--radius-full)',
                    fontSize: 'var(--font-size-xs)',
                    fontWeight: 600,
                    border:
                      activeFilter === f.key
                        ? '1px solid var(--primary-700)'
                        : '1px solid var(--border-color)',
                    background: activeFilter === f.key ? 'var(--primary-700)' : 'var(--bg-surface)',
                    color: activeFilter === f.key ? 'var(--text-inverse)' : 'var(--text-secondary)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          {/* Category Tabs */}
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '8px',
              borderTop: '1px solid var(--border-light)',
              paddingTop: '12px',
              fontSize: 'var(--font-size-xs)',
            }}
          >
            <span style={{ fontWeight: 600, alignSelf: 'center', marginRight: '4px' }}>Category:</span>
            {[
              { key: 'all', label: 'All Categories' },
              { key: 'appointment_information', label: 'Appointment Info' },
              { key: 'clinic_logistics', label: 'Clinic Logistics' },
              { key: 'communication', label: 'Communication' },
              { key: 'program_information', label: 'Program Info' },
              { key: 'approved_education', label: 'Education & Support' },
            ].map((c) => (
              <button
                key={c.key}
                onClick={() => {
                  setCategoryFilter(c.key);
                  setCurrentPage(1);
                }}
                style={{
                  padding: '5px 12px',
                  borderRadius: 'var(--radius-sm)',
                  border:
                    categoryFilter === c.key
                      ? '1px solid var(--primary-700)'
                      : '1px solid var(--border-color)',
                  background: categoryFilter === c.key ? 'var(--primary-50)' : 'var(--bg-surface)',
                  color: categoryFilter === c.key ? 'var(--primary-800)' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontWeight: categoryFilter === c.key ? 700 : 500,
                  fontSize: 'var(--font-size-xs)',
                }}
              >
                {c.label}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Knowledge Base Cards Grid */}
      {loading ? (
        <LoadingSpinner message="Loading approved reference library..." />
      ) : error ? (
        <Card>
          <div style={{ padding: '24px', textAlign: 'center', color: 'var(--status-danger)' }}>
            <p>{error}</p>
            <Button variant="outline" size="sm" onClick={fetchData} style={{ marginTop: '12px' }}>
              Retry
            </Button>
          </div>
        </Card>
      ) : paginatedItems.length === 0 ? (
        <Card>
          <EmptyState
            icon={<BookOpen size={36} />}
            title="No approved information found"
            description={
              searchQuery || categoryFilter !== 'all' || activeFilter !== 'all'
                ? 'Try adjusting your search criteria or category filter.'
                : 'No approved knowledge items exist. Add the first reference entry.'
            }
            action={
              <Button
                variant="primary"
                size="sm"
                icon={<PlusCircle size={16} />}
                onClick={() => setIsAddModalOpen(true)}
              >
                Add Approved Info
              </Button>
            }
          />
        </Card>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
              gap: '16px',
            }}
          >
            {paginatedItems.map((item) => (
              <Card key={item.id}>
                <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                  {/* Top badges */}
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '10px',
                      gap: '8px',
                    }}
                  >
                    <Badge variant="neutral" size="sm">
                      {item.category.replace(/_/g, ' ').toUpperCase()}
                    </Badge>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span
                        style={{
                          fontSize: 'var(--font-size-xs)',
                          color: 'var(--text-muted)',
                          fontWeight: 600,
                        }}
                      >
                        v{item.version}
                      </span>
                      <Badge variant={item.is_active ? 'success' : 'neutral'} size="sm">
                        {item.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                  </div>

                  {/* Title */}
                  <h3
                    style={{
                      margin: '0 0 10px 0',
                      fontSize: 'var(--font-size-base)',
                      fontWeight: 700,
                      color: 'var(--text-main)',
                    }}
                  >
                    {item.title}
                  </h3>

                  {/* Content snippet */}
                  <p
                    style={{
                      margin: '0 0 16px 0',
                      fontSize: 'var(--font-size-sm)',
                      color: 'var(--text-secondary)',
                      lineHeight: 1.5,
                      flex: 1,
                      whiteSpace: 'pre-wrap',
                    }}
                  >
                    {item.content}
                  </p>

                  {/* Footer Bar */}
                  <div
                    style={{
                      borderTop: '1px solid var(--border-light)',
                      paddingTop: '12px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      fontSize: 'var(--font-size-xs)',
                      color: 'var(--text-muted)',
                    }}
                  >
                    <span>Updated {new Date(item.updated_at).toLocaleDateString()}</span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleToggleActive(item)}
                    >
                      {item.is_active ? 'Deactivate' : 'Activate'}
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={setCurrentPage}
              />
            </div>
          )}
        </div>
      )}

      {/* Add Modal */}
      <AddApprovedInfoModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSuccess={() => fetchData()}
      />
    </div>
  );
};
