/**
 * CareFlow AI — TypeScript Domain Definitions
 * Strictly aligned with Phase 5 API & SQLAlchemy Schema Specifications.
 */

// --- Common API Envelopes ---
export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
}

export interface DataResponse<T> {
  data: T;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationMeta;
}

export interface ErrorDetail {
  code: string;
  message: string;
  details?: Record<string, unknown> | null;
}

export interface ErrorResponse {
  error: ErrorDetail;
}

// --- Health ---
export interface HealthData {
  status: 'ok' | 'degraded' | 'unavailable';
  database: 'ok' | 'unavailable';
  service: string;
  version: string;
}

// --- Client & Communication Preferences ---
export type EnrollmentStatus = 'active' | 'inactive' | 'completed' | 'withdrawn';
export type CommunicationChannel = 'web' | 'sms' | 'whatsapp' | 'email';

export interface Client {
  id: string;
  external_reference: string | null;
  preferred_name: string;
  preferred_language: string;
  enrollment_status: EnrollmentStatus;
  status: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ClientCreate {
  external_reference?: string;
  preferred_name: string;
  preferred_language?: string;
  status?: EnrollmentStatus;
  enrollment_status?: EnrollmentStatus;
  communication_channel?: CommunicationChannel;
  is_active?: boolean;
}

export interface ClientUpdate {
  external_reference?: string;
  preferred_name?: string;
  preferred_language?: string;
  status?: EnrollmentStatus;
  enrollment_status?: EnrollmentStatus;
  is_active?: boolean;
}

export interface CommunicationPreference {
  id: string;
  client_id: string;
  channel: CommunicationChannel;
  preferred_channel?: string;
  is_enabled: boolean;
  updated_at: string;
}

export interface CommunicationPreferenceCreate {
  channel?: CommunicationChannel;
  preferred_channel?: CommunicationChannel;
  is_enabled?: boolean;
}

// --- Appointments ---
export type AppointmentStatus = 'scheduled' | 'completed' | 'missed' | 'cancelled' | 'rescheduled';

export interface Appointment {
  id: string;
  client_id: string;
  appointment_type: string;
  scheduled_at: string;
  status: AppointmentStatus;
  location_label: string | null;
  created_at?: string;
}

export interface AppointmentCreate {
  client_id: string;
  appointment_type?: string;
  scheduled_at: string;
  status?: AppointmentStatus;
  location_label?: string;
}

export interface AppointmentUpdate {
  appointment_type?: string;
  scheduled_at?: string;
  status?: AppointmentStatus;
  location_label?: string;
}

// --- Interactions ---
export type InteractionDirection = 'incoming' | 'outgoing';
export type InteractionType =
  | 'message'
  | 'appointment_reminder'
  | 'follow_up'
  | 'staff_response'
  | 'ai_response'
  | 'system_event';

export type AIIntentCategory =
  | 'appointment_inquiry'
  | 'rescheduling'
  | 'clinic_info'
  | 'general_support'
  | 'clinical_concern'
  | 'emergency_escalation'
  | 'medication_concern'
  | 'unknown';

export interface Interaction {
  id: string;
  client_id: string;
  channel: CommunicationChannel;
  direction: InteractionDirection;
  interaction_type: InteractionType;
  intent_category: AIIntentCategory | null;
  message_reference: string | null;
  content: string | null;
  created_at: string;
}

export interface InteractionCreate {
  client_id: string;
  channel: CommunicationChannel;
  direction: InteractionDirection;
  interaction_type: InteractionType;
  intent_category?: AIIntentCategory;
  message_reference?: string;
  content?: string;
}

// --- Follow-up Tasks ---
export type FollowUpPriority = 'normal' | 'high' | 'urgent';
export type FollowUpStatus = 'pending' | 'assigned' | 'in_progress' | 'completed' | 'cancelled';

export interface FollowUpTask {
  id: string;
  client_id: string;
  assigned_to: string | null;
  reason: string;
  priority: FollowUpPriority;
  status: FollowUpStatus;
  due_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface FollowUpCreate {
  client_id: string;
  assigned_to?: string | null;
  reason: string;
  priority?: FollowUpPriority;
  status?: FollowUpStatus;
  due_at?: string | null;
}

export interface FollowUpUpdate {
  reason?: string;
  priority?: FollowUpPriority;
  status?: FollowUpStatus;
  assigned_to?: string | null;
  due_at?: string | null;
  completed_at?: string | null;
}

// --- Escalations ---
export type EscalationCategory =
  | 'clinical_concern'
  | 'medication_concern'
  | 'sensitive_concern'
  | 'human_request'
  | 'emergency_related'
  | 'unknown_intent'
  | 'ai_uncertainty'
  | 'system_failure';

export type EscalationStatus = 'open' | 'assigned' | 'in_review' | 'resolved' | 'cancelled';

export interface Escalation {
  id: string;
  client_id: string;
  assigned_to: string | null;
  category: EscalationCategory;
  priority: FollowUpPriority;
  reason: string;
  status: EscalationStatus;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface EscalationCreate {
  client_id: string;
  assigned_to?: string | null;
  category: EscalationCategory;
  priority?: FollowUpPriority;
  reason: string;
  status?: EscalationStatus;
}

export interface EscalationUpdate {
  category?: EscalationCategory;
  priority?: FollowUpPriority;
  reason?: string;
  status?: EscalationStatus;
  assigned_to?: string | null;
  resolved_at?: string | null;
}

// --- Approved Information ---
export type ApprovedInfoCategory =
  | 'appointment_information'
  | 'clinic_logistics'
  | 'communication'
  | 'program_information'
  | 'approved_education';

export interface ApprovedInformation {
  id: string;
  title: string;
  category: ApprovedInfoCategory;
  content: string;
  version: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ApprovedInformationCreate {
  title: string;
  category: ApprovedInfoCategory;
  content: string;
  version?: number;
  is_active?: boolean;
}

export interface ApprovedInformationUpdate {
  title?: string;
  category?: ApprovedInfoCategory;
  content?: string;
  version?: number;
  is_active?: boolean;
}

// --- Audit Logs ---
export interface AuditLog {
  id: string;
  user_id: string | null;
  action: string;
  entity_type: string;
  entity_id: string | null;
  metadata?: Record<string, unknown> | null;
  created_at: string;
}
