"""
AI Agent Orchestration Service for CareFlow AI.

Source of truth: docs/ai-agent-specification.md - Sections 5, 19, 20, 31, 37, 43
and docs/api.md - Section 19.
"""

import logging
import uuid
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.enums import (
    AIIntentCategory,
    EscalationCategory,
    FollowUpPriority,
)
from app.schemas.message import (
    MessageProcessRequest,
    MessageProcessResponseData,
)
from app.services.agent.classifier import classify_message
from app.services.agent.guardrails import (
    sanitize_input,
    detect_prompt_injection,
    validate_output_safety,
)
from app.services.agent.prompts import (
    SAFE_CLINICAL_ACK,
    SAFE_MEDICATION_ACK,
    SAFE_EMERGENCY_ACK,
    SAFE_STAFF_REQUEST_ACK,
    SAFE_CLARIFICATION_ACK,
    SAFE_FALLBACK_ACK,
)
from app.services.agent.tools import (
    get_client_profile,
    get_appointment,
    get_approved_information,
    create_followup,
    create_escalation,
    record_interaction,
)
from app.services.audit import record_audit

logger = logging.getLogger("careflow.agent.orchestrator")


def process_client_message(
    db: Session,
    request: MessageProcessRequest,
) -> MessageProcessResponseData:
    """
    Core end-to-end processing pipeline for incoming client messages.
    Follows docs/ai-agent-specification.md:
    1. Validate client
    2. Sanitize input & detect injection
    3. Record incoming interaction
    4. Classify intent and barriers
    5. Execute controlled actions (Tools / Escalations / Follow-ups)
    6. Run post-generation output guardrails
    7. Record outgoing interaction & audit log
    8. Return standardized response
    """
    # Step 1: Validate client existence
    client = db.query(Client).filter(Client.id == request.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id '{request.client_id}' not found.",
        )

    # Step 2: Sanitize input & scan for prompt injection attempts
    raw_message = request.message
    cleaned_message = sanitize_input(raw_message)
    is_injection = detect_prompt_injection(raw_message)

    if is_injection:
        logger.warning(
            "Prompt injection attempt detected for client_id=%s. Neutralizing input.",
            request.client_id,
        )
        record_audit(
            db=db,
            action="prompt_injection_flagged",
            entity_type="client",
            entity_id=client.id,
            metadata={"channel": request.channel.value},
        )

    # Step 3: Record incoming client interaction
    incoming_interaction = record_interaction(
        db=db,
        client_id=client.id,
        channel=request.channel.value,
        direction="incoming",
        interaction_type="message",
        content=cleaned_message,
    )

    try:
        # Step 4: Classify intent and barriers
        intent, barrier = classify_message(cleaned_message)

        # Step 5: Decision Matrix routing
        escalated = False
        escalation_id: Optional[uuid.UUID] = None
        followup_id: Optional[uuid.UUID] = None
        response_text = ""

        if intent == AIIntentCategory.EMERGENCY_RELATED:
            esc = create_escalation(
                db=db,
                client_id=client.id,
                category=EscalationCategory.EMERGENCY_RELATED.value,
                priority="urgent",
                reason="Client message indicated acute medical emergency or distress.",
            )
            escalated = True
            escalation_id = esc.id
            response_text = SAFE_EMERGENCY_ACK

        elif intent == AIIntentCategory.MEDICATION_CONCERN:
            esc = create_escalation(
                db=db,
                client_id=client.id,
                category=EscalationCategory.MEDICATION_CONCERN.value,
                priority="high",
                reason="Client reported medication-related question, side effect, or dose concern.",
            )
            escalated = True
            escalation_id = esc.id
            response_text = SAFE_MEDICATION_ACK

        elif intent == AIIntentCategory.CLINICAL_CONCERN:
            esc = create_escalation(
                db=db,
                client_id=client.id,
                category=EscalationCategory.CLINICAL_CONCERN.value,
                priority="high",
                reason="Client reported medical symptoms, test result interpretation, or requested diagnosis.",
            )
            escalated = True
            escalation_id = esc.id
            response_text = SAFE_CLINICAL_ACK

        elif intent == AIIntentCategory.HUMAN_STAFF_REQUEST:
            esc = create_escalation(
                db=db,
                client_id=client.id,
                category=EscalationCategory.HUMAN_REQUEST.value,
                priority="normal",
                reason="Client explicitly requested human healthcare staff assistance.",
            )
            escalated = True
            escalation_id = esc.id
            response_text = SAFE_STAFF_REQUEST_ACK

        elif intent == AIIntentCategory.RESCHEDULING:
            task = create_followup(
                db=db,
                client_id=client.id,
                reason="Appointment rescheduling request",
                priority=FollowUpPriority.NORMAL.value,
            )
            followup_id = task.id
            appt = get_appointment(db, client.id)
            if appt:
                response_text = (
                    f"I understand you would like to reschedule your upcoming appointment scheduled for "
                    f"{appt['scheduled_at']}. A follow-up task has been assigned to the clinic team, "
                    f"and a staff member will contact you to coordinate a convenient date."
                )
            else:
                response_text = (
                    "I understand you would like to reschedule an appointment. I have submitted "
                    "a request to our clinic staff, and they will contact you to schedule a date."
                )

        elif intent == AIIntentCategory.BARRIER_TO_CARE:
            barrier_label = barrier.replace("_", " ") if barrier else "care engagement"
            priority = (
                FollowUpPriority.HIGH.value
                if barrier == "transportation"
                else FollowUpPriority.NORMAL.value
            )
            task = create_followup(
                db=db,
                client_id=client.id,
                reason=f"Reported barrier to care: {barrier_label}",
                priority=priority,
            )
            followup_id = task.id
            response_text = (
                f"Thank you for letting us know. We understand that {barrier_label} can make it "
                f"challenging to attend clinic appointments. I have recorded this with our support staff, "
                f"and a team member will reach out to discuss support options with you."
            )

        elif intent == AIIntentCategory.APPOINTMENT_ASSISTANCE:
            appt = get_appointment(db, client.id)
            client_name = client.preferred_name or "there"
            if appt:
                response_text = (
                    f"Hello {client_name}. Your {appt['appointment_type']} appointment is currently "
                    f"{appt['status']} for {appt['scheduled_at']} at {appt['location_label']}."
                )
            else:
                response_text = (
                    f"Hello {client_name}. You currently do not have an upcoming appointment scheduled in "
                    f"our records. Please contact the clinic if you would like to schedule a visit."
                )

        elif intent == AIIntentCategory.GENERAL_SUPPORT:
            approved = get_approved_information(db, category="clinic_logistics")
            if not approved:
                approved = get_approved_information(db)

            if approved:
                info_item = approved[0]
                response_text = f"{info_item['title']}: {info_item['content']}"
            else:
                response_text = (
                    "Our clinic staff is available to support your care engagement and answer "
                    "program questions. Please let us know how we can best assist you."
                )

        else:
            # UNKNOWN intent
            response_text = SAFE_CLARIFICATION_ACK

        # Step 6: Post-generation output guardrails
        is_safe, final_response = validate_output_safety(response_text)
        if not is_safe:
            escalated = True
            if not escalation_id:
                esc = create_escalation(
                    db=db,
                    client_id=client.id,
                    category=EscalationCategory.CLINICAL_CONCERN.value,
                    priority="high",
                    reason="Output guardrail intervened to prevent potential clinical advice.",
                )
                escalation_id = esc.id

        # Update incoming interaction classification
        incoming_interaction.intent_category = intent.value

        # Step 7: Record outgoing AI response interaction
        record_interaction(
            db=db,
            client_id=client.id,
            channel=request.channel.value,
            direction="outgoing",
            interaction_type="ai_response",
            intent_category=intent.value,
            content=final_response,
            message_reference=str(incoming_interaction.id),
        )

        # Step 8: Record audit event
        record_audit(
            db=db,
            action="ai_message_processed",
            entity_type="interaction",
            entity_id=incoming_interaction.id,
            metadata={
                "intent": intent.value,
                "escalated": escalated,
                "barrier": barrier,
            },
        )

        db.commit()

        return MessageProcessResponseData(
            interaction_id=incoming_interaction.id,
            intent=intent,
            response=final_response,
            escalated=escalated,
            escalation_id=escalation_id,
            followup_id=followup_id,
            barrier_detected=barrier,
        )

    except Exception as e:
        db.rollback()
        logger.error("Error processing message for client %s: %s", client.id, str(e))
        # Failsafe: Try to record minimal incoming interaction and audit in fresh transaction
        try:
            record_audit(
                db=db,
                action="ai_processing_failed",
                entity_type="client",
                entity_id=client.id,
                metadata={"error": str(e)},
            )
            db.commit()
        except Exception:
            db.rollback()

        return MessageProcessResponseData(
            interaction_id=incoming_interaction.id,
            intent=AIIntentCategory.UNKNOWN,
            response=SAFE_FALLBACK_ACK,
            escalated=False,
            escalation_id=None,
            followup_id=None,
            barrier_detected=None,
        )
