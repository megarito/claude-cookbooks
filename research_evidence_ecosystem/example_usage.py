#!/usr/bin/env python3
"""
Example: Process weekly data dump with intelligent multi-source routing.

This script demonstrates the complete workflow:
1. Classify all files in a weekly data dump
2. Route to appropriate processors (chat, medical, work)
3. Build unified timeline
4. Export to Obsidian

Usage:
    python example_usage.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from research_evidence_ecosystem.orchestrator.master_orchestrator import MasterOrchestrator
from research_evidence_ecosystem.classifiers.data_type_classifier import DataTypeClassifier


async def example_1_classify_files():
    """Example 1: Just classify files without processing."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Classify Files")
    print("=" * 70 + "\n")

    classifier = DataTypeClassifier()

    # Classify a single file
    print("Classifying individual files:\n")

    example_files = [
        "data/2026_week_01/chats/claude_export.json",
        "data/2026_week_01/medical/lab_results.pdf",
        "data/2026_week_01/work/timesheet.xlsx",
    ]

    for file_path in example_files:
        # Create example file if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        if not Path(file_path).exists():
            print(f"  (Note: {file_path} doesn't exist - showing simulated classification)")

        result = classifier._classify_by_filename(
            Path(file_path).name.lower(), Path(file_path).suffix.lower()
        )

        if result:
            print(f"File: {Path(file_path).name}")
            print(f"  Type: {result.data_type}")
            print(f"  Confidence: {result.confidence}")
            print(f"  Processor: {result.suggested_processor}")
            print()

    print("\nExample 1 complete! ✓")


async def example_2_process_week():
    """Example 2: Process complete weekly data dump."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Process Weekly Data Dump")
    print("=" * 70 + "\n")

    # Check if example data exists
    data_dir = Path("data/2026_week_01")
    if not data_dir.exists():
        print("⚠️  No example data found at data/2026_week_01/")
        print("    To run this example, create the directory structure:")
        print()
        print("    data/2026_week_01/")
        print("    ├── chats/")
        print("    │   ├── claude_export.json")
        print("    │   └── chatgpt_export.json")
        print("    ├── medical/")
        print("    │   ├── lab_results.pdf")
        print("    │   └── vitals.csv")
        print("    └── work/")
        print("        └── timesheet.xlsx")
        print()
        print("    See MULTI_SOURCE_GUIDE.md for file format examples.")
        print()
        return

    # Process the week
    orchestrator = MasterOrchestrator(obsidian_vault_path="obsidian_vault")

    results = await orchestrator.process_weekly_data_dump(
        data_directory=str(data_dir), week_id="2026-W01"
    )

    print("\nResults Summary:")
    print(f"  Chat incidents: {len(results['chat_incidents'])}")
    print(f"  Medical events: {len(results['medical_events'])}")
    print(f"  Work events: {len(results['work_events'])}")
    print(f"  Total timeline events: {len(results['timeline_events'])}")

    print("\nExample 2 complete! ✓")


async def example_3_multiple_weeks():
    """Example 3: Process multiple weeks at once."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Process Multiple Weeks")
    print("=" * 70 + "\n")

    data_root = Path("data")
    if not data_root.exists():
        print("⚠️  No data directory found. Create data/2026_week_01/, etc.")
        return

    # Find all week directories
    week_dirs = sorted(data_root.glob("2026_week_*"))

    if not week_dirs:
        print("⚠️  No week directories found matching pattern '2026_week_*'")
        return

    print(f"Found {len(week_dirs)} week directories:\n")
    for week_dir in week_dirs:
        print(f"  - {week_dir.name}")

    print("\nProcessing each week...\n")

    orchestrator = MasterOrchestrator()

    all_results = []
    for week_dir in week_dirs:
        try:
            results = await orchestrator.process_weekly_data_dump(str(week_dir))
            all_results.append(results)
        except Exception as e:
            print(f"  ✗ Error processing {week_dir.name}: {e}")

    # Summary across all weeks
    print("\n" + "=" * 70)
    print("MULTI-WEEK SUMMARY")
    print("=" * 70 + "\n")

    total_chat = sum(len(r["chat_incidents"]) for r in all_results)
    total_medical = sum(len(r["medical_events"]) for r in all_results)
    total_work = sum(len(r["work_events"]) for r in all_results)
    total_timeline = sum(len(r["timeline_events"]) for r in all_results)

    print(f"Weeks processed: {len(all_results)}")
    print(f"Total chat incidents: {total_chat}")
    print(f"Total medical events: {total_medical}")
    print(f"Total work events: {total_work}")
    print(f"Total timeline events: {total_timeline}")

    print("\nExample 3 complete! ✓")


async def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("MULTI-SOURCE DATA PROCESSING EXAMPLES")
    print("=" * 70)

    # Run example 1 (always works - no data needed)
    await example_1_classify_files()

    # Ask user which other examples to run
    print("\n" + "=" * 70)
    print("Additional examples require sample data in data/ directory.")
    print("=" * 70)

    try:
        # Try example 2
        await example_2_process_week()

        # Try example 3
        await example_3_multiple_weeks()

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
        return

    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Review MULTI_SOURCE_GUIDE.md for detailed usage")
    print("  2. Set up your weekly data directory structure")
    print("  3. Export your chats, medical records, work data")
    print("  4. Run: await orchestrator.process_weekly_data_dump('data/YOUR_WEEK')")
    print()


if __name__ == "__main__":
    asyncio.run(main())
