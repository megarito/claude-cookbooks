"""Chat message models for parsing exported conversation data."""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Single message from chat export (Claude, ChatGPT, etc.)"""

    message_id: str
    timestamp: datetime
    source: Literal["claude", "chatgpt", "other"]
    role: Literal["user", "assistant", "system"]
    content: str

    # Metadata from export
    export_week: str  # "2026-W01" format
    conversation_id: str
    model: str | None = None  # "claude-opus-4-5", "gpt-4", etc.

    # Extracted semantics
    mentioned_entities: list[str] = []  # People, places, conditions, events
    mentioned_dates: list[str] = []  # Date references in content
    mentioned_times: list[str] = []  # Time references
    incident_indicators: list[str] = []  # Keywords suggesting incidents

    # Confidence & classification
    is_incident_related: bool = False
    incident_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    sentiment: Literal["neutral", "concerning", "urgent", "routine"] = "neutral"


class ChatConversation(BaseModel):
    """Thread of related messages"""

    conversation_id: str
    messages: list[ChatMessage]

    # Temporal metadata
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    export_week: str

    # Semantic analysis
    primary_topic: str
    mentioned_entities: list[str]
    extracted_incidents: list[str]  # Incident IDs extracted from this convo

    # Cross-references
    related_schedule_events: list[str] = []  # Schedule event IDs
    related_notes: list[str] = []  # Note IDs
    related_research: list[str] = []  # Research document IDs


class WeeklyChatExport(BaseModel):
    """Week's worth of chat data"""

    week_id: str  # "2026-W01"
    start_date: datetime
    end_date: datetime
    source: Literal["claude", "chatgpt", "mixed"]

    conversations: list[ChatConversation]
    total_messages: int

    # Weekly summary
    incidents_mentioned: int
    entities_discussed: list[str]
    topics: list[str]

    # Quality metrics
    completeness: float = Field(ge=0.0, le=1.0)  # % of week covered
    parsing_errors: list[str] = []
