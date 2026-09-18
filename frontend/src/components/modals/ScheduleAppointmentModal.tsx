import React, { useEffect, useState } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { createAppointment, listClients } from '../../api';
import { AppointmentStatus, Client } from '../../types';

interface ScheduleAppointmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  defaultClientId?: string;
  initialClientId?: string;
}

export const ScheduleAppointmentModal: React.FC<ScheduleAppointmentModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  defaultClientId,
  initialClientId,
}) => {
  const targetClientId = defaultClientId || initialClientId || '';
  const [clients, setClients] = useState<Client[]>([]);
  const [selectedClientId, setSelectedClientId] = useState<string>(targetClientId);
  const [appointmentType, setAppointmentType] = useState('clinical_review');
  const [scheduledDate, setScheduledDate] = useState('');
  const [scheduledTime, setScheduledTime] = useState('10:00');
  const [locationLabel, setLocationLabel] = useState('Main Clinic Suite 102');
  const [status, setStatus] = useState<AppointmentStatus>('scheduled');
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

    // Default to tomorrow's date
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateStr = tomorrow.toISOString().split('T')[0];
    setScheduledDate(dateStr);
  }, [isOpen, defaultClientId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedClientId) {
      setError('Please select a client.');
      return;
    }
    if (!scheduledDate || !scheduledTime) {
      setError('Please provide date and time.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const scheduledAtIso = new Date(`${scheduledDate}T${scheduledTime}:00Z`).toISOString();

      await createAppointment({
        client_id: selectedClientId,
        appointment_type: appointmentType,
        scheduled_at: scheduledAtIso,
        status: status,
        location_label: locationLabel || undefined,
      });

      onSuccess();
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to schedule appointment.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Schedule Appointment"
      subtitle="Book a clinic consultation, lab review, or medication pickup."
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
            <label className="form-label" htmlFor="appt-client">
              Client *
            </label>
            <select
              id="appt-client"
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
          <label className="form-label" htmlFor="appt-type">
            Appointment Type *
          </label>
          <select
            id="appt-type"
            className="form-select"
            value={appointmentType}
            onChange={(e) => setAppointmentType(e.target.value)}
          >
            <option value="clinical_review">Clinical Review</option>
            <option value="medication_pickup">Medication Refill / Pickup</option>
            <option value="lab_consultation">Laboratory Follow-up</option>
            <option value="peer_counseling">Peer Adherence Counseling</option>
            <option value="routine_checkup">Routine Care Checkup</option>
          </select>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div className="form-group">
            <label className="form-label" htmlFor="appt-date">
              Scheduled Date *
            </label>
            <input
              id="appt-date"
              type="date"
              className="form-input"
              value={scheduledDate}
              onChange={(e) => setScheduledDate(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="appt-time">
              Scheduled Time *
            </label>
            <input
              id="appt-time"
              type="time"
              className="form-input"
              value={scheduledTime}
              onChange={(e) => setScheduledTime(e.target.value)}
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="appt-location">
            Location Label
          </label>
          <input
            id="appt-location"
            type="text"
            className="form-input"
            placeholder="e.g. Community Health Center — Room 102"
            value={locationLabel}
            onChange={(e) => setLocationLabel(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="appt-status">
            Initial Status
          </label>
          <select
            id="appt-status"
            className="form-select"
            value={status}
            onChange={(e) => setStatus(e.target.value as AppointmentStatus)}
          >
            <option value="scheduled">Scheduled</option>
            <option value="rescheduled">Rescheduled</option>
          </select>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '24px' }}>
          <Button type="button" variant="secondary" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" loading={loading}>
            Schedule Appointment
          </Button>
        </div>
      </form>
    </Modal>
  );
};
