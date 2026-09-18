"""
CareFlow AI Multi-Layer Safety Guardrails.

Source of truth: docs/safety-privacy.md - Sections 15, 16, 17, 18, 23
and docs/ai-agent-specification.md - Sections 4, 34, 35.
"""

import re
import logging
from typing import Tuple, Optional

from app.services.agent.prompts import SAFE_CLINICAL_ACK, SAFE_MEDICATION_ACK

logger = logging.getLogger("careflow.agent.guardrails")

# ------------------------------------------------------------------------------
# 1. Emergency Detection Patterns
# ------------------------------------------------------------------------------
EMERGENCY_PATTERNS = [
    r"\bemergency\b",
    r"\bcall 911\b",
    r"\bcan'?t breathe\b",
    r"\bdifficulty breathing\b",
    r"\bshortness of breath\b",
    r"\bchest pain\b",
    r"\bheart attack\b",
    r"\bsuicid(e|al)\b",
    r"\bkill myself\b",
    r"\bend my life\b",
    r"\boverdose\b",
    r"\bbleeding heavily\b",
    r"\bunconscious\b",
    r"\bpassed out\b",
    r"\bseizure\b",
    r"\banaphylaxis\b",
    r"\bpoison(ing|ed)?\b",
]

# ------------------------------------------------------------------------------
# 2. Medication Concern Patterns
# ------------------------------------------------------------------------------
MEDICATION_PATTERNS = [
    r"\bstop (taking|my) (pills|meds|medication|treatment)\b",
    r"\bshould i stop\b",
    r"\bmissed (my )?(dose|pills|meds|medication)\b",
    r"\bskip(ped)? (my )?(dose|pills|meds|medication)\b",
    r"\bside effects?\b",
    r"\brash from (the )?(pills|meds|medication)\b",
    r"\bnausea from (the )?(pills|meds|medication)\b",
    r"\bvomit(ing)? (after|the) (pills|meds|medication)\b",
    r"\bchange (my )?(dose|dosage|medication|prescription|pills)\b",
    r"\bswitch (my )?(medication|pills|treatment)\b",
    r"\bdouble (my )?dose\b",
    r"\btake extra (pills|dose)\b",
    r"\bdose adjustment\b",
    r"\bdrug reaction\b",
]

# ------------------------------------------------------------------------------
# 3. Clinical Concern Patterns (Symptoms, Diagnosis, Interpretation)
# ------------------------------------------------------------------------------
CLINICAL_PATTERNS = [
    r"\bdiagnos(e|is|ed)\b",
    r"\bwhat (illness|disease|condition) do i have\b",
    r"\bprescribe\b",
    r"\bprescription\b",
    r"\bviral load (is|result|high|low|test)\b",
    r"\bcd4 (count|result|level)\b",
    r"\blab(oratory)? (test|results?)\b",
    r"\bblood (test|work) results?\b",
    r"\bswollen lymph\b",
    r"\bhigh fever\b",
    r"\bsevere pain\b",
    r"\binfection\b",
    r"\btreatment plan\b",
]

# ------------------------------------------------------------------------------
# 4. Prompt Injection / Adversarial Patterns
# ------------------------------------------------------------------------------
PROMPT_INJECTION_PATTERNS = [
    r"ignore (all )?(previous|above|system) instructions",
    r"disregard (all )?(previous|system|your)?\s*(safety\s*)?(rules|instructions)",
    r"you are now in (developer|dan|jailbreak|unrestricted) mode",
    r"pretend you are a doctor",
    r"act as a (physician|doctor|pharmacist|clinician)",
    r"reveal (your )?(initial |secret )?(system prompt|instructions)",
    r"output (your )?(initial )?(instructions|system prompt)",
    r"bypass (all )?safety rules",
    r"<script.*?>",
    r"drop table\b",
    r"delete from\b",
    r"union select\b",
]


# ------------------------------------------------------------------------------
# 5. Output Prescriptive Language Guardrail Patterns
# ------------------------------------------------------------------------------
UNSAFE_OUTPUT_PATTERNS = [
    r"\bi diagnose you with\b",
    r"\byou (are diagnosed with|have been diagnosed with)\b",
    r"\byou should (stop taking|discontinue)\b",
    r"\byou should (increase|decrease) your (dose|medication)\b",
    r"\bi prescribe\b",
    r"\byou need to take (amoxicillin|doxycycline|paracetamol|ibuprofen|antibiotics)\b",
    r"\byour (cd4|viral load) means that you\b",
]


def check_emergency(text: str) -> bool:
    """Detects immediate emergency or acute crisis cues."""
    lower_text = text.lower()
    for pattern in EMERGENCY_PATTERNS:
        if re.search(pattern, lower_text):
            logger.warning("Emergency signal matched pattern: %s", pattern)
            return True
    return False


def check_medication_concern(text: str) -> bool:
    """Detects medication changes, side effects, missed doses, or dosage queries."""
    lower_text = text.lower()
    for pattern in MEDICATION_PATTERNS:
        if re.search(pattern, lower_text):
            logger.info("Medication concern matched pattern: %s", pattern)
            return True
    return False


def check_clinical_concern(text: str) -> bool:
    """Detects symptom reporting, medical diagnosis, lab interpretation, or prescription requests."""
    lower_text = text.lower()
    for pattern in CLINICAL_PATTERNS:
        if re.search(pattern, lower_text):
            logger.info("Clinical concern matched pattern: %s", pattern)
            return True
    return False


def detect_prompt_injection(text: str) -> bool:
    """Detects attempts to manipulate, override, or extract system instructions."""
    lower_text = text.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, lower_text, re.IGNORECASE):
            logger.warning("Prompt injection attempt matched pattern: %s", pattern)
            return True
    return False


def sanitize_input(text: str) -> str:
    """
    Sanitizes client input text by removing null bytes, normalizing whitespace,
    and escaping artificial prompt delimiter tags.
    """
    cleaned = text.replace("\x00", "").strip()
    cleaned = cleaned.replace("<client_message>", "").replace("</client_message>", "")
    cleaned = cleaned.replace("<system>", "").replace("</system>", "")
    return cleaned


def validate_output_safety(output_text: str) -> Tuple[bool, str]:
    """
    Scans generated LLM output for accidental diagnostic or prescriptive advice.
    Returns (is_safe, sanitized_or_fallback_text).
    """
    lower_output = output_text.lower()
    for pattern in UNSAFE_OUTPUT_PATTERNS:
        if re.search(pattern, lower_output):
            logger.error(
                "Post-generation safety guardrail tripped on output pattern: %s. Replacing with safe fallback.",
                pattern,
            )
            return False, SAFE_CLINICAL_ACK
    return True, output_text
