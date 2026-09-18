"""
Messages API Endpoint for CareFlow AI.

Source of truth: docs/api.md - Section 19 and docs/ai-agent-specification.md.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.message import MessageProcessRequest, MessageProcessResponse
from app.services.agent.orchestrator import process_client_message

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post(
    "",
    response_model=MessageProcessResponse,
    status_code=status.HTTP_200_OK,
    summary="Process incoming client message through AI agent",
    description=(
        "Primary entry point for AI-assisted patient engagement. "
        "Classifies client intent, applies strict non-clinical safety guardrails, "
        "coordinates tool execution, manages human escalation when appropriate, "
        "and logs an auditable interaction trail."
    ),
)
def process_message(
    payload: MessageProcessRequest,
    db: Session = Depends(get_db),
) -> MessageProcessResponse:
    """
    Receives and processes an incoming client message.
    """
    result = process_client_message(db=db, request=payload)
    return MessageProcessResponse(data=result)
