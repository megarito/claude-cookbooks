"""Parse weekly chat exports from Claude, ChatGPT, and other sources."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from research_evidence_ecosystem.models.chat_message import (
    ChatConversation,
    ChatMessage,
    WeeklyChatExport,
)


class WeeklyChatParser:
    """Parse weekly chat export files into structured format."""

    def parse_claude_export(self, export_path: str, week_id: str) -> WeeklyChatExport:
        """
        Parse Claude conversation export (JSON format).

        Expected format:
        {
            "conversations": [
                {
                    "id": "conv_123",
                    "created_at": "2026-01-01T10:00:00Z",
                    "messages": [
                        {
                            "id": "msg_456",
                            "role": "user",
                            "content": "I had a severe headache on Monday...",
                            "timestamp": "2026-01-01T10:00:00Z"
                        },
                        ...
                    ]
                }
            ]
        }
        """
        with open(export_path) as f:
            data = json.load(f)

        conversations = []
        for conv_data in data.get("conversations", []):
            messages = self._parse_claude_messages(conv_data, week_id)
            if messages:
                conversation = ChatConversation(
                    conversation_id=conv_data["id"],
                    messages=messages,
                    start_time=messages[0].timestamp,
                    end_time=messages[-1].timestamp,
                    duration_minutes=self._calculate_duration(messages),
                    export_week=week_id,
                    primary_topic=self._extract_topic(messages),
                    mentioned_entities=self._extract_entities(messages),
                    extracted_incidents=[],
                )
                conversations.append(conversation)

        return self._build_weekly_export(conversations, week_id, "claude")

    def parse_chatgpt_export(self, export_path: str, week_id: str) -> WeeklyChatExport:
        """
        Parse ChatGPT conversation export (conversations.json format).

        Expected format:
        [
            {
                "id": "conv_123",
                "create_time": 1704110400,
                "mapping": {
                    "msg_id": {
                        "message": {
                            "id": "msg_id",
                            "author": {"role": "user"},
                            "content": {"parts": ["Text here"]},
                            "create_time": 1704110400
                        }
                    }
                }
            }
        ]
        """
        with open(export_path) as f:
            data = json.load(f)

        conversations = []
        for conv_data in data:
            messages = self._parse_chatgpt_messages(conv_data, week_id)
            if messages:
                conversation = ChatConversation(
                    conversation_id=conv_data["id"],
                    messages=messages,
                    start_time=messages[0].timestamp,
                    end_time=messages[-1].timestamp,
                    duration_minutes=self._calculate_duration(messages),
                    export_week=week_id,
                    primary_topic=self._extract_topic(messages),
                    mentioned_entities=self._extract_entities(messages),
                    extracted_incidents=[],
                )
                conversations.append(conversation)

        return self._build_weekly_export(conversations, week_id, "chatgpt")

    def _parse_claude_messages(
        self, conv_data: dict[str, Any], week_id: str
    ) -> list[ChatMessage]:
        """Extract messages from Claude conversation."""
        messages = []
        for msg in conv_data.get("messages", []):
            # Basic incident detection via keywords
            content = msg.get("content", "")
            incident_keywords = self._detect_incident_keywords(content)

            message = ChatMessage(
                message_id=msg["id"],
                timestamp=datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00")),
                source="claude",
                role=msg["role"],
                content=content,
                export_week=week_id,
                conversation_id=conv_data["id"],
                model=conv_data.get("model"),
                incident_indicators=incident_keywords,
                is_incident_related=len(incident_keywords) > 0,
                incident_confidence=min(len(incident_keywords) * 0.2, 1.0),
            )
            messages.append(message)
        return messages

    def _parse_chatgpt_messages(
        self, conv_data: dict[str, Any], week_id: str
    ) -> list[ChatMessage]:
        """Extract messages from ChatGPT conversation mapping."""
        messages = []
        for node_id, node in conv_data.get("mapping", {}).items():
            if "message" not in node or not node["message"]:
                continue

            msg = node["message"]
            if not msg.get("content") or not msg["content"].get("parts"):
                continue

            content = " ".join(msg["content"]["parts"])
            incident_keywords = self._detect_incident_keywords(content)

            message = ChatMessage(
                message_id=msg["id"],
                timestamp=datetime.fromtimestamp(msg.get("create_time", 0)),
                source="chatgpt",
                role=msg["author"]["role"],
                content=content,
                export_week=week_id,
                conversation_id=conv_data["id"],
                incident_indicators=incident_keywords,
                is_incident_related=len(incident_keywords) > 0,
                incident_confidence=min(len(incident_keywords) * 0.2, 1.0),
            )
            messages.append(message)

        # Sort by timestamp
        messages.sort(key=lambda m: m.timestamp)
        return messages

    def _detect_incident_keywords(self, content: str) -> list[str]:
        """Detect keywords suggesting incident mentions."""
        # Medical incident indicators
        medical_keywords = [
            "pain",
            "symptom",
            "diagnosis",
            "emergency",
            "hospital",
            "injury",
            "fell",
            "accident",
            "medication",
            "treatment",
            "doctor",
            "appointment",
        ]

        # Legal incident indicators
        legal_keywords = [
            "incident",
            "accident",
            "violation",
            "breach",
            "complaint",
            "dispute",
            "filed",
            "lawsuit",
            "hearing",
            "testimony",
        ]

        # Temporal indicators (suggests event discussion)
        temporal_keywords = [
            "on monday",
            "last week",
            "yesterday",
            "that day",
            "when",
            "after",
            "before",
            "during",
        ]

        content_lower = content.lower()
        found_keywords = []

        for keyword in medical_keywords + legal_keywords + temporal_keywords:
            if keyword in content_lower:
                found_keywords.append(keyword)

        return found_keywords

    def _extract_topic(self, messages: list[ChatMessage]) -> str:
        """Extract primary topic from conversation (simplified)."""
        # In production, use LLM to summarize
        if not messages:
            return "unknown"

        # Use first user message as proxy
        user_messages = [m for m in messages if m.role == "user"]
        if user_messages:
            first_content = user_messages[0].content
            # Take first sentence or 100 chars
            topic = first_content.split(".")[0][:100]
            return topic

        return "conversation"

    def _extract_entities(self, messages: list[ChatMessage]) -> list[str]:
        """Extract mentioned entities (simplified - in production use NER)."""
        # Placeholder: collect unique capitalized words
        entities = set()
        for msg in messages:
            words = msg.content.split()
            for word in words:
                if word and word[0].isupper() and len(word) > 2:
                    entities.add(word)

        return list(entities)[:20]  # Limit to top 20

    def _calculate_duration(self, messages: list[ChatMessage]) -> int:
        """Calculate conversation duration in minutes."""
        if len(messages) < 2:
            return 0

        duration = (messages[-1].timestamp - messages[0].timestamp).total_seconds() / 60
        return int(duration)

    def _build_weekly_export(
        self, conversations: list[ChatConversation], week_id: str, source: str
    ) -> WeeklyChatExport:
        """Build weekly export summary."""
        if not conversations:
            # Return empty week
            return WeeklyChatExport(
                week_id=week_id,
                start_date=datetime.now(),
                end_date=datetime.now(),
                source=source,
                conversations=[],
                total_messages=0,
                incidents_mentioned=0,
                entities_discussed=[],
                topics=[],
                completeness=0.0,
            )

        all_entities = set()
        all_topics = []
        total_messages = 0
        incidents_count = 0

        for conv in conversations:
            all_entities.update(conv.mentioned_entities)
            all_topics.append(conv.primary_topic)
            total_messages += len(conv.messages)
            incidents_count += sum(1 for m in conv.messages if m.is_incident_related)

        return WeeklyChatExport(
            week_id=week_id,
            start_date=conversations[0].start_time,
            end_date=conversations[-1].end_time,
            source=source,
            conversations=conversations,
            total_messages=total_messages,
            incidents_mentioned=incidents_count,
            entities_discussed=list(all_entities)[:50],
            topics=all_topics,
            completeness=1.0,  # Assume complete for now
        )
