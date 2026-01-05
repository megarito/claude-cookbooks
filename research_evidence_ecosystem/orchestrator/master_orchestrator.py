"""
Master Orchestrator - Intelligently route and process multi-source weekly data.

Coordinates:
- Data classification (identify data types)
- Intelligent routing (send to appropriate MCP server)
- Multi-agent processing (use Claude Code SDK agents)
- Timeline synthesis (combine all sources)
- Export to Obsidian

Usage:
    orchestrator = MasterOrchestrator()
    await orchestrator.process_weekly_data_dump("data/2026_week_01/")
"""

import asyncio
from pathlib import Path
from typing import Any
import os

from research_evidence_ecosystem.classifiers.data_type_classifier import (
    DataTypeClassifier,
    DataClassification,
)


class MasterOrchestrator:
    """
    Master orchestrator for processing multi-source weekly data dumps.

    Handles chat exports, medical records, work data, and research simultaneously.
    """

    def __init__(self, obsidian_vault_path: str = "obsidian_vault"):
        self.classifier = DataTypeClassifier()
        self.obsidian_vault = obsidian_vault_path

        # Track processed data
        self.processed_chats = []
        self.processed_medical = []
        self.processed_work = []
        self.processed_research = []

    async def process_weekly_data_dump(
        self, data_directory: str, week_id: str | None = None
    ) -> dict[str, Any]:
        """
        Process an entire weekly data dump directory.

        Expected structure:
        data/2026_week_01/
        ├── chats/
        │   ├── claude_export.json
        │   ├── chatgpt_export.json
        │   └── perplexity_research.json
        ├── medical/
        │   ├── lab_results.pdf
        │   ├── doctor_visit_summary.txt
        │   └── vitals.csv
        ├── work/
        │   ├── timesheet.xlsx
        │   ├── incident_report.pdf
        │   └── communications/
        └── research/
            └── notes.md

        Args:
            data_directory: Path to weekly data dump
            week_id: Week identifier (e.g., "2026-W01"), auto-detected if None

        Returns:
            Summary of processed data
        """
        print(f"\n{'='*70}")
        print(f"MASTER ORCHESTRATOR - Processing Weekly Data")
        print(f"{'='*70}\n")

        data_path = Path(data_directory)
        if not data_path.exists():
            raise ValueError(f"Data directory not found: {data_directory}")

        # Auto-detect week ID from directory name
        if not week_id:
            week_id = self._detect_week_id(data_path.name)

        print(f"Week ID: {week_id}")
        print(f"Source: {data_directory}\n")

        # Step 1: Classify all files
        print("Step 1: Classifying all files...")
        classifications = self.classifier.classify_directory(str(data_path))

        self._print_classification_summary(classifications)

        # Step 2: Route to specialized processors
        print("\nStep 2: Processing data by type...")

        results = {
            "week_id": week_id,
            "chat_incidents": [],
            "medical_events": [],
            "work_events": [],
            "research_notes": [],
            "timeline_events": [],
        }

        # Process chat data
        chat_results = await self._process_chat_data(
            classifications.get("chat_claude", [])
            + classifications.get("chat_chatgpt", [])
            + classifications.get("chat_perplexity", []),
            week_id,
        )
        results["chat_incidents"] = chat_results

        # Process medical data
        medical_results = await self._process_medical_data(
            classifications.get("medical_appointment", [])
            + classifications.get("medical_lab_result", [])
            + classifications.get("medical_imaging", [])
            + classifications.get("medical_vitals", [])
            + classifications.get("medical_visit_summary", []),
            week_id,
        )
        results["medical_events"] = medical_results

        # Process work data
        work_results = await self._process_work_data(
            classifications.get("work_timesheet", [])
            + classifications.get("work_incident", [])
            + classifications.get("work_hours", [])
            + classifications.get("legal_damages", []),
            week_id,
        )
        results["work_events"] = work_results

        # Step 3: Build unified timeline
        print("\nStep 3: Building unified timeline...")
        timeline = self._build_unified_timeline(results)
        results["timeline_events"] = timeline

        # Step 4: Export to Obsidian
        print("\nStep 4: Exporting to Obsidian...")
        await self._export_to_obsidian(results, week_id)

        # Print summary
        self._print_final_summary(results)

        return results

    async def _process_chat_data(
        self, chat_files: list[DataClassification], week_id: str
    ) -> list[dict]:
        """Process all chat exports using chat_timeline_mcp."""
        if not chat_files:
            print("  📱 Chat Data: None found")
            return []

        print(f"  📱 Chat Data: Processing {len(chat_files)} files...")

        from research_evidence_ecosystem.workflows.chat_to_timeline_workflow import (
            ChatToTimelineWorkflow,
        )

        workflow = ChatToTimelineWorkflow(domain="general")

        all_incidents = []

        for chat_file in chat_files:
            try:
                # Determine source type
                source = "claude" if "claude" in chat_file.data_type else "chatgpt"

                incidents = await workflow.process_weekly_export(
                    export_path=chat_file.file_path, week_id=week_id, source=source
                )

                all_incidents.extend(incidents)
                print(f"     ✓ {Path(chat_file.file_path).name}: {len(incidents)} incidents")

            except Exception as e:
                print(f"     ✗ {Path(chat_file.file_path).name}: Error - {e}")

        return [
            {
                "type": "chat_incident",
                "description": inc.description,
                "date": str(inc.occurred_date),
                "confidence": inc.overall_confidence,
                "sources": inc.corroboration_count,
            }
            for inc in all_incidents
        ]

    async def _process_medical_data(
        self, medical_files: list[DataClassification], week_id: str
    ) -> list[dict]:
        """Process medical records using medical_data_mcp."""
        if not medical_files:
            print("  🏥 Medical Data: None found")
            return []

        print(f"  🏥 Medical Data: Processing {len(medical_files)} files...")

        # In production: Use Claude Code SDK with medical_data_mcp
        # For now, simulate processing

        results = []
        for med_file in medical_files:
            file_name = Path(med_file.file_path).name
            med_type = med_file.data_type.replace("medical_", "")

            # Simulate extraction
            result = {
                "type": med_type,
                "file": file_name,
                "date": "2026-01-06",  # Would extract from file
                "summary": f"Processed {med_type}",
            }

            results.append(result)
            print(f"     ✓ {file_name}: {med_type}")

        return results

    async def _process_work_data(
        self, work_files: list[DataClassification], week_id: str
    ) -> list[dict]:
        """Process work records using work_data_mcp."""
        if not work_files:
            print("  💼 Work Data: None found")
            return []

        print(f"  💼 Work Data: Processing {len(work_files)} files...")

        results = []
        for work_file in work_files:
            file_name = Path(work_file.file_path).name
            work_type = work_file.data_type.replace("work_", "").replace("legal_", "")

            # Simulate extraction
            result = {
                "type": work_type,
                "file": file_name,
                "date": "2026-01-06",
                "summary": f"Processed {work_type}",
            }

            results.append(result)
            print(f"     ✓ {file_name}: {work_type}")

        return results

    def _build_unified_timeline(self, results: dict) -> list[dict]:
        """Combine all events into unified timeline."""
        timeline = []

        # Add chat incidents
        for incident in results.get("chat_incidents", []):
            timeline.append(
                {
                    "date": incident["date"],
                    "type": "chat_incident",
                    "description": incident["description"],
                    "source": "chat",
                    "confidence": incident["confidence"],
                }
            )

        # Add medical events
        for event in results.get("medical_events", []):
            timeline.append(
                {
                    "date": event.get("date", "unknown"),
                    "type": event["type"],
                    "description": event["summary"],
                    "source": "medical",
                    "confidence": 1.0,
                }
            )

        # Add work events
        for event in results.get("work_events", []):
            timeline.append(
                {
                    "date": event.get("date", "unknown"),
                    "type": event["type"],
                    "description": event["summary"],
                    "source": "work",
                    "confidence": 1.0,
                }
            )

        # Sort chronologically
        timeline.sort(key=lambda e: str(e.get("date", "9999")))

        print(f"  📅 Timeline: {len(timeline)} total events")

        return timeline

    async def _export_to_obsidian(self, results: dict, week_id: str):
        """Export all results to Obsidian vault."""
        vault_path = Path(self.obsidian_vault) / week_id
        vault_path.mkdir(parents=True, exist_ok=True)

        # Create week summary note
        summary_md = self._create_week_summary(results, week_id)
        with open(vault_path / f"{week_id}_Summary.md", "w") as f:
            f.write(summary_md)

        # Create timeline note
        timeline_md = self._create_timeline_markdown(results["timeline_events"])
        with open(vault_path / f"{week_id}_Timeline.md", "w") as f:
            f.write(timeline_md)

        print(f"  ✓ Exported to {vault_path}")

    def _create_week_summary(self, results: dict, week_id: str) -> str:
        """Create week summary markdown."""
        return f"""---
type: weekly_summary
week: {week_id}
chat_incidents: {len(results['chat_incidents'])}
medical_events: {len(results['medical_events'])}
work_events: {len(results['work_events'])}
total_timeline_events: {len(results['timeline_events'])}
---

# {week_id} Weekly Summary

## Data Sources Processed

### 📱 Chat Data
- Incidents extracted: {len(results['chat_incidents'])}

### 🏥 Medical Data
- Events processed: {len(results['medical_events'])}

### 💼 Work Data
- Events processed: {len(results['work_events'])}

## Timeline
[[{week_id}_Timeline|View Complete Timeline]]

## Key Events
{self._format_key_events(results['timeline_events'][:5])}

## Next Steps
- [ ] Review timeline accuracy
- [ ] Cross-reference with calendar
- [ ] Add additional context
"""

    def _create_timeline_markdown(self, timeline: list[dict]) -> str:
        """Create timeline markdown."""
        md = "# Timeline\n\n"
        for event in timeline:
            md += f"## {event['date']} - {event['description']}\n"
            md += f"- **Type**: {event['type']}\n"
            md += f"- **Source**: {event['source']}\n"
            md += f"- **Confidence**: {event['confidence']:.2f}\n\n"
        return md

    def _format_key_events(self, events: list[dict]) -> str:
        """Format key events for summary."""
        if not events:
            return "No events"
        return "\n".join([f"- {e['date']}: {e['description']}" for e in events])

    def _detect_week_id(self, dir_name: str) -> str:
        """Auto-detect week ID from directory name."""
        import re

        # Try patterns like "2026_week_01" or "week_01"
        match = re.search(r"(\d{4}_)?week_(\d{2})", dir_name, re.IGNORECASE)
        if match:
            year = match.group(1).rstrip("_") if match.group(1) else "2026"
            week = match.group(2)
            return f"{year}-W{week}"

        return "UNKNOWN_WEEK"

    def _print_classification_summary(self, classifications: dict):
        """Print classification results."""
        print("\nFile Classification Results:")
        for data_type, files in classifications.items():
            if files:
                print(f"  {data_type}: {len(files)} files")

    def _print_final_summary(self, results: dict):
        """Print final processing summary."""
        print(f"\n{'='*70}")
        print("PROCESSING COMPLETE")
        print(f"{'='*70}\n")
        print(f"Chat Incidents:    {len(results['chat_incidents'])}")
        print(f"Medical Events:    {len(results['medical_events'])}")
        print(f"Work Events:       {len(results['work_events'])}")
        print(f"Timeline Events:   {len(results['timeline_events'])}")
        print(f"\nExported to: {self.obsidian_vault}/{results['week_id']}")


# Example usage
async def main():
    """Example: Process weekly data dump."""
    orchestrator = MasterOrchestrator(obsidian_vault_path="obsidian_vault")

    results = await orchestrator.process_weekly_data_dump(
        data_directory="data/2026_week_01", week_id="2026-W01"
    )

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
