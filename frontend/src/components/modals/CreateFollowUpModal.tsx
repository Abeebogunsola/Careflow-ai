import React, { useEffect, useState } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { createFollowUp, listClients } from '../../api';
import { Client, FollowUpPriority } from '../../types';

interface CreateFollowUpModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  defaultClientId?: string;
  initialClientId?: string;
}

export const CreateFollowUpModal: React.FC<CreateFollowUpModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  defaultClientId,
  initialClientId,
}) => {
  const targetClientId = defaultClientId || initialClientId || '';
  const [clients, setClients] = useState<Client[]>([]);
  const [selectedClientId, setSelectedClientId] = useState<string>(targetClientId);
  const [reason, setReason] = useState('Missed appointment outreach');
  const [priority, setPriority] = useState<FollowUpPriority>('normal');
  const [dueDate, setDueDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && !targetClientId) {
      listClients({ page_size: 50 }).then((res) => {
        setClients(res.data);
        if (res.data.length > 0 && !selectedClientId) {
          setSelectedClientId(res.data[0].id);
        }
      });
    } else if (targetClientId) {
      setSelectedClientId(targetClientId);
    }

    const nextDay = new Date();
    nextDay.setDate(nextDay.getDate() + 2);
    setDueDate(nextDay.toISOString().split('T')[0]);
  }, [isOpen, defaultClientId, initialClientId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedClientId) {
      setError('Please select a client.');
      return;
    }
    if (!reason.trim()) {
      setError('Please provide a reason.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const dueAtIso = dueDate ? new Date(`${dueDate}T17:00:00Z`).toISOString() : null;

      await createFollowUp({
        client_id: selectedClientId,
        reason: reason.trim(),
        priority: priority,
        status: 'pending',
        due_at: dueAtIso,
      });

      onSuccess();
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to create follow-up task.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create Follow-Up Task"
      subtitle="Assign an outreach task to care navigation or clinic retention staff."
    >
      <form onSubmit={handleSubmit}>
        {error && (
          <div
            style={{
              padding: '10px 14px',
              backgroundColor: 'var(--status-danger-bg)',
              color: 'var(--status-danger)',
              border: '1px solid var(--status-danger-border)',
              borderRadius: 'var(--radius-md)',
              fontSize: 'var(--font-size-xs)',
              marginBottom: '16px',
            }}
          >
            {error}
          </div>
        )}

        {!defaultClientId && (
          <div className="form-group">
            <label className="form-label" htmlFor="task-client">
              Client *
            </label>
            <select
              id="task-client"
              className="form-select"
              value={selectedClientId}
              onChange={(e) => setSelectedClientId(e.target.value)}
              required
            >
              {clients.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.preferred_name} {c.external_reference ? `(${c.external_reference})` : ''}
                </option>
              ))}
            </select>
          </div>
        )}

        <div className="form-group">
          <label className="form-label" htmlFor="task-reason">
            Task Reason *
          </label>
          <input
            id="task-reason"
            type="text"
            className="form-input"
            placeholder="e.g. Missed appointment outreach or Transportation check-in"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            required
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div className="form-group">
            <label className="form-label" htmlFor="task-priority">
              Priority
            </label>
            <select
              id="task-priority"
              className="form-select"
              value={priority}
              onChange={(e) => setPriority(e.target.value as FollowUpPriority)}
            >
              <option value="normal">Normal</option>
              <option value="high">High Priority</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="task-duedate">
              Due Date
            </label>
            <input
              id="task-duedate"
              type="date"
              className="form-input"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
            />
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '24px' }}>
          <Button type="button" variant="secondary" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" loading={loading}>
            Create Task
          </Button>
        </div>
      </form>
    </Modal>
  );
};
