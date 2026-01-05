# Research & Evidence Ecosystem

A comprehensive system for building legal and medical timelines from multiple sources:
- Weekly chat exports (Claude, ChatGPT)
- Calendar/schedule data
- Research notes and prior outputs
- External research (Perplexity)

## Overview

This ecosystem helps you **reconstruct incidents and build timelines** by:

1. **Parsing chat exports** - Extract conversations organized by week
2. **Extracting incidents** - Use AI to identify event mentions in real-time conversations
3. **Temporal correlation** - Match chat mentions to schedules and appointments
4. **Timeline synthesis** - Build chronological timelines from all sources
5. **Knowledge organization** - Export to Obsidian with backlinks and entity graphs

## Use Cases

### Medical Timelines
- Patient symptom tracking from chat logs
- Appointment and treatment history
- Medication events and side effects
- Build comprehensive medical timelines for care coordination

### Legal Timelines
- Incident reconstruction from witness statements
- Event chronology for case preparation
- Evidence organization with citations
- Depositions and filing timeline tracking

## Quick Start

### 1. Install Dependencies

```bash
cd research_evidence_ecosystem
pip install anthropic pydantic python-dotenv
```

### 2. Set API Key

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

### 3. Run Example Workflow

```python
from workflows.chat_to_timeline_workflow import ChatToTimelineWorkflow
import asyncio

async def example():
    workflow = ChatToTimelineWorkflow(domain="medical")

    # Process weekly chat export
    incidents = await workflow.process_weekly_export(
        export_path="data/2026_week_01_claude.json",
        week_id="2026-W01",
        source="claude"
    )

    # Build timeline
    timeline = workflow.build_timeline(incidents)

    # Export to Obsidian
    workflow.export_to_obsidian(incidents, "obsidian_vault")

asyncio.run(example())
```

## Architecture

```
research_evidence_ecosystem/
├── models/                    # Pydantic data models
│   ├── chat_message.py       # Chat message structure
│   ├── incident_mention.py   # Incident extraction
│   └── schedule_event.py     # Calendar events
│
├── mcp_servers/               # MCP integrations
│   ├── chat_timeline_mcp/    # Chat parsing
│   ├── schedule_mcp/         # Calendar integration
│   ├── obsidian_mcp/         # Obsidian vault operations
│   └── perplexity_mcp/       # Research verification
│
├── workflows/                 # End-to-end workflows
│   ├── chat_to_timeline_workflow.py
│   └── incident_reconstruction.py
│
└── notebooks/                 # Jupyter tutorials
    ├── 01_incident_extraction_from_chats.ipynb
    ├── 02_schedule_correlation.ipynb
    └── 03_obsidian_integration.ipynb
```

## Key Features

### 1. Multi-Source Chat Parsing

Supports multiple export formats:
- Claude conversation exports (JSON)
- ChatGPT exports (conversations.json)
- Extensible to other chat platforms

```python
from mcp_servers.chat_timeline_mcp.weekly_chat_parser import WeeklyChatParser

parser = WeeklyChatParser()
week_data = parser.parse_claude_export("2026_week_01.json", "2026-W01")
```

### 2. Intelligent Incident Extraction

Uses Claude to extract structured incident mentions:

```python
from mcp_servers.chat_timeline_mcp.incident_extractor import IncidentExtractor

extractor = IncidentExtractor()
mentions = await extractor.extract_incidents_from_conversation(
    conversation=chat_data,
    domain="medical"  # or "legal"
)
```

### 3. Temporal Correlation

Match chat mentions to scheduled events:

```python
# Correlate incidents with appointments
correlations = correlator.match_incidents_to_schedule(
    incidents=extracted_incidents,
    schedule_events=calendar_data
)
```

### 4. Obsidian Integration

Export as interconnected markdown notes:
- Individual incident notes with citations
- Entity relationship graph
- Timeline overview
- Automatic backlinks

```python
workflow.export_to_obsidian(incidents, "obsidian_vault")
```

## Data Models

### ChatMessage
Single message from chat export with metadata:
```python
ChatMessage(
    message_id="msg_123",
    timestamp=datetime.now(),
    source="claude",
    role="user",
    content="I had severe headache on Monday...",
    incident_indicators=["pain", "monday"],
    is_incident_related=True,
    confidence=0.8
)
```

### IncidentMention
Extracted incident from chat/notes:
```python
IncidentMention(
    description="Severe headache",
    mentioned_date="2026-01-06",
    date_precision="exact",
    incident_type="symptom",
    confidence=0.85,
    is_firsthand=True,
    source_type="chat"
)
```

### IncidentReconstruction
Unified incident from multiple mentions:
```python
IncidentReconstruction(
    incident_id="inc_123",
    description="Severe headache episode",
    occurred_date="2026-01-06",
    mentions=[mention1, mention2, mention3],
    corroboration_count=3,
    overall_confidence=0.9
)
```

## Workflows

### Complete Chat-to-Timeline Workflow

```python
from workflows.chat_to_timeline_workflow import ChatToTimelineWorkflow

workflow = ChatToTimelineWorkflow(domain="medical")

# Process multiple weeks
incidents = await workflow.process_multiple_weeks(
    export_dir="data/chat_exports",
    source="claude"
)

# Build timeline
timeline = workflow.build_timeline(incidents)

# Export to Obsidian
workflow.export_to_obsidian(incidents, "obsidian_vault")
```

### Weekly Processing

```python
# Process each week as exports arrive
for week in ["2026-W01", "2026-W02", "2026-W03"]:
    incidents = await workflow.process_weekly_export(
        export_path=f"data/{week}_claude.json",
        week_id=week,
        source="claude"
    )
    # Incremental export
    workflow.export_to_obsidian(incidents, f"vault/{week}")
```

## Integration with Other Tools

### Perplexity Research Verification

```python
# Coming soon: Verify incident claims with web research
from mcp_servers.perplexity_mcp import PerplexityMCP

research = await perplexity.verify_incident(
    incident=extracted_incident,
    focus="medical"
)
```

### Schedule Integration

```python
# Coming soon: Parse calendar data
from mcp_servers.schedule_mcp import ScheduleMCP

events = schedule_mcp.parse_ical("calendar.ics")
correlations = correlator.match_to_incidents(events, incidents)
```

## Export Formats

### Obsidian Markdown

```markdown
---
type: incident
date: 2026-01-06
incident_type: symptom
confidence: 0.85
---

# Severe headache episode

## Details
- **Date**: 2026-01-06 (exact)
- **Type**: symptom
- **Confidence**: 0.85

## Entities Involved
- [[Patient Name]]
- [[Dr. Smith]]

## Source Mentions
### Mention 1
- **Source**: conv_123
- **Firsthand**: true
> I had a severe headache on Monday...
```

### JSON Timeline

```json
{
  "timeline": [
    {
      "date": "2026-01-06",
      "type": "symptom",
      "description": "Severe headache",
      "confidence": 0.85,
      "sources": 3
    }
  ]
}
```

## Roadmap

- [x] Chat parsing (Claude, ChatGPT)
- [x] Incident extraction with AI
- [x] Basic timeline generation
- [x] Obsidian export
- [ ] Schedule/calendar integration
- [ ] Perplexity research verification
- [ ] Knowledge graph visualization
- [ ] Multi-document synthesis
- [ ] Conflict detection and resolution
- [ ] Interactive timeline UI

## Contributing

See main cookbook README for contribution guidelines.

## License

MIT License - see main cookbook LICENSE file.
