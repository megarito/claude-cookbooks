"""Schedule and calendar event models."""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class ScheduleEvent(BaseModel):
    """Calendar appointment or scheduled event"""

    event_id: str

    # Temporal data
    start_time: datetime
    end_time: datetime | None = None
    duration_minutes: int | None = None
    timezone: str = "UTC"

    # Event details
    title: str
    description: str | None = None
    location: str | None = None
    event_type: Literal[
        "appointment",
        "meeting",
        "procedure",
        "hearing",
        "deadline",
        "medication",
        "other",
    ] = "other"

    # Participants
    organizer: str | None = None
    attendees: list[str] = []

    # Integration
    source_calendar: str  # "google", "outlook", "ical", etc.
    source_file: str | None = None

    # Incident correlation
    related_incidents: list[str] = []  # Incident IDs mentioned in proximity
    related_chats: list[str] = []  # Conversations discussing this event
    related_notes: list[str] = []

    # Metadata
    is_recurring: bool = False
    recurrence_pattern: str | None = None
    status: Literal["confirmed", "tentative", "cancelled"] = "confirmed"


class ScheduleCorrelation(BaseModel):
    """Links schedule events to chat mentions and incidents"""

    correlation_id: str

    schedule_event_id: str
    chat_conversation_ids: list[str] = []
    incident_ids: list[str] = []

    # Temporal proximity
    time_difference_hours: float
    proximity_type: Literal[
        "before_event",  # Chat/incident before appointment
        "during_event",  # Concurrent
        "after_event",  # Chat/incident after appointment
        "follow_up",  # Days later, still related
    ]

    # Confidence
    correlation_confidence: float = Field(ge=0.0, le=1.0)
    correlation_basis: str  # Why we think these are related

    # Examples:
    # - "Chat mentioned appointment 2 days before"
    # - "Incident occurred during scheduled procedure"
    # - "Follow-up discussion 1 week after appointment"
