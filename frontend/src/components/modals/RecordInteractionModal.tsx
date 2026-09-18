import React, { useEffect, useState } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { createInteraction, listClients } from '../../api';
import {
  AIIntentCategory,
  Client,
  CommunicationChannel,
  InteractionDirection,
  InteractionType,
} from '../../types';

interface RecordInteractionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  defaultClientId?: string;
  initialClientId?: string;
}

export const RecordInteractionModal: React.FC<RecordInteractionModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  defaultClientId,
  initialClientId,
}) => {
  const targetClientId = defaultClientId || initialClientId || '';
  const [clients, setClients] = useState<Client[]>([]);
  const [selectedClientId, setSelectedClientId] = useState<string>(targetClientId);
  const [channel, setChannel] = useState<CommunicationChannel>('whatsapp');
  const [direction, setDirection] = useState<InteractionDirection>('incoming');
  const [type, setType] = useState<InteractionType>('message');
  const [intent, setIntent] = useState<AIIntentCategory>('general_support');
  const [content, setContent] = useState('');
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
  }, [isOpen, defaultClientId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedClientId) {
      setError('Please select a client.');
      return;
    }
    if (!content.trim()) {
      setError('Message content is required.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await createInteraction({
        client_id: selectedClientId,
        channel: channel,
        direction: direction,
        interaction_type: type,
        intent_category: intent,
        content: content.trim(),
      });

      setContent('');
      onSuccess();
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to record interaction.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Record Communication Interaction"
      subtitle="Log an inbound message, outbound reminder, or client outreach interaction."
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
            <label className="form-label" htmlFor="int-client">
              Client *
            </label>
            <select
              id="int-client"
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
            <label className="form-label" htmlFor="int-channel">
              Channel *
            </label>
            <select
              id="int-channel"
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

          <div className="form-group">
            <label className="form-label" htmlFor="int-direction">
              Direction *
            </label>
            <select
              id="int-direction"
              className="form-select"
              value={direction}
              onChange={(e) => setDirection(e.target.value as InteractionDirection)}
            >
              <option value="incoming">Incoming (From Client)</option>
              <option value="outgoing">Outgoing (To Client)</option>
            </select>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div className="form-group">
            <label className="form-label" htmlFor="int-type">
              Interaction Type *
            </label>
            <select
              id="int-type"
              className="form-select"
              value={type}
              onChange={(e) => setType(e.target.value as InteractionType)}
            >
              <option value="message">Direct Message</option>
              <option value="appointment_reminder">Appointment Reminder</option>
              <option value="follow_up">Retention Follow-up</option>
              <option value="staff_response">Staff Manual Response</option>
              <option value="ai_response">AI Assisted Response</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="int-intent">
              AI Classified Intent
            </label>
            <select
              id="int-intent"
              className="form-select"
              value={intent}
              onChange={(e) => setIntent(e.target.value as AIIntentCategory)}
            >
              <option value="rescheduling">Appointment Rescheduling</option>
              <option value="appointment_inquiry">Appointment Inquiry</option>
              <option value="clinic_info">Clinic Logistics</option>
              <option value="general_support">General Support</option>
              <option value="clinical_concern">Clinical Question</option>
              <option value="medication_concern">Medication Concern</option>
              <option value="emergency_escalation">Emergency Concern</option>
              <option value="unknown">Unclassified</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="int-content">
            Message Content *
          </label>
          <textarea
            id="int-content"
            className="form-textarea"
            placeholder="Enter the message text or communication summary..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '24px' }}>
          <Button type="button" variant="secondary" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" loading={loading}>
            Save Interaction
          </Button>
        </div>
      </form>
    </Modal>
  );
};
