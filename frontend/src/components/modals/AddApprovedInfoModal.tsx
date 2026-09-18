import React, { useState } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { createApprovedInformation } from '../../api';
import { ApprovedInfoCategory, ApprovedInformation } from '../../types';

interface AddApprovedInfoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (item: ApprovedInformation) => void;
}

export const AddApprovedInfoModal: React.FC<AddApprovedInfoModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState<ApprovedInfoCategory>('appointment_information');
  const [content, setContent] = useState('');
  const [version, setVersion] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) {
      setError('Title and content are required.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const created = await createApprovedInformation({
        title: title.trim(),
        category,
        content: content.trim(),
        version,
        is_active: true,
      });

      onSuccess(created);
      setTitle('');
      setContent('');
      setVersion(1);
      onClose();
    } catch (err: unknown) {
      console.error('Failed to create approved information:', err);
      setError('Failed to save approved information. Please check backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add Approved Reference Information">
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', margin: 0 }}>
          Only program-authorized information can be referenced by the AI for client responses.
        </p>

        {error && (
          <div
            style={{
              padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--status-danger-bg)',
              color: 'var(--status-danger)',
              fontSize: 'var(--font-size-xs)',
            }}
          >
            {error}
          </div>
        )}

        {/* Title */}
        <div>
          <label
            style={{
              display: 'block',
              fontSize: 'var(--font-size-xs)',
              fontWeight: 600,
              marginBottom: '6px',
            }}
          >
            Title / Topic *
          </label>
          <input
            type="text"
            required
            placeholder="e.g., Clinic Operating Hours & Pharmacy Location"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              fontSize: 'var(--font-size-sm)',
              outline: 'none',
            }}
          />
        </div>

        {/* Category */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 100px', gap: '12px' }}>
          <div>
            <label
              style={{
                display: 'block',
                fontSize: 'var(--font-size-xs)',
                fontWeight: 600,
                marginBottom: '6px',
              }}
            >
              Category *
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as ApprovedInfoCategory)}
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                fontSize: 'var(--font-size-sm)',
                outline: 'none',
              }}
            >
              <option value="appointment_information">Appointment Information</option>
              <option value="clinic_logistics">Clinic Logistics</option>
              <option value="communication">Communication</option>
              <option value="program_information">Program Information</option>
              <option value="approved_education">Approved Education</option>
            </select>
          </div>

          <div>
            <label
              style={{
                display: 'block',
                fontSize: 'var(--font-size-xs)',
                fontWeight: 600,
                marginBottom: '6px',
              }}
            >
              Version
            </label>
            <input
              type="number"
              min={1}
              value={version}
              onChange={(e) => setVersion(parseInt(e.target.value) || 1)}
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                fontSize: 'var(--font-size-sm)',
                outline: 'none',
              }}
            />
          </div>
        </div>

        {/* Content */}
        <div>
          <label
            style={{
              display: 'block',
              fontSize: 'var(--font-size-xs)',
              fontWeight: 600,
              marginBottom: '6px',
            }}
          >
            Approved Content Body *
          </label>
          <textarea
            required
            rows={5}
            placeholder="Enter the official, vetted text that the AI agent is allowed to cite or synthesize..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              fontSize: 'var(--font-size-sm)',
              outline: 'none',
              resize: 'vertical',
            }}
          />
        </div>

        {/* Form Actions */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '8px' }}>
          <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" disabled={loading}>
            {loading ? 'Saving...' : 'Add Approved Information'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
