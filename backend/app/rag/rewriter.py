"""Query Rewriter & Multi-Turn Conversational Expander.
Disambiguates conversational follow-up questions and expands domain acronyms
(SOP, RCA, CAPA, HVAC, SLA, GDP, GMP, QMS).
"""

import re

from pydantic import BaseModel

ACRONYM_MAP: dict[str, str] = {
    "sop": "standard operating procedure",
    "rca": "root cause analysis",
    "capa": "corrective and preventive action",
    "hvac": "heating ventilation and air conditioning",
    "sla": "service level agreement",
    "gdp": "good distribution practice",
    "gmp": "good manufacturing practice",
    "qms": "quality management system",
    "temp": "temperature",
    "pto": "paid time off",
    "bereavement": "compassionate leave",
}

PRONOUN_PATTERNS = [
    r"\bit\b",
    r"\bits\b",
    r"\bthis\b",
    r"\bthat\b",
    r"\bthese\b",
    r"\bthose\b",
    r"\bthe same\b",
    r"\bthe procedure\b",
    r"\bthe document\b",
]


class MessageContext(BaseModel):
    role: str
    content: str


class QueryRewriter:
    """Expands domain terminology and resolves multi-turn conversational references."""

    def __init__(self, acronym_map: dict[str, str] | None = None):
        self.acronym_map = acronym_map or ACRONYM_MAP

    def expand_acronyms(self, query: str) -> str:
        """Expands common domain acronyms while preserving original tokens."""
        tokens = query.split()
        expanded_parts = []
        for token in tokens:
            clean = re.sub(r"[^\w]", "", token).lower()
            if clean in self.acronym_map:
                expanded_parts.append(f"{token} ({self.acronym_map[clean]})")
            else:
                expanded_parts.append(token)
        return " ".join(expanded_parts)

    def rewrite_query(
        self, query: str, conversation_history: list[MessageContext] | None = None
    ) -> str:
        """Rewrites elliptical/pronoun-heavy queries using prior conversation context."""
        query_clean = query.strip()
        if not conversation_history:
            return query_clean

        # Check if query contains conversational references or is very short
        has_pronoun = any(re.search(pat, query_clean, re.IGNORECASE) for pat in PRONOUN_PATTERNS)
        is_short_followup = len(query_clean.split()) <= 4 and (
            query_clean.lower().startswith("what about")
            or query_clean.lower().startswith("how about")
            or query_clean.lower().startswith("and ")
            or query_clean.lower().startswith("who ")
        )

        if not (has_pronoun or is_short_followup):
            return query_clean

        # Extract context topic or document mentions from the latest messages
        recent_context = ""
        for msg in reversed(conversation_history[-4:]):
            content = msg.content
            # Look for document title mentions or key topics
            match = re.search(r"(\b(?:CLIN|SOP|HR|IT)-[A-Z0-9\-]+[:\s\w]+)", content)
            if match:
                recent_context = match.group(1).strip()
                break
            if msg.role == "user" and len(content.split()) >= 4:
                recent_context = content.strip()
                break

        if recent_context:
            # Append context to disambiguate the search
            rewritten = f"{query_clean} regarding {recent_context}"
            return rewritten

        return query_clean
