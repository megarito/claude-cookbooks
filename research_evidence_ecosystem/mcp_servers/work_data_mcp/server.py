"""
Work Data MCP Server - Process timesheets, incidents, communications, hours.

Handles:
- Timesheets and hour tracking
- Work incident reports
- Pay and damages
- Work communications
- Schedule management
"""

from datetime import datetime, timedelta
from pydantic import BaseModel


class Timesheet(BaseModel):
    """Work timesheet entry"""

    entry_id: str
    date: datetime
    employee_id: str
    clock_in: datetime | None = None
    clock_out: datetime | None = None
    hours_worked: float
    overtime_hours: float = 0.0
    project_code: str | None = None
    notes: str | None = None


class WorkIncident(BaseModel):
    """Work-related incident report"""

    incident_id: str
    incident_date: datetime
    reported_date: datetime
    incident_type: str  # "injury", "safety", "harassment", "property"
    severity: str  # "minor", "moderate", "severe", "critical"
    description: str
    location: str
    witnesses: list[str] = []
    actions_taken: str | None = None
    follow_up_required: bool = False


class PayRecord(BaseModel):
    """Pay and compensation record"""

    pay_id: str
    pay_period_start: datetime
    pay_period_end: datetime
    regular_hours: float
    overtime_hours: float
    regular_rate: float
    overtime_rate: float
    total_pay: float
    deductions: dict[str, float] = {}
    net_pay: float


class WorkDataMCP:
    """MCP Server for work-related data processing."""

    tools = [
        {
            "name": "parse_timesheet",
            "description": "Extract work hours from timesheet files",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "format": {
                        "type": "string",
                        "enum": ["csv", "excel", "pdf", "json"],
                    },
                    "calculate_overtime": {
                        "type": "boolean",
                        "default": True,
                    },
                },
                "required": ["file_path"],
            },
        },
        {
            "name": "parse_incident_report",
            "description": "Extract details from work incident reports",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "extract_witnesses": {
                        "type": "boolean",
                        "default": True,
                    },
                    "link_to_compensation": {
                        "type": "boolean",
                        "default": True,
                        "description": "Link to workers comp claims",
                    },
                },
                "required": ["file_path"],
            },
        },
        {
            "name": "calculate_damages",
            "description": "Calculate pay damages and compensation",
            "input_schema": {
                "type": "object",
                "properties": {
                    "incident_id": {"type": "string"},
                    "damage_type": {
                        "type": "string",
                        "enum": ["wage_loss", "medical", "pain_suffering", "punitive"],
                    },
                    "time_period": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "string"},
                            "end": {"type": "string"},
                        },
                    },
                },
                "required": ["incident_id", "damage_type"],
            },
        },
        {
            "name": "track_work_communications",
            "description": "Organize and track work-related communications",
            "input_schema": {
                "type": "object",
                "properties": {
                    "communications_dir": {"type": "string"},
                    "filter_type": {
                        "type": "string",
                        "enum": ["email", "slack", "teams", "all"],
                    },
                    "extract_action_items": {
                        "type": "boolean",
                        "default": True,
                    },
                },
                "required": ["communications_dir"],
            },
        },
        {
            "name": "correlate_hours_with_incidents",
            "description": "Link work hours to incident reports for wage loss claims",
            "input_schema": {
                "type": "object",
                "properties": {
                    "incident_date": {"type": "string"},
                    "timesheet_files": {"type": "array", "items": {"type": "string"}},
                    "calculate_lost_wages": {
                        "type": "boolean",
                        "default": True,
                    },
                },
                "required": ["incident_date", "timesheet_files"],
            },
        },
    ]

    async def execute_tool(self, name: str, arguments: dict):
        """Execute work data tool."""
        if name == "parse_timesheet":
            return await self._parse_timesheet(arguments)
        elif name == "calculate_damages":
            return await self._calculate_damages(arguments)
        # ... other tools

    async def _parse_timesheet(self, arguments: dict) -> dict:
        """Parse timesheet file."""
        file_path = arguments["file_path"]
        calculate_overtime = arguments.get("calculate_overtime", True)

        # In production: parse CSV/Excel/PDF with Claude
        return {
            "success": True,
            "pay_period": "2026-01-01 to 2026-01-07",
            "total_hours": 42.5,
            "regular_hours": 40.0,
            "overtime_hours": 2.5,
            "entries": [
                {
                    "date": "2026-01-06",
                    "clock_in": "08:00",
                    "clock_out": "17:30",
                    "hours": 8.5,
                    "overtime": 0.5,
                }
            ],
        }

    async def _calculate_damages(self, arguments: dict) -> dict:
        """Calculate compensation for damages."""
        incident_id = arguments["incident_id"]
        damage_type = arguments["damage_type"]

        # Calculate based on type
        if damage_type == "wage_loss":
            return {
                "damage_type": "wage_loss",
                "incident_id": incident_id,
                "days_lost": 10,
                "daily_rate": 240.00,
                "total_loss": 2400.00,
                "calculation_method": "actual_wages",
            }

        return {"damage_type": damage_type, "amount": 0.0}
