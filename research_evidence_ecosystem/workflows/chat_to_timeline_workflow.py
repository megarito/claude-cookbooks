"""Complete workflow: Weekly chat exports → Timeline reconstruction."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Literal

from research_evidence_ecosystem.mcp_servers.chat_timeline_mcp.incident_extractor import (
    IncidentExtractor,
)
from research_evidence_ecosystem.mcp_servers.chat_timeline_mcp.weekly_chat_parser import (
    WeeklyChatParser,
)
from research_evidence_ecosystem.models.incident_mention import IncidentReconstruction


class ChatToTimelineWorkflow:
    """End-to-end workflow for building timelines from chat exports."""

    def __init__(self, domain: Literal["medical", "legal", "general"] = "general"):
        self.domain = domain
        self.parser = WeeklyChatParser()
        self.extractor = IncidentExtractor()

    async def process_weekly_export(
        self,
        export_path: str,
        week_id: str,
        source: Literal["claude", "chatgpt"] = "claude",
    ) -> list[IncidentReconstruction]:
        """
        Process a single weekly chat export.

        Returns:
            List of reconstructed incidents from this week
        """
        print(f"\n{'='*60}")
        print(f"Processing {week_id} ({source})")
        print(f"{'='*60}\n")

        # Step 1: Parse export
        print("Step 1: Parsing chat export...")
        if source == "claude":
            week_data = self.parser.parse_claude_export(export_path, week_id)
        else:
            week_data = self.parser.parse_chatgpt_export(export_path, week_id)

        print(f"  ✓ Found {len(week_data.conversations)} conversations")
        print(f"  ✓ Total messages: {week_data.total_messages}")
        print(f"  ✓ Incident-related messages: {week_data.incidents_mentioned}")

        # Step 2: Extract incidents
        print("\nStep 2: Extracting incidents from conversations...")
        all_mentions = []

        for i, conversation in enumerate(week_data.conversations, 1):
            print(f"  Conversation {i}/{len(week_data.conversations)}: {conversation.primary_topic[:40]}...")

            mentions = await self.extractor.extract_incidents_from_conversation(
                conversation=conversation, domain=self.domain
            )

            print(f"    → Found {len(mentions)} incident mentions")
            all_mentions.extend(mentions)

        print(f"\n  ✓ Total mentions extracted: {len(all_mentions)}")

        # Step 3: Cluster mentions
        print("\nStep 3: Clustering related mentions...")
        incidents = self.extractor.cluster_incidents(all_mentions)
        print(f"  ✓ Identified {len(incidents)} unique incidents")

        return incidents

    async def process_multiple_weeks(
        self,
        export_dir: str,
        source: Literal["claude", "chatgpt"] = "claude",
        file_pattern: str = "*.json",
    ) -> list[IncidentReconstruction]:
        """
        Process multiple weekly exports from a directory.

        Args:
            export_dir: Directory containing weekly export files
            source: Chat platform
            file_pattern: Glob pattern for export files

        Returns:
            Combined list of all incidents across all weeks
        """
        export_path = Path(export_dir)
        export_files = sorted(export_path.glob(file_pattern))

        if not export_files:
            print(f"No export files found matching {file_pattern} in {export_dir}")
            return []

        print(f"Found {len(export_files)} export files")

        all_incidents = []

        for export_file in export_files:
            # Extract week ID from filename (assumes format: 2026_week_01_claude.json)
            week_id = export_file.stem.split("_week_")[1].split("_")[0]
            week_id = f"2026-W{week_id.zfill(2)}"

            incidents = await self.process_weekly_export(
                export_path=str(export_file), week_id=week_id, source=source
            )

            all_incidents.extend(incidents)

        # Deduplicate incidents across weeks
        print(f"\n{'='*60}")
        print("Deduplicating incidents across weeks...")
        print(f"{'='*60}\n")

        deduplicated = self._deduplicate_incidents(all_incidents)
        print(f"  ✓ {len(all_incidents)} total incidents")
        print(f"  ✓ {len(deduplicated)} unique incidents after deduplication")

        return deduplicated

    def _deduplicate_incidents(
        self, incidents: list[IncidentReconstruction]
    ) -> list[IncidentReconstruction]:
        """Remove duplicate incidents across multiple weeks."""
        # Group by incident description similarity
        # In production, use embeddings for better matching
        unique_incidents = []
        seen_descriptions = set()

        for incident in incidents:
            # Simple dedup by description prefix
            desc_key = incident.description[:50].lower()

            if desc_key not in seen_descriptions:
                unique_incidents.append(incident)
                seen_descriptions.add(desc_key)
            else:
                # Merge mentions into existing incident
                for existing in unique_incidents:
                    if existing.description[:50].lower() == desc_key:
                        existing.mentions.extend(incident.mentions)
                        existing.corroboration_count += incident.corroboration_count
                        break

        return unique_incidents

    def build_timeline(
        self, incidents: list[IncidentReconstruction]
    ) -> list[dict[str, any]]:
        """
        Build chronological timeline from incidents.

        Returns:
            Sorted list of timeline events
        """
        timeline = []

        for incident in incidents:
            if incident.occurred_date and incident.occurred_date != "unknown":
                timeline.append(
                    {
                        "date": incident.occurred_date,
                        "precision": incident.date_precision,
                        "incident_id": incident.incident_id,
                        "type": incident.incident_type,
                        "description": incident.description,
                        "entities": incident.entities_involved,
                        "confidence": incident.overall_confidence,
                        "sources": incident.corroboration_count,
                        "mentions": len(incident.mentions),
                    }
                )

        # Sort chronologically
        timeline.sort(key=lambda e: str(e["date"]))

        return timeline

    def export_to_obsidian(
        self, incidents: list[IncidentReconstruction], output_dir: str
    ) -> None:
        """
        Export incidents as Obsidian markdown notes.

        Creates:
        - Individual incident notes
        - Timeline overview note
        - Entity index notes
        """
        output_path = Path(output_dir)
        incidents_dir = output_path / "incidents"
        entities_dir = output_path / "entities"

        incidents_dir.mkdir(parents=True, exist_ok=True)
        entities_dir.mkdir(parents=True, exist_ok=True)

        # Export individual incidents
        print(f"\nExporting to {output_dir}...")

        entity_index = {}  # Track which incidents mention each entity

        for incident in incidents:
            # Create incident note
            safe_date = str(incident.occurred_date).replace(":", "-")[:10]
            filename = f"{safe_date}_{incident.incident_type}_{incident.incident_id[:8]}.md"

            md_content = self._create_incident_markdown(incident)

            with open(incidents_dir / filename, "w") as f:
                f.write(md_content)

            # Update entity index
            for entity in incident.entities_involved:
                if entity not in entity_index:
                    entity_index[entity] = []
                entity_index[entity].append(incident.incident_id)

        print(f"  ✓ Created {len(incidents)} incident notes")

        # Create entity index notes
        for entity, incident_ids in entity_index.items():
            entity_note = f"""---
type: entity
incidents: {len(incident_ids)}
---

# {entity}

Mentioned in {len(incident_ids)} incidents:

"""
            for inc_id in incident_ids:
                entity_note += f"- [[{inc_id}]]\n"

            safe_entity = entity.replace("/", "-").replace(":", "")
            with open(entities_dir / f"{safe_entity}.md", "w") as f:
                f.write(entity_note)

        print(f"  ✓ Created {len(entity_index)} entity notes")

        # Create timeline overview
        timeline = self.build_timeline(incidents)
        timeline_md = self._create_timeline_markdown(timeline)

        with open(output_path / "Timeline_Overview.md", "w") as f:
            f.write(timeline_md)

        print(f"  ✓ Created timeline overview")

    def _create_incident_markdown(self, incident: IncidentReconstruction) -> str:
        """Generate Obsidian markdown for an incident."""
        md = f"""---
type: incident
date: {incident.occurred_date}
date_precision: {incident.date_precision}
incident_type: {incident.incident_type}
confidence: {incident.overall_confidence}
sources: {incident.corroboration_count}
tags: [incident, {incident.incident_type}]
---

# {incident.description}

## Details
- **Date**: {incident.occurred_date} ({incident.date_precision})
- **Type**: {incident.incident_type}
- **Confidence**: {incident.overall_confidence:.2f}
- **Corroboration**: {incident.corroboration_count} sources

## Entities Involved
"""
        for entity in incident.entities_involved:
            md += f"- [[{entity}]]\n"

        md += "\n## Source Mentions\n"

        for i, mention in enumerate(incident.mentions, 1):
            md += f"""
### Mention {i}
- **Source**: {mention.source_id}
- **Date**: {mention.source_timestamp}
- **Firsthand**: {mention.is_firsthand}
- **Confidence**: {mention.confidence:.2f}

> {mention.excerpt}
"""

        return md

    def _create_timeline_markdown(self, timeline: list[dict]) -> str:
        """Generate Obsidian timeline overview."""
        md = f"""---
type: timeline
total_events: {len(timeline)}
generated: {datetime.now().isoformat()}
---

# Timeline Overview

Total events: {len(timeline)}

## Chronological Events

"""
        for event in timeline:
            md += f"""
### {event['date']} - {event['description']}
- **Type**: {event['type']}
- **Precision**: {event['precision']}
- **Confidence**: {event['confidence']:.2f}
- **Sources**: {event['sources']}
- **Entities**: {', '.join(event['entities'][:5])}

"""

        return md


# Example usage
async def main():
    """Example workflow execution."""
    workflow = ChatToTimelineWorkflow(domain="medical")

    # Process single week
    incidents = await workflow.process_weekly_export(
        export_path="data/chat_exports/2026_week_01_claude.json",
        week_id="2026-W01",
        source="claude",
    )

    # Or process multiple weeks
    # incidents = await workflow.process_multiple_weeks(
    #     export_dir="data/chat_exports",
    #     source="claude"
    # )

    # Build timeline
    timeline = workflow.build_timeline(incidents)

    # Export to Obsidian
    workflow.export_to_obsidian(incidents, output_dir="obsidian_vault")

    print("\n" + "=" * 60)
    print("WORKFLOW COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
