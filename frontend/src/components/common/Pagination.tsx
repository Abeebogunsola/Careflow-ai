import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './Button';

interface PaginationProps {
  page?: number;
  currentPage?: number;
  pageSize?: number;
  total?: number;
  totalPages?: number;
  onPageChange: (newPage: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({
  page,
  currentPage,
  pageSize = 10,
  total = 0,
  totalPages: propTotalPages,
  onPageChange,
}) => {
  const activePage = currentPage || page || 1;
  const calculatedTotalPages = propTotalPages !== undefined
    ? Math.max(1, propTotalPages)
    : Math.max(1, Math.ceil(total / pageSize));

  const startItem = total === 0 ? 0 : (activePage - 1) * pageSize + 1;
  const endItem = Math.min(activePage * pageSize, total || (calculatedTotalPages * pageSize));

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 16px',
        backgroundColor: 'var(--bg-surface)',
        borderTop: '1px solid var(--border-color)',
        fontSize: 'var(--font-size-xs)',
        color: 'var(--text-secondary)',
      }}
    >
      <div>
        Showing <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{startItem}</span> to{' '}
        <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{endItem}</span> of{' '}
        <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{total}</span> entries
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Button
          variant="secondary"
          size="sm"
          disabled={activePage <= 1}
          onClick={() => onPageChange(activePage - 1)}
          icon={<ChevronLeft size={14} />}
        >
          Previous
        </Button>
        <span style={{ fontWeight: 500, padding: '0 4px' }}>
          Page {activePage} of {calculatedTotalPages}
        </span>
        <Button
          variant="secondary"
          size="sm"
          disabled={activePage >= calculatedTotalPages}
          onClick={() => onPageChange(activePage + 1)}
          icon={<ChevronRight size={14} />}
        >
          Next
        </Button>
      </div>
    </div>
  );
};
