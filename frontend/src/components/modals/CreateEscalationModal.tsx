import React, { useEffect, useState } from 'react';
import { AlertTriangle, ShieldCheck } from 'lucide-react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { createEscalation, listClients } from '../../api';
import { Client, EscalationCategory, FollowUpPriority } from '../../types';

interface CreateEscalationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  defaultClientId?: string;
  initialClientId?: string;
}

export const CreateEscalationModal: React.FC<CreateEscalationModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  defaultClientId,
  initialClientId,
}) => {
  const targetClientId = defaultClientId || initialClientId || '';
  const [clients, setClients] = useState<Client[]>([]);
  const [selectedClientId, setSelectedClientId] = useState<string>(targetClientId);
  const [category, setCategory] = useState<EscalationCategory>('clinical_concern');
  const [priority, setPriority] = useState<FollowUpPriority>('urgent');
  const [reason, setReason] = useState('');
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
  }, [isOpen, defaultClientId, initialClientId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedClientId) {
      setError('Please select a client.');
      return;
    }
    if (!reason.trim()) {
      setError('Please provide escalation details.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await createEscalation({
        client_id: selectedClientId,
        category: category,
        priority: priority,
        reason: reason.trim(),
        status: 'open',
      });

      setReason('');
      onSuccess();
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to create escalation.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create Clinical / Support Escalation"
      subtitle="Routes complex or sensitive client situations directly to qualified staff."
    >
      <form onSubmit={handleSubmit}>
        {/* Human Oversight Advisory */}
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: '10px',
            padding: '12px 14px',
            backgroundColor: 'var(--status-warning-bg)',
            border: '1px solid var(--status-warning-border)',
            borderRadius: 'var(--radius-md)',
            marginBottom: '16px',
            fontSize: 'var(--font-size-xs)',
            color: '#78350f',
            lineHeight: 1.4,
          }}
        >
          <AlertTriangle size={18} style={{ color: 'var(--status-warning)', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong>Requires Human Staff Review:</strong>
            <p style={{ marginTop: '2px' }}>
              CareFlow AI does not autonomously diagnose, prescribe, or alter medication. Escalations alert clinical or care coordination team members to intervene.
            </p>
          </div>
        </div>

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
            <label className="form-label" htmlFor="esc-client">
              Client *
            </label>
            <select
              id="esc-client"
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

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div className="form-group">
            <label className="form-label" htmlFor="esc-category">
              Concern Category *
            </label>
            <select
              id="esc-category"
              className="form-select"
              value={category}
              onChange={(e) => setCategory(e.target.value as EscalationCategory)}
            >
              <option value="clinical_concern">Clinical Concern</option>
              <option value="medication_concern">Medication Concern</option>
              <option value="sensitive_concern">Sensitive / Stigma Concern</option>
              <option value="human_request">Client Requested Human Staff</option>
              <option value="emergency_related">Emergency / Acute Care</option>
              <option value="ai_uncertainty">AI Ambiguity / Uncertainty</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="esc-priority">
              Triage Priority *
            </label>
            <select
              id="esc-priority"
              className="form-select"
              value={priority}
              onChange={(e) => setPriority(e.target.value as FollowUpPriority)}
            >
              <option value="urgent">Urgent (Immediate Review)</option>
              <option value="high">High Priority</option>
              <option value="normal">Normal Review</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="esc-reason">
            Escalation Reason & Notes *
          </label>
          <textarea
            id="esc-reason"
            className="form-textarea"
            placeholder="Describe the clinical question, medication side-effect report, or client need requiring human review..."
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            required
          />
          <span className="form-hint">
            Summarize the situation objectively without including unnecessary identifiable records.
          </span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '24px' }}>
          <Button type="button" variant="secondary" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="danger"
            loading={loading}
            icon={<ShieldCheck size={16} />}
          >
            Submit for Staff Review
          </Button>
        </div>
      </form>
    </Modal>
  );
};
