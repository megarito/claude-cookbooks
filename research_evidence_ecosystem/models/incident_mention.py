"""Incident extraction models for timeline reconstruction."""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class IncidentMention(BaseModel):
    """Single mention of an incident extracted from chat/notes/schedule"""

    mention_id: str
    incident_id: str  # Multiple mentions may refer to same incident

    # Source attribution
    source_type: Literal["chat", "schedule", "note", "research", "document"]
    source_id: str  # Conversation ID, event ID, note ID, etc.
    source_timestamp: datetime

    # Incident details from this mention
    mentioned_date: datetime | str | None = None  # When incident occurred
    date_precision: Literal["exact", "approximate", "relative", "unknown"] = "unknown"
    description: str
    incident_type: str | None = None  # "symptom", "appointment", "accident", "filing", etc.

    # Context
    excerpt: str  # Relevant text snippet
    surrounding_context: str | None = None
    mentioned_entities: list[str] = []

    # Confidence & verification
    confidence: float = Field(ge=0.0, le=1.0)
    is_firsthand: bool = False  # True if from person involved
    verification_status: Literal["unverified", "corroborated", "verified", "disputed"] = (
        "unverified"
    )

    # Conflicts
    conflicts_with: list[str] = []  # Other mention IDs with different details


class IncidentReconstruction(BaseModel):
    """Complete incident built from multiple mentions"""

    incident_id: str

    # Core incident details
    incident_type: str
    description: str
    occurred_date: datetime | str
    date_precision: Literal["exact", "approximate", "range"]

    # All mentions contributing to this incident
    mentions: list[IncidentMention]
    primary_mention_id: str  # Most authoritative/complete mention

    # Synthesis
    entities_involved: list[str]
    location: str | None = None
    outcome: str | None = None

    # Timeline integration
    timeline_event_id: str | None = None
    preceding_events: list[str] = []  # Other incident IDs
    following_events: list[str] = []

    # Verification
    overall_confidence: float = Field(ge=0.0, le=1.0)
    corroboration_count: int = 0  # How many sources mention this
    conflicts: list[dict[str, str]] = []  # Conflicting details

    # Evidence
    supporting_documents: list[str] = []
    related_schedule_events: list[str] = []
    related_research: list[str] = []


class TemporalCluster(BaseModel):
    """Group of related events occurring in same time window"""

    cluster_id: str
    time_window_start: datetime
    time_window_end: datetime

    # Events in this cluster
    incidents: list[str]  # Incident IDs
    schedule_events: list[str]  # Schedule event IDs
    chat_conversations: list[str]  # Conversation IDs
    notes: list[str]  # Note IDs

    # Analysis
    cluster_type: Literal["routine", "critical", "investigative", "follow_up"]
    primary_narrative: str  # What happened during this period
    key_entities: list[str]

    # Causality
    likely_causes: list[str] = []  # Earlier incident IDs
    likely_effects: list[str] = []  # Later incident IDs
