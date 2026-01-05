"""Extract incident mentions from chat conversations using Claude."""

import os
from typing import Any

from anthropic import Anthropic

from research_evidence_ecosystem.models.chat_message import ChatConversation, ChatMessage
from research_evidence_ecosystem.models.incident_mention import (
    IncidentMention,
    IncidentReconstruction,
)


class IncidentExtractor:
    """Use Claude to extract structured incident mentions from chat data."""

    def __init__(self, api_key: str | None = None):
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    async def extract_incidents_from_conversation(
        self, conversation: ChatConversation, domain: str = "general"
    ) -> list[IncidentMention]:
        """
        Extract all incident mentions from a conversation.

        Args:
            conversation: Parsed chat conversation
            domain: "medical" or "legal" for specialized extraction
        """
        # Prepare conversation text
        conv_text = self._format_conversation(conversation)

        # Domain-specific prompts
        domain_instructions = self._get_domain_instructions(domain)

        prompt = f"""You are analyzing a chat conversation to extract mentions of real-world incidents or events.

{domain_instructions}

Conversation:
{conv_text}

Extract ALL mentions of incidents, events, or occurrences. For each mention, identify:
1. What happened (description)
2. When it happened (if mentioned - extract any date/time references)
3. Who was involved (entities)
4. Whether this is firsthand information or secondhand
5. Confidence level (0.0-1.0)

Return a JSON array of incidents. Use this schema:
{{
    "incidents": [
        {{
            "description": "brief description",
            "mentioned_date": "ISO date if available, or relative like 'last Monday', or null",
            "date_precision": "exact|approximate|relative|unknown",
            "incident_type": "symptom|appointment|accident|filing|etc",
            "excerpt": "exact quote from conversation",
            "mentioned_entities": ["entity1", "entity2"],
            "confidence": 0.8,
            "is_firsthand": true
        }}
    ]
}}

If no incidents are mentioned, return {{"incidents": []}}.
"""

        # Call Claude with structured output
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        # Parse response
        import json

        result_text = response.content[0].text

        # Extract JSON from markdown code blocks if present
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()

        result = json.loads(result_text)

        # Convert to IncidentMention objects
        mentions = []
        for idx, incident_data in enumerate(result.get("incidents", [])):
            mention = IncidentMention(
                mention_id=f"{conversation.conversation_id}_mention_{idx}",
                incident_id=f"incident_{hash(incident_data['description'][:50])}",  # Temp ID
                source_type="chat",
                source_id=conversation.conversation_id,
                source_timestamp=conversation.start_time,
                mentioned_date=incident_data.get("mentioned_date"),
                date_precision=incident_data.get("date_precision", "unknown"),
                description=incident_data["description"],
                incident_type=incident_data.get("incident_type"),
                excerpt=incident_data.get("excerpt", ""),
                mentioned_entities=incident_data.get("mentioned_entities", []),
                confidence=incident_data.get("confidence", 0.5),
                is_firsthand=incident_data.get("is_firsthand", False),
            )
            mentions.append(mention)

        return mentions

    def _format_conversation(self, conversation: ChatConversation) -> str:
        """Format conversation for Claude analysis."""
        lines = []
        for msg in conversation.messages:
            role = msg.role.upper()
            timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M")
            lines.append(f"[{timestamp}] {role}: {msg.content}")

        return "\n".join(lines)

    def _get_domain_instructions(self, domain: str) -> str:
        """Get domain-specific extraction instructions."""
        if domain == "medical":
            return """MEDICAL DOMAIN: Look for:
- Symptoms (pain, discomfort, changes in condition)
- Medical appointments (doctor visits, procedures, tests)
- Medication events (started, stopped, side effects)
- Injuries or accidents
- Diagnoses received
- Hospital/ER visits
- Changes in treatment
"""
        elif domain == "legal":
            return """LEGAL DOMAIN: Look for:
- Incidents or accidents
- Contract signings or breaches
- Legal filings or deadlines
- Court hearings or depositions
- Disputes or complaints
- Violations or citations
- Witness statements
- Evidence discovery
"""
        else:
            return """GENERAL: Look for any significant events, incidents, or occurrences mentioned in the conversation."""

    def cluster_incidents(self, mentions: list[IncidentMention]) -> list[IncidentReconstruction]:
        """
        Group related mentions into unified incidents.

        Uses similarity in description, date, and entities to identify
        multiple mentions of the same incident.
        """
        # Simplified clustering - in production use embeddings or LLM
        clusters: dict[str, list[IncidentMention]] = {}

        for mention in mentions:
            # Try to match to existing cluster
            matched = False
            for cluster_id, cluster_mentions in clusters.items():
                if self._mentions_match(mention, cluster_mentions[0]):
                    clusters[cluster_id].append(mention)
                    matched = True
                    break

            if not matched:
                # Create new cluster
                clusters[mention.incident_id] = [mention]

        # Build reconstructions
        reconstructions = []
        for incident_id, cluster_mentions in clusters.items():
            reconstruction = self._build_reconstruction(incident_id, cluster_mentions)
            reconstructions.append(reconstruction)

        return reconstructions

    def _mentions_match(self, mention1: IncidentMention, mention2: IncidentMention) -> bool:
        """Check if two mentions likely refer to same incident."""
        # Simple heuristic: same date or similar description
        if mention1.mentioned_date and mention2.mentioned_date:
            if mention1.mentioned_date == mention2.mentioned_date:
                return True

        # Check entity overlap
        entities1 = set(mention1.mentioned_entities)
        entities2 = set(mention2.mentioned_entities)
        overlap = len(entities1 & entities2)
        if overlap >= 2:
            return True

        return False

    def _build_reconstruction(
        self, incident_id: str, mentions: list[IncidentMention]
    ) -> IncidentReconstruction:
        """Build unified incident from multiple mentions."""
        # Use highest-confidence mention as primary
        mentions.sort(key=lambda m: m.confidence, reverse=True)
        primary = mentions[0]

        # Aggregate entities
        all_entities = set()
        for mention in mentions:
            all_entities.update(mention.mentioned_entities)

        return IncidentReconstruction(
            incident_id=incident_id,
            incident_type=primary.incident_type or "unknown",
            description=primary.description,
            occurred_date=primary.mentioned_date or "unknown",
            date_precision=primary.date_precision,
            mentions=mentions,
            primary_mention_id=primary.mention_id,
            entities_involved=list(all_entities),
            overall_confidence=sum(m.confidence for m in mentions) / len(mentions),
            corroboration_count=len(mentions),
        )
