"""Prompt Injection, Delimiter Sanitization & Input Guardrails.
Defends KnowFlow AI against jailbreaks, system prompt exfiltration,
and context boundary manipulation.
"""

import re

from pydantic import BaseModel


class InjectionDetectionResult(BaseModel):
    is_safe: bool
    sanitized_text: str
    flagged_patterns: list[str]
    threat_level: str  # "NONE", "LOW", "MEDIUM", "HIGH"


# Adversarial jailbreak and instruction override patterns
INJECTION_PATTERNS = [
    (r"(?i)\bignore\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions|directions|prompts)\b", "HIGH", "INSTRUCTION_OVERRIDE"),
    (r"(?i)\bdisregard\s+(?:all\s+)?(?:previous|prior|above)\s+(?:rules|constraints|instructions)\b", "HIGH", "INSTRUCTION_OVERRIDE"),
    (r"(?i)\breveal\s+(?:the\s+|your\s+)?(?:system\s+prompt|developer\s+mode|internal\s+instructions)\b", "HIGH", "SYSTEM_PROMPT_EXFILTRATION"),
    (r"(?i)\bwhat\s+(?:is|are)\s+your\s+(?:exact\s+)?(?:system\s+prompt|initial\s+instructions)\b", "MEDIUM", "SYSTEM_PROMPT_EXFILTRATION"),
    (r"(?i)<\s*(?:system|admin|developer|instruction)\s*>", "HIGH", "TAG_INJECTION"),
    (r"(?i)```\s*(?:system|admin|instruction)", "HIGH", "CODEBLOCK_INJECTION"),
    (r"(?i)\bDAN\s+mode\b|\bdo\s+anything\s+now\b", "HIGH", "JAILBREAK_ROLEPLAY"),
    (r"(?i)\byou\s+are\s+now\s+in\s+developer\s+mode\b", "HIGH", "JAILBREAK_ROLEPLAY"),
    (r"(?i)\bpretend\s+(?:you\s+have\s+no\s+rules|you\s+are\s+unrestricted)\b", "HIGH", "JAILBREAK_ROLEPLAY"),
    (r"(?i)\bbypass\s+(?:grounding|verification|sop)\b", "MEDIUM", "POLICY_BYPASS"),
]


class PromptInjectionGuard:
    """Multi-layer input sanitization and prompt injection defense."""

    def __init__(self, canary_token: str = "CANARY_KF_PROMPT_GUARD_9918"):
        self.canary_token = canary_token

    def sanitize_input(self, text: str) -> str:
        """Strips non-printable control characters, zero-width characters,
        and neutralizes dangerous XML/markdown tags.
        """
        if not text:
            return ""

        # Remove zero-width characters and invisible unicode
        cleaned = re.sub(r"[\u200B-\u200D\uFEFF\u00A0]", " ", text)

        # Remove non-printable ASCII control codes (except newline, tab, carriage return)
        cleaned = "".join(ch for ch in cleaned if ch in "\n\r\t" or (32 <= ord(ch) <= 126) or ord(ch) > 127)

        # Neutralize XML tags like <system>, <admin>, </system>
        cleaned = re.sub(r"<\s*/?\s*(system|admin|developer|context|instruction)[^>]*>", "[FILTERED_TAG]", cleaned, flags=re.IGNORECASE)

        return cleaned.strip()

    def inspect_query(self, query: str) -> InjectionDetectionResult:
        """Inspects query text against known injection patterns and returns threat status."""
        flagged: list[str] = []
        highest_threat = "NONE"

        # Check raw query for delimiters, tags, and instruction overrides
        for pattern, threat, rule_name in INJECTION_PATTERNS:
            if re.search(pattern, query):
                flagged.append(f"{rule_name}:{threat}")
                if threat == "HIGH":
                    highest_threat = "HIGH"
                elif threat == "MEDIUM" and highest_threat != "HIGH":
                    highest_threat = "MEDIUM"
                elif threat == "LOW" and highest_threat == "NONE":
                    highest_threat = "LOW"

        sanitized = self.sanitize_input(query)

        is_safe = highest_threat != "HIGH"
        return InjectionDetectionResult(
            is_safe=is_safe,
            sanitized_text=sanitized,
            flagged_patterns=flagged,
            threat_level=highest_threat,
        )

    def isolate_chunk_context(self, chunk_id: str, title: str, section: str, page: int, text: str) -> str:
        """Wraps retrieved chunk text inside strict XML boundary tags with explicit instruction
        that context contents cannot alter the system prompt.
        """
        # Neutralize any attempts by documents to fake end-tags
        safe_text = re.sub(r"<\s*/\s*verified_document_chunk\s*>", "[TAG_ESCAPED]", text, flags=re.IGNORECASE)

        return (
            f'<verified_document_chunk id="{chunk_id}" document="{title}" section="{section}" page="{page}">\n'
            f"{safe_text}\n"
            f"</verified_document_chunk>"
        )

    def scan_output_for_canary(self, output: str) -> bool:
        """Returns True if output does NOT contain the canary token (safe).
        Returns False if canary leaked into output (alert!).
        """
        return self.canary_token not in output
