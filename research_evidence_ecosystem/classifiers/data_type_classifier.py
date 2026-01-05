"""
Multi-Source Data Classifier - Automatically identify data types.

Classifies incoming data files/exports into categories:
- Chat exports (ChatGPT, Claude, Perplexity)
- Medical records (appointments, labs, imaging, vitals)
- Work records (timesheets, incidents, communications)
- Legal/financial (pay damages, claims)
"""

from pathlib import Path
from typing import Literal
from pydantic import BaseModel
import json
import re


class DataClassification(BaseModel):
    """Result of data classification"""

    file_path: str
    data_type: Literal[
        # Chat sources
        "chat_claude",
        "chat_chatgpt",
        "chat_perplexity",
        # Medical
        "medical_appointment",
        "medical_lab_result",
        "medical_imaging",
        "medical_visit_summary",
        "medical_vitals",
        # Work
        "work_timesheet",
        "work_incident",
        "work_communication",
        "work_hours",
        # Legal/Financial
        "legal_damages",
        "legal_claim",
        # Research
        "research_notes",
        # Unknown
        "unknown",
    ]
    confidence: float
    detected_features: list[str]
    suggested_processor: str
    metadata: dict[str, any] = {}


class DataTypeClassifier:
    """Classify data files by type using pattern matching and content analysis."""

    def classify_file(self, file_path: str) -> DataClassification:
        """
        Classify a file by examining filename, extension, and content.

        Returns:
            DataClassification with type, confidence, and routing info
        """
        path = Path(file_path)

        # Quick classification by filename patterns
        filename_lower = path.name.lower()
        extension = path.suffix.lower()

        # Try filename pattern matching first
        classification = self._classify_by_filename(filename_lower, extension)
        if classification:
            classification.file_path = file_path
            return classification

        # If filename unclear, read content for analysis
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content_sample = f.read(5000)  # First 5KB

            classification = self._classify_by_content(content_sample, extension)
            classification.file_path = file_path
            return classification

        except Exception as e:
            # Couldn't read file
            return DataClassification(
                file_path=file_path,
                data_type="unknown",
                confidence=0.0,
                detected_features=[f"error: {str(e)}"],
                suggested_processor="manual_review",
            )

    def _classify_by_filename(
        self, filename: str, extension: str
    ) -> DataClassification | None:
        """Classify based on filename patterns."""

        # Chat exports
        if "chatgpt" in filename or "conversations.json" in filename:
            return DataClassification(
                file_path="",
                data_type="chat_chatgpt",
                confidence=0.95,
                detected_features=["filename_chatgpt"],
                suggested_processor="chat_timeline_mcp",
            )

        if "claude" in filename and ("export" in filename or "conversation" in filename):
            return DataClassification(
                file_path="",
                data_type="chat_claude",
                confidence=0.95,
                detected_features=["filename_claude"],
                suggested_processor="chat_timeline_mcp",
            )

        if "perplexity" in filename:
            return DataClassification(
                file_path="",
                data_type="chat_perplexity",
                confidence=0.9,
                detected_features=["filename_perplexity"],
                suggested_processor="perplexity_mcp",
            )

        # Medical records
        if any(
            term in filename
            for term in ["lab", "labwork", "blood_test", "urinalysis", "pathology"]
        ):
            return DataClassification(
                file_path="",
                data_type="medical_lab_result",
                confidence=0.9,
                detected_features=["filename_lab"],
                suggested_processor="medical_data_mcp",
            )

        if any(term in filename for term in ["mri", "ct_scan", "xray", "x-ray", "ultrasound"]):
            return DataClassification(
                file_path="",
                data_type="medical_imaging",
                confidence=0.9,
                detected_features=["filename_imaging"],
                suggested_processor="medical_data_mcp",
            )

        if any(term in filename for term in ["visit_summary", "office_visit", "doctor_note"]):
            return DataClassification(
                file_path="",
                data_type="medical_visit_summary",
                confidence=0.85,
                detected_features=["filename_visit"],
                suggested_processor="medical_data_mcp",
            )

        if "vitals" in filename or "vital_signs" in filename:
            return DataClassification(
                file_path="",
                data_type="medical_vitals",
                confidence=0.9,
                detected_features=["filename_vitals"],
                suggested_processor="medical_data_mcp",
            )

        # Work records
        if "timesheet" in filename or "hours" in filename:
            return DataClassification(
                file_path="",
                data_type="work_timesheet",
                confidence=0.85,
                detected_features=["filename_timesheet"],
                suggested_processor="work_data_mcp",
            )

        if "incident" in filename and "report" in filename:
            return DataClassification(
                file_path="",
                data_type="work_incident",
                confidence=0.85,
                detected_features=["filename_incident"],
                suggested_processor="work_data_mcp",
            )

        # Legal/financial
        if any(term in filename for term in ["damages", "compensation", "settlement"]):
            return DataClassification(
                file_path="",
                data_type="legal_damages",
                confidence=0.8,
                detected_features=["filename_damages"],
                suggested_processor="legal_mcp",
            )

        return None  # No match by filename

    def _classify_by_content(
        self, content: str, extension: str
    ) -> DataClassification:
        """Classify by examining file content."""

        features = []
        content_lower = content.lower()

        # Check for JSON structure
        if extension == ".json":
            try:
                data = json.loads(content)

                # ChatGPT export structure
                if isinstance(data, list) and len(data) > 0:
                    if "mapping" in data[0] and "create_time" in data[0]:
                        return DataClassification(
                            file_path="",
                            data_type="chat_chatgpt",
                            confidence=0.98,
                            detected_features=["json_chatgpt_structure"],
                            suggested_processor="chat_timeline_mcp",
                            metadata={"conversations": len(data)},
                        )

                # Claude export structure
                if isinstance(data, dict) and "conversations" in data:
                    return DataClassification(
                        file_path="",
                        data_type="chat_claude",
                        confidence=0.98,
                        detected_features=["json_claude_structure"],
                        suggested_processor="chat_timeline_mcp",
                        metadata={"conversations": len(data.get("conversations", []))},
                    )

            except json.JSONDecodeError:
                pass

        # Medical content indicators
        medical_terms = [
            "blood pressure",
            "heart rate",
            "temperature",
            "patient",
            "diagnosis",
            "prescription",
            "mg/dl",
            "bpm",
            "mmhg",
        ]
        medical_count = sum(1 for term in medical_terms if term in content_lower)

        if medical_count >= 3:
            features.append(f"medical_terms_{medical_count}")

            # Specific medical subtypes
            if any(term in content_lower for term in ["wbc", "rbc", "hemoglobin", "glucose"]):
                return DataClassification(
                    file_path="",
                    data_type="medical_lab_result",
                    confidence=0.85,
                    detected_features=features + ["lab_values"],
                    suggested_processor="medical_data_mcp",
                )

            if any(term in content_lower for term in ["blood pressure", "pulse", "o2 sat"]):
                return DataClassification(
                    file_path="",
                    data_type="medical_vitals",
                    confidence=0.8,
                    detected_features=features + ["vitals_values"],
                    suggested_processor="medical_data_mcp",
                )

        # Work/timesheet indicators
        work_terms = ["hours worked", "overtime", "shift", "clock in", "clock out", "payroll"]
        work_count = sum(1 for term in work_terms if term in content_lower)

        if work_count >= 2:
            return DataClassification(
                file_path="",
                data_type="work_timesheet",
                confidence=0.75,
                detected_features=[f"work_terms_{work_count}"],
                suggested_processor="work_data_mcp",
            )

        # Legal/incident indicators
        if any(
            term in content_lower
            for term in ["incident report", "accident", "injury", "workers comp"]
        ):
            return DataClassification(
                file_path="",
                data_type="work_incident",
                confidence=0.8,
                detected_features=["incident_language"],
                suggested_processor="work_data_mcp",
            )

        # Default: unknown
        return DataClassification(
            file_path="",
            data_type="unknown",
            confidence=0.0,
            detected_features=features,
            suggested_processor="manual_review",
        )

    def classify_directory(self, directory: str) -> dict[str, list[DataClassification]]:
        """
        Classify all files in a directory.

        Returns:
            Dictionary mapping data types to lists of files
        """
        path = Path(directory)
        classifications = []

        # Find all relevant files
        for file_path in path.rglob("*"):
            if file_path.is_file():
                # Skip hidden files and common non-data files
                if file_path.name.startswith("."):
                    continue
                if file_path.suffix in [".pyc", ".log", ".tmp"]:
                    continue

                classification = self.classify_file(str(file_path))
                classifications.append(classification)

        # Group by data type
        grouped = {}
        for classification in classifications:
            data_type = classification.data_type
            if data_type not in grouped:
                grouped[data_type] = []
            grouped[data_type].append(classification)

        return grouped


# Example usage
if __name__ == "__main__":
    classifier = DataTypeClassifier()

    # Classify single file
    result = classifier.classify_file("data/2026_week_01_claude.json")
    print(f"File: {result.file_path}")
    print(f"Type: {result.data_type}")
    print(f"Confidence: {result.confidence}")
    print(f"Processor: {result.suggested_processor}")

    # Classify entire directory
    grouped = classifier.classify_directory("data/weekly_exports")
    for data_type, files in grouped.items():
        print(f"\n{data_type}: {len(files)} files")
        for f in files[:3]:  # Show first 3
            print(f"  - {f.file_path}")
