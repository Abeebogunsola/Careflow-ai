import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { EmptyState } from '../components/common/EmptyState';
import { Modal } from '../components/common/Modal';
import { Pagination } from '../components/common/Pagination';
import { Users } from 'lucide-react';

describe('Common UI Components', () => {
  describe('Badge', () => {
    it('renders with children and variant class', () => {
      render(<Badge variant="success">Active</Badge>);
      const badge = screen.getByText('Active');
      expect(badge).toBeInTheDocument();
      expect(badge.className).toContain('badge-success');
    });

    it('applies danger variant and custom className', () => {
      render(<Badge variant="danger" className="custom-cls">Urgent</Badge>);
      const badge = screen.getByText('Urgent');
      expect(badge.className).toContain('badge-danger');
      expect(badge.className).toContain('custom-cls');
    });
  });

  describe('Button', () => {
    it('renders text and responds to click', () => {
      const handleClick = vi.fn();
      render(<Button onClick={handleClick}>Click Me</Button>);
      const btn = screen.getByRole('button', { name: /click me/i });
      fireEvent.click(btn);
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('respects disabled state', () => {
      const handleClick = vi.fn();
      render(<Button disabled onClick={handleClick}>Disabled</Button>);
      const btn = screen.getByRole('button', { name: /disabled/i });
      expect(btn).toBeDisabled();
      fireEvent.click(btn);
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('Card', () => {
    it('renders card title, action, and children', () => {
      render(
        <Card title="Card Title" action={<button>Action</button>}>
          <div>Card Content</div>
        </Card>
      );
      expect(screen.getByText('Card Title')).toBeInTheDocument();
      expect(screen.getByText('Action')).toBeInTheDocument();
      expect(screen.getByText('Card Content')).toBeInTheDocument();
    });
  });

  describe('EmptyState', () => {
    it('renders icon, title, description, and action button', () => {
      const onAction = vi.fn();
      render(
        <EmptyState
          icon={Users}
          title="No items found"
          description="Try creating a new record."
          actionLabel="Add Item"
          onAction={onAction}
        />
      );
      expect(screen.getByText('No items found')).toBeInTheDocument();
      expect(screen.getByText('Try creating a new record.')).toBeInTheDocument();
      const actionBtn = screen.getByRole('button', { name: /add item/i });
      fireEvent.click(actionBtn);
      expect(onAction).toHaveBeenCalledTimes(1);
    });
  });

  describe('Modal', () => {
    it('does not render when isOpen is false', () => {
      render(
        <Modal isOpen={false} onClose={() => {}} title="Test Modal">
          <div>Modal Body</div>
        </Modal>
      );
      expect(screen.queryByText('Test Modal')).not.toBeInTheDocument();
    });

    it('renders title and children when isOpen is true and triggers onClose', () => {
      const handleClose = vi.fn();
      render(
        <Modal isOpen={true} onClose={handleClose} title="Test Modal">
          <div>Modal Body Content</div>
        </Modal>
      );
      expect(screen.getByText('Test Modal')).toBeInTheDocument();
      expect(screen.getByText('Modal Body Content')).toBeInTheDocument();

      const closeBtn = screen.getByRole('button', { name: /close dialog/i });
      fireEvent.click(closeBtn);
      expect(handleClose).toHaveBeenCalledTimes(1);
    });
  });

  describe('Pagination', () => {
    it('handles next and previous page changes', () => {
      const handlePageChange = vi.fn();
      render(
        <Pagination
          currentPage={2}
          totalPages={5}
          pageSize={10}
          total={50}
          onPageChange={handlePageChange}
        />
      );

      expect(screen.getByText(/Page 2 of 5/i)).toBeInTheDocument();

      const prevBtn = screen.getByRole('button', { name: /previous/i });
      fireEvent.click(prevBtn);
      expect(handlePageChange).toHaveBeenCalledWith(1);

      const nextBtn = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextBtn);
      expect(handlePageChange).toHaveBeenCalledWith(3);
    });
  });
});
