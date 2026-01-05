

# Multi-Source Data Processing with Claude Code

## Your Complete Weekly Data Ecosystem

This guide shows you how to use Claude Code to intelligently process your weekly data dumps containing:

- **Chat Exports**: ChatGPT, Claude, Perplexity
- **Medical Records**: Appointments, labs, imaging, vitals, visit summaries
- **Work Data**: Timesheets, incidents, hours, pay/damages, communications
- **Research**: Notes, prior outputs, research findings

## How It Works

### Intelligent Data Classification

The system **automatically identifies** what type of data each file contains:

```python
from classifiers.data_type_classifier import DataTypeClassifier

classifier = DataTypeClassifier()

# Classify a file
result = classifier.classify_file("unknown_export.json")
print(f"Type: {result.data_type}")           # "chat_claude"
print(f"Confidence: {result.confidence}")     # 0.98
print(f"Processor: {result.suggested_processor}")  # "chat_timeline_mcp"

# Classify entire directory
grouped = classifier.classify_directory("data/2026_week_01")
# Returns: {
#   "chat_claude": [file1, file2],
#   "medical_lab_result": [file3],
#   "work_timesheet": [file4]
# }
```

### Automatic Routing

Each data type gets sent to the appropriate specialized processor:

```
📱 Chat Data        → chat_timeline_mcp  → Incident extraction
🏥 Medical Data     → medical_data_mcp   → Appointment/lab/vitals parsing
💼 Work Data        → work_data_mcp      → Timesheet/incident processing
📚 Research         → perplexity_mcp     → Research verification
```

### Unified Timeline

All sources get combined into one chronological timeline with cross-references.

## Setup: Organize Your Weekly Data

### Recommended Directory Structure

```
data/
├── 2026_week_01/
│   ├── chats/
│   │   ├── claude_conversations.json
│   │   ├── chatgpt_export.json
│   │   └── perplexity_research.md
│   ├── medical/
│   │   ├── 2026-01-06_lab_results.pdf
│   │   ├── 2026-01-08_doctor_visit_summary.txt
│   │   ├── 2026-01-09_vitals.csv
│   │   └── imaging_mri_results.pdf
│   ├── work/
│   │   ├── timesheet_week01.xlsx
│   │   ├── incident_report_2026-01-07.pdf
│   │   ├── hours_log.csv
│   │   └── communications/
│   │       ├── email_thread_damages.txt
│   │       └── slack_work_incident.json
│   └── research/
│       ├── legal_research_notes.md
│       └── prior_case_analysis.pdf
│
├── 2026_week_02/
│   └── ... (same structure)
│
└── 2026_week_03/
    └── ...
```

**Note**: The structure is flexible! The classifier will identify files regardless of organization.

## Usage: Process Weekly Data

### Method 1: One-Line Processing (Recommended)

```python
import asyncio
from orchestrator.master_orchestrator import MasterOrchestrator

async def process_week():
    orchestrator = MasterOrchestrator(obsidian_vault_path="obsidian_vault")

    results = await orchestrator.process_weekly_data_dump(
        data_directory="data/2026_week_01",
        week_id="2026-W01"  # Optional: auto-detected from folder name
    )

    print(f"✓ Processed {len(results['timeline_events'])} events")

asyncio.run(process_week())
```

**Output:**
```
======================================================================
MASTER ORCHESTRATOR - Processing Weekly Data
======================================================================

Week ID: 2026-W01
Source: data/2026_week_01

Step 1: Classifying all files...

File Classification Results:
  chat_claude: 1 files
  chat_chatgpt: 1 files
  medical_lab_result: 2 files
  medical_vitals: 1 files
  work_timesheet: 1 files
  work_incident: 1 files

Step 2: Processing data by type...
  📱 Chat Data: Processing 2 files...
     ✓ claude_conversations.json: 12 incidents
     ✓ chatgpt_export.json: 8 incidents
  🏥 Medical Data: Processing 3 files...
     ✓ lab_results.pdf: lab_result
     ✓ vitals.csv: vitals
  💼 Work Data: Processing 2 files...
     ✓ timesheet_week01.xlsx: timesheet
     ✓ incident_report.pdf: incident

Step 3: Building unified timeline...
  📅 Timeline: 25 total events

Step 4: Exporting to Obsidian...
  ✓ Exported to obsidian_vault/2026-W01

======================================================================
PROCESSING COMPLETE
======================================================================
Chat Incidents:    20
Medical Events:    3
Work Events:       2
Timeline Events:   25

Exported to: obsidian_vault/2026-W01
```

### Method 2: Process Multiple Weeks

```python
async def process_all_weeks():
    orchestrator = MasterOrchestrator()

    # Process all weeks in data directory
    from pathlib import Path

    weeks = sorted(Path("data").glob("2026_week_*"))

    for week_dir in weeks:
        print(f"\n{'='*60}")
        print(f"Processing {week_dir.name}")
        print(f"{'='*60}\n")

        await orchestrator.process_weekly_data_dump(str(week_dir))

    print("\n✅ All weeks processed!")

asyncio.run(process_all_weeks())
```

### Method 3: Using Claude Code Interactive Agent

Create a Claude Code agent that processes your data:

```python
# weekly_processor_agent.py
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from orchestrator.master_orchestrator import MasterOrchestrator

async def create_processing_agent():
    """Create agent that processes weekly data dumps."""

    async with ClaudeSDKClient(
        options=ClaudeAgentOptions(
            model="claude-sonnet-4-5",
            permission_mode="auto",  # Auto-process
        )
    ) as agent:

        await agent.query("""
            Process my weekly data dump at data/2026_week_01/.

            This directory contains:
            - Chat exports from Claude, ChatGPT, Perplexity
            - Medical records (appointments, labs, vitals)
            - Work timesheets and incident reports

            Tasks:
            1. Classify all files by type
            2. Extract incidents from chat data
            3. Parse medical records
            4. Process work timesheets
            5. Build unified timeline
            6. Export to Obsidian vault

            Use the MasterOrchestrator to handle this.
        """)

        async for msg in agent.receive_response():
            print(msg.result if hasattr(msg, 'result') else msg)

# Run it
import asyncio
asyncio.run(create_processing_agent())
```

## Supported Data Types

### 📱 Chat Data

**Supported formats:**
- ✅ Claude conversation exports (JSON)
- ✅ ChatGPT exports (conversations.json)
- ✅ Perplexity research (Markdown, JSON)

**What gets extracted:**
- Incident mentions
- Event descriptions
- Dates and times
- Entity references (people, places)
- Confidence scores

**Example chat file:**
```json
{
  "conversations": [
    {
      "id": "conv_123",
      "messages": [
        {
          "role": "user",
          "content": "I had severe back pain on January 6th after lifting at work...",
          "timestamp": "2026-01-07T10:00:00Z"
        }
      ]
    }
  ]
}
```

### 🏥 Medical Data

**Supported types:**
- ✅ Lab results (PDF, text, CSV)
- ✅ Imaging results (MRI, CT, X-ray reports)
- ✅ Doctor visit summaries
- ✅ Vital signs (CSV, text)
- ✅ Medical appointments

**What gets extracted:**
- Test names and values
- Abnormal flags
- Provider names
- Dates and locations
- Findings and impressions

**Example lab result:**
```
Patient: John Doe
Test Date: 2026-01-06

Results:
- Glucose: 95 mg/dL (Reference: 70-100) ✓
- Hemoglobin: 13.2 g/dL (Reference: 13.5-17.5) ↓ LOW
- WBC: 7.2 K/uL (Reference: 4.5-11.0) ✓
```

### 💼 Work Data

**Supported types:**
- ✅ Timesheets (Excel, CSV, PDF)
- ✅ Work incident reports
- ✅ Hours tracking
- ✅ Pay and damages documentation
- ✅ Work communications

**What gets extracted:**
- Hours worked (regular + overtime)
- Incident details
- Pay calculations
- Lost wages
- Action items from communications

**Example timesheet:**
```csv
Date,Clock In,Clock Out,Hours,Overtime
2026-01-06,08:00,17:30,8.5,0.5
2026-01-07,08:00,16:00,8.0,0.0
```

### 📚 Research & Notes

**Supported types:**
- ✅ Research notes (Markdown, text)
- ✅ Prior case analysis
- ✅ Perplexity research
- ✅ Legal/medical research

## Output: Obsidian Vault

### Generated Structure

```
obsidian_vault/
├── 2026-W01/
│   ├── 2026-W01_Summary.md          # Week overview
│   ├── 2026-W01_Timeline.md         # Complete timeline
│   ├── incidents/
│   │   ├── 2026-01-06_symptom_back_pain.md
│   │   ├── 2026-01-07_work_incident.md
│   │   └── ...
│   ├── medical/
│   │   ├── 2026-01-06_lab_results.md
│   │   ├── 2026-01-09_vitals.md
│   │   └── ...
│   └── work/
│       ├── 2026-W01_timesheet_summary.md
│       └── 2026-01-07_incident_report.md
│
└── entities/
    ├── John_Doe.md
    ├── Dr_Smith.md
    ├── Company_ABC.md
    └── ...
```

### Example Week Summary Note

```markdown
---
type: weekly_summary
week: 2026-W01
chat_incidents: 20
medical_events: 3
work_events: 2
total_timeline_events: 25
---

# 2026-W01 Weekly Summary

## Data Sources Processed

### 📱 Chat Data
- Incidents extracted: 20
- Sources: Claude (12), ChatGPT (8)

### 🏥 Medical Data
- Lab results: 2
- Vitals tracked: 1
- Events processed: 3

### 💼 Work Data
- Hours worked: 42.5 (40 regular, 2.5 overtime)
- Incidents: 1 work injury
- Events processed: 2

## Timeline
[[2026-W01_Timeline|View Complete Timeline]]

## Key Events
- 2026-01-06: Severe back pain after lifting
- 2026-01-06: Lab results (1 abnormal value)
- 2026-01-07: Work incident report filed
- 2026-01-09: Doctor visit for back pain
- 2026-01-09: Baseline vitals recorded

## Cross-References
- Work incident on 1/7 correlates with back pain on 1/6
- Doctor visit on 1/9 follows up on 1/6 symptom
- Lab results on 1/6 ordered prior to doctor visit

## Next Steps
- [ ] Review timeline accuracy
- [ ] Add imaging results when received
- [ ] Cross-reference with calendar
- [ ] Follow up on abnormal lab values
```

## Advanced: Custom Processing Rules

### Filter by Data Type

```python
# Only process medical data
orchestrator = MasterOrchestrator()
classifications = orchestrator.classifier.classify_directory("data/2026_week_01")

medical_only = {
    k: v for k, v in classifications.items()
    if k.startswith("medical_")
}

# Process just medical files
results = await orchestrator._process_medical_data(
    sum(medical_only.values(), []),
    week_id="2026-W01"
)
```

### Custom Confidence Thresholds

```python
# Only include high-confidence incidents
results = await orchestrator.process_weekly_data_dump("data/2026_week_01")

high_confidence = [
    incident for incident in results["chat_incidents"]
    if incident["confidence"] >= 0.8
]

print(f"High-confidence incidents: {len(high_confidence)}")
```

### Link Incidents Across Sources

```python
# Find incidents mentioned in both chats AND medical records
from datetime import datetime, timedelta

def find_correlated_events(chat_incidents, medical_events):
    """Find events mentioned in multiple sources."""
    correlations = []

    for chat_inc in chat_incidents:
        chat_date = datetime.fromisoformat(chat_inc["date"])

        for med_event in medical_events:
            med_date = datetime.fromisoformat(med_event["date"])

            # Events within 3 days
            if abs((chat_date - med_date).days) <= 3:
                correlations.append({
                    "chat": chat_inc["description"],
                    "medical": med_event["summary"],
                    "time_diff_days": (med_date - chat_date).days
                })

    return correlations

# Use it
correlations = find_correlated_events(
    results["chat_incidents"],
    results["medical_events"]
)

for corr in correlations:
    print(f"Chat: {corr['chat']}")
    print(f"Medical: {corr['medical']}")
    print(f"Gap: {corr['time_diff_days']} days\n")
```

## Privacy & Security

### HIPAA Compliance for Medical Data

The system handles medical data locally:
- ✅ No cloud uploads (except to Anthropic API for extraction)
- ✅ Files stay on your machine
- ✅ Obsidian vault is local
- ⚠️ API calls to Claude include content - ensure compliance

**For strict HIPAA compliance:**
- Use local LLM instead of API
- Or de-identify data before processing
- Or use Anthropic's HIPAA-compliant offerings

### Data Retention

```python
# Auto-delete source files after processing
orchestrator = MasterOrchestrator()

results = await orchestrator.process_weekly_data_dump("data/2026_week_01")

# Delete sensitive source files
import shutil
shutil.rmtree("data/2026_week_01/medical")  # Keep only Obsidian vault
```

## Troubleshooting

### Files Not Being Classified

**Problem**: Files showing as "unknown" type

**Solution**: Check filename patterns or file content:

```python
classifier = DataTypeClassifier()
result = classifier.classify_file("mystery_file.pdf")

print(f"Detected features: {result.detected_features}")
# Might show: ["no_recognizable_patterns"]

# Add custom classification rule
def custom_classify(file_path):
    if "mycompany" in file_path.lower():
        return "work_incident"
    return classifier.classify_file(file_path).data_type
```

### Missing Incidents

**Problem**: Chat processing finds fewer incidents than expected

**Solution**: Ensure chats explicitly mention dates and events:

```
❌ "Something happened last week"
✅ "On January 6, 2026, I experienced severe back pain"

❌ "Went to the doctor"
✅ "Doctor appointment with Dr. Smith on 1/9/2026 for back pain"
```

### Export Format Issues

**Problem**: ChatGPT export format not recognized

**Solution**: Ensure you're using the official export format:
- ChatGPT Settings → Data Controls → Export Data
- Wait for email with `conversations.json`

## Next Steps

1. **Start simple**: Process one week manually
2. **Automate**: Set up weekly script to auto-process new data
3. **Refine**: Adjust classification rules for your specific files
4. **Integrate**: Add calendar correlation, Perplexity verification
5. **Visualize**: Build interactive timeline viewer

## Summary

You now have a complete system that:
✅ Auto-classifies any data file type
✅ Routes to specialized processors
✅ Extracts incidents from chats
✅ Parses medical records
✅ Processes work timesheets
✅ Builds unified timelines
✅ Exports to Obsidian with cross-references

**One command to process everything:**
```python
await orchestrator.process_weekly_data_dump("data/2026_week_01")
```
