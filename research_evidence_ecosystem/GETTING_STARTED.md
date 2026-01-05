# Getting Started: Chat Timeline Reconstruction

## Your Use Case

You have:
- **Weekly chat exports** (Claude, ChatGPT) containing real-time conversations about incidents
- **Schedules and appointments** (calendar data)
- **Notes and prior research** (various formats)
- **Prior outputs** from previous analysis

You need to:
- **Extract incident mentions** from chat conversations
- **Build chronological timelines** combining all sources
- **Organize evidence** in Obsidian with knowledge graphs
- **Verify facts** with external research (Perplexity)

## What We Built

### Core System (Phase 1 - Complete ✅)

1. **Data Models** (`models/`)
   - `ChatMessage` - Single message with incident detection
   - `ChatConversation` - Thread of related messages
   - `WeeklyChatExport` - Week's worth of data
   - `IncidentMention` - Extracted incident from any source
   - `IncidentReconstruction` - Unified incident from multiple mentions
   - `ScheduleEvent` - Calendar appointment/event

2. **Chat Parser** (`mcp_servers/chat_timeline_mcp/`)
   - `WeeklyChatParser` - Parse Claude and ChatGPT exports
   - Automatic incident keyword detection
   - Entity extraction
   - Temporal organization

3. **Incident Extractor** (`mcp_servers/chat_timeline_mcp/`)
   - `IncidentExtractor` - Use Claude to extract structured incidents
   - Domain-specific extraction (medical, legal, general)
   - Confidence scoring
   - Firsthand vs. secondhand detection
   - Incident clustering (merge related mentions)

4. **Complete Workflow** (`workflows/`)
   - `ChatToTimelineWorkflow` - End-to-end processing
   - Multi-week processing
   - Deduplication across weeks
   - Timeline generation
   - Obsidian export with backlinks

5. **Tutorial Notebook** (`notebooks/`)
   - `01_incident_extraction_from_chats.ipynb` - Complete walkthrough

## Quick Start (5 Minutes)

### Step 1: Prepare Your Data

Organize your chat exports by week:

```
data/
├── chat_exports/
│   ├── 2026_week_01_claude.json
│   ├── 2026_week_02_claude.json
│   └── 2026_week_03_chatgpt.json
└── schedules/
    └── calendar_2026_Q1.ics
```

### Step 2: Export Your Chats

**For Claude:**
Export your conversations as JSON (format expected by parser):
```json
{
  "conversations": [
    {
      "id": "conv_abc123",
      "created_at": "2026-01-01T10:00:00Z",
      "model": "claude-sonnet-4-5",
      "messages": [
        {
          "id": "msg_1",
          "role": "user",
          "content": "I had a severe headache last Monday...",
          "timestamp": "2026-01-01T10:00:00Z"
        },
        {
          "id": "msg_2",
          "role": "assistant",
          "content": "I understand. Can you describe...",
          "timestamp": "2026-01-01T10:01:00Z"
        }
      ]
    }
  ]
}
```

**For ChatGPT:**
Use ChatGPT's export feature (conversations.json format is supported)

### Step 3: Run the Workflow

```python
import asyncio
from workflows.chat_to_timeline_workflow import ChatToTimelineWorkflow

async def main():
    # Initialize workflow for your domain
    workflow = ChatToTimelineWorkflow(domain="medical")  # or "legal"

    # Process all weeks in directory
    incidents = await workflow.process_multiple_weeks(
        export_dir="data/chat_exports",
        source="claude",
        file_pattern="*_claude.json"
    )

    # Build timeline
    timeline = workflow.build_timeline(incidents)

    # Export to Obsidian
    workflow.export_to_obsidian(
        incidents=incidents,
        output_dir="obsidian_vault/case_name"
    )

    # Print summary
    print(f"\nExtracted {len(incidents)} unique incidents")
    print(f"Timeline has {len(timeline)} dated events")

asyncio.run(main())
```

### Step 4: View in Obsidian

Open your Obsidian vault at `obsidian_vault/case_name`:

```
case_name/
├── incidents/              # Individual incident notes
│   ├── 2026-01-06_symptom_abc12345.md
│   ├── 2026-01-08_appointment_def67890.md
│   └── ...
├── entities/               # Entity relationship notes
│   ├── Patient_Name.md
│   ├── Dr_Smith.md
│   └── ...
└── Timeline_Overview.md    # Complete chronological view
```

## Example Workflow: Medical Timeline

```python
# Medical use case: Build patient timeline from chat history
from workflows.chat_to_timeline_workflow import ChatToTimelineWorkflow
import asyncio

async def build_patient_timeline():
    workflow = ChatToTimelineWorkflow(domain="medical")

    # Process patient's weekly chat logs
    incidents = await workflow.process_multiple_weeks(
        export_dir="data/patient_chats",
        source="claude"
    )

    # Filter by incident type
    symptoms = [i for i in incidents if i.incident_type == "symptom"]
    appointments = [i for i in incidents if i.incident_type == "appointment"]
    medications = [i for i in incidents if i.incident_type == "medication"]

    print(f"Patient Timeline Summary:")
    print(f"  Symptoms reported: {len(symptoms)}")
    print(f"  Appointments: {len(appointments)}")
    print(f"  Medication events: {len(medications)}")

    # Export organized timeline
    workflow.export_to_obsidian(incidents, "vault/patient_timeline")

asyncio.run(build_patient_timeline())
```

## Example Workflow: Legal Case

```python
# Legal use case: Incident reconstruction from witness statements
from workflows.chat_to_timeline_workflow import ChatToTimelineWorkflow
import asyncio

async def reconstruct_incident():
    workflow = ChatToTimelineWorkflow(domain="legal")

    # Process chat logs with witness interviews
    incidents = await workflow.process_multiple_weeks(
        export_dir="data/witness_interviews",
        source="chatgpt"
    )

    # Find incidents with multiple corroborating sources
    well_corroborated = [
        i for i in incidents
        if i.corroboration_count >= 2 and i.overall_confidence >= 0.7
    ]

    print(f"Incident Reconstruction:")
    print(f"  Total incidents: {len(incidents)}")
    print(f"  Well-corroborated: {len(well_corroborated)}")

    # Build timeline
    timeline = workflow.build_timeline(well_corroborated)

    # Export
    workflow.export_to_obsidian(incidents, "vault/case_timeline")

asyncio.run(reconstruct_incident())
```

## Understanding the Output

### Incident Note Structure

Each incident gets its own Obsidian note:

```markdown
---
type: incident
date: 2026-01-06
incident_type: symptom
confidence: 0.85
sources: 3
tags: [incident, symptom]
---

# Severe headache episode

## Details
- **Date**: 2026-01-06 (exact)
- **Type**: symptom
- **Confidence**: 0.85
- **Corroboration**: 3 sources

## Entities Involved
- [[Patient Name]]
- [[Dr. Smith]]
- [[ER Department]]

## Source Mentions

### Mention 1
- **Source**: conv_123 (chat)
- **Date**: 2026-01-07T10:30:00
- **Firsthand**: true
- **Confidence**: 0.9

> "I had a severe headache on Monday that lasted 4 hours.
> Took ibuprofen but it didn't help much."

### Mention 2
- **Source**: conv_456 (chat)
- **Date**: 2026-01-09T14:00:00
- **Firsthand**: true
- **Confidence**: 0.8

> "Following up on that headache from last Monday -
> Dr. Smith said it might be related to stress."
```

### Timeline Overview

```markdown
# Timeline Overview

Total events: 47

## Chronological Events

### 2026-01-01 - Initial consultation
- **Type**: appointment
- **Confidence**: 0.95
- **Sources**: 2

### 2026-01-06 - Severe headache episode
- **Type**: symptom
- **Confidence**: 0.85
- **Sources**: 3

### 2026-01-08 - MRI scan
- **Type**: procedure
- **Confidence**: 0.9
- **Sources**: 1
```

## Next Steps

### Phase 2: Schedule Integration

```python
# Coming soon - correlate with calendar
from mcp_servers.schedule_mcp import ScheduleMCP

schedule = ScheduleMCP()
events = schedule.parse_ical("calendar.ics")

# Match incidents to appointments
correlations = schedule.correlate_with_incidents(events, incidents)
```

### Phase 3: Research Verification

```python
# Coming soon - verify with Perplexity
from mcp_servers.perplexity_mcp import PerplexityMCP

perplexity = PerplexityMCP()
research = await perplexity.verify_incident(
    incident=extracted_incident,
    focus="medical"
)
```

### Phase 4: Knowledge Graph

```python
# Coming soon - visualize entity relationships
from mcp_servers.obsidian_mcp import ObsidianMCP

obsidian = ObsidianMCP()
graph = obsidian.build_knowledge_graph(
    vault_path="obsidian_vault/case_name"
)
```

## Troubleshooting

### No incidents found

**Problem**: Parser doesn't detect any incidents in chats

**Solution**: Check that your chats actually mention events. The parser looks for keywords like:
- Medical: "pain", "symptom", "doctor", "appointment", "medication", "hospital"
- Legal: "incident", "accident", "violation", "filed", "hearing", "dispute"
- Temporal: "on Monday", "last week", "yesterday", "that day"

### Low confidence scores

**Problem**: Incidents have low confidence scores

**Solution**: This is normal for:
- Vague descriptions ("something happened")
- Secondhand accounts ("I heard that...")
- Uncertain dates ("sometime last month")

Focus on incidents with confidence >= 0.7 for high-quality timelines.

### Incorrect date extraction

**Problem**: Dates are wrong or missing

**Solution**: Be explicit in your chats. Instead of "last Monday", say "Monday, January 6, 2026" for exact dates.

## Tips for Better Results

### 1. Structured Chat Habits

When documenting incidents in chats, include:
- Specific dates and times
- Clear descriptions
- Named entities (people, places, organizations)
- Whether you witnessed it firsthand

Example:
```
❌ "Something bad happened last week"

✅ "On Monday, January 6, 2026 at 3pm, I experienced severe
    headache pain. Lasted 4 hours. Dr. Smith was notified."
```

### 2. Weekly Processing

Process chats weekly rather than monthly:
- More accurate temporal references
- Better incident clustering
- Easier to correlate with schedules

### 3. Domain Specification

Always specify your domain:
```python
workflow = ChatToTimelineWorkflow(domain="medical")  # Better extraction
```

### 4. Cross-Verification

Use multiple sources:
- Chats + schedules + notes = higher confidence
- Look for incidents with corroboration_count >= 2

## Support

For issues or questions:
- Check the main README: `research_evidence_ecosystem/README.md`
- See example notebook: `notebooks/01_incident_extraction_from_chats.ipynb`
- Review data models: `models/` directory

## Summary

You now have a complete system to:
✅ Parse weekly chat exports (Claude, ChatGPT)
✅ Extract incidents using AI
✅ Build chronological timelines
✅ Export to Obsidian with knowledge graphs
⏳ Schedule correlation (Phase 2)
⏳ Research verification (Phase 3)
⏳ Advanced knowledge graphs (Phase 4)

**Start with the notebook**: `notebooks/01_incident_extraction_from_chats.ipynb`
