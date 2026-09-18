"""
CareFlow AI Agent Package.

Source of truth: docs/ai-agent-specification.md and docs/safety-privacy.md.
"""

from app.services.agent.orchestrator import process_client_message

__all__ = ["process_client_message"]
