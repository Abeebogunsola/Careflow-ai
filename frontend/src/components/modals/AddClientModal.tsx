import React, { useState } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { createClient } from '../../api';
import { CommunicationChannel, EnrollmentStatus } from '../../types';

interface AddClientModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const AddClientModal: React.FC<AddClientModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [preferredName, setPreferredName] = useState('');
  const [externalReference, setExternalReference] = useState('');
  const [preferredLanguage, setPreferredLanguage] = useState('en');
  const [channel, setChannel] = useState<CommunicationChannel>('whatsapp');
  const [status, setStatus] = useState<EnrollmentStatus>('active');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!preferredName.trim()) {
      setError('Preferred name or pseudonym is required.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await createClient({
        preferred_name: preferredName.trim(),
        external_reference: externalReference.trim() || undefined,
        preferred_language: preferredLanguage,
        communication_channel: channel,
        enrollment_status: status,
        status: status,
      });

      setPreferredName('');
      setExternalReference('');
      onSuccess();
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to create client.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Add New Client"
      subtitle="Register a client for care retention and communication outreach."
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

        <div className="form-group">
          <label className="form-label" htmlFor="preferred-name">
            Preferred Name or Pseudonym *
          </label>
          <input
            id="preferred-name"
            type="text"
            className="form-input"
            placeholder="e.g. Alex T. or Morgan R."
            value={preferredName}
            onChange={(e) => setPreferredName(e.target.value)}
            required
          />
          <span className="form-hint">
            Use pseudonyms or preferred first names to preserve privacy. Never use full legal names.
          </span>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="ext-ref">
            Synthetic Reference Identifier
          </label>
          <input
            id="ext-ref"
            type="text"
            className="form-input"
            placeholder="e.g. SYNTH-PAT-0042"
            value={externalReference}
            onChange={(e) => setExternalReference(e.target.value)}
          />
          <span className="form-hint">
            Optional synthetic reference ID for cross-referencing demo clinic databases.
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div className="form-group">
            <label className="form-label" htmlFor="preferred-lang">
              Preferred Language
            </label>
            <select
              id="preferred-lang"
              className="form-select"
              value={preferredLanguage}
              onChange={(e) => setPreferredLanguage(e.target.value)}
            >
              <option value="en">English</option>
              <option value="es">Spanish (Español)</option>
              <option value="fr">French (Français)</option>
              <option value="pt">Portuguese (Português)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="preferred-channel">
              Outreach Channel
            </label>
            <select
              id="preferred-channel"
              className="form-select"
              value={channel}
              onChange={(e) => setChannel(e.target.value as CommunicationChannel)}
            >
              <option value="whatsapp">WhatsApp</option>
              <option value="sms">SMS</option>
              <option value="web">Web Portal</option>
              <option value="email">Email</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="enrollment-status">
            Enrollment Status
          </label>
          <select
            id="enrollment-status"
            className="form-select"
            value={status}
            onChange={(e) => setStatus(e.target.value as EnrollmentStatus)}
          >
            <option value="active">Active (Receiving Outreach)</option>
            <option value="inactive">Inactive (Paused)</option>
            <option value="completed">Completed Program</option>
            <option value="withdrawn">Withdrawn</option>
          </select>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '24px' }}>
          <Button type="button" variant="secondary" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" loading={loading}>
            Save Client
          </Button>
        </div>
      </form>
    </Modal>
  );
};
