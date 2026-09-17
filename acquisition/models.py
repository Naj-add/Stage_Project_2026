from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SectionConfig:
    """
    Configuration of one warehouse section for an operation.
    """

    section_id: int
    code: str
    expected_weight: float


@dataclass
class WeighingRuntime:
    """
    Runtime state of one operation/section weighing.
    """

    operation_id: int
    section_id: int
    section_code: str

    expected_weight: float

    state: str = "IDLE"

    current_weight: float = 0.0

    stable_readings: int = 0

    is_stable: bool = False

    started_at: Optional[datetime] = None

    ready_at: Optional[datetime] = None

    validated_at: Optional[datetime] = None

    cancelled_at: Optional[datetime] = None

    validated_by: Optional[int] = None

    last_update: Optional[datetime] = None

    source_s7: str = "OPC-UA-SIMULATION"

    error_message: Optional[str] = None

    history: list[float] = field(default_factory=list)

    def to_dict(self):
        return {
            "operation_id": self.operation_id,
            "section_id": self.section_id,
            "section_code": self.section_code,
            "expected_weight": self.expected_weight,
            "current_weight": round(
                self.current_weight,
                3
            ),
            "state": self.state,
            "stable_readings": self.stable_readings,
            "is_stable": self.is_stable,
            "started_at": (
                self.started_at.isoformat()
                if self.started_at
                else None
            ),
            "ready_at": (
                self.ready_at.isoformat()
                if self.ready_at
                else None
            ),
            "validated_at": (
                self.validated_at.isoformat()
                if self.validated_at
                else None
            ),
            "cancelled_at": (
                self.cancelled_at.isoformat()
                if self.cancelled_at
                else None
            ),
            "validated_by": self.validated_by,
            "last_update": (
                self.last_update.isoformat()
                if self.last_update
                else None
            ),
            "source_s7": self.source_s7,
            "error_message": self.error_message,
        }


@dataclass
class OperationRuntime:
    """
    Runtime state of an operation containing multiple sections.
    """

    operation_id: int

    sections: dict[str, WeighingRuntime] = field(
        default_factory=dict
    )

    active_section_code: Optional[str] = None

    status: str = "PENDING"

    created_at: datetime = field(
        default_factory=datetime.now
    )

    def to_dict(self):
        return {
            "operation_id": self.operation_id,
            "status": self.status,
            "active_section_code": self.active_section_code,
            "sections": [
                section.to_dict()
                for section in self.sections.values()
            ],
            "created_at": self.created_at.isoformat(),
        }