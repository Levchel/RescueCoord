import enum


class IncidentType(str, enum.Enum):
    BUILDING_COLLAPSE = "BUILDING_COLLAPSE"
    FIRE = "FIRE"
    INDUSTRIAL_ACCIDENT = "INDUSTRIAL_ACCIDENT"
    FLOOD = "FLOOD"
    OTHER = "OTHER"


class Priority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class MissionStatusCoord(str, enum.Enum):
    CREATED = "CREATED"
    PLANNING = "PLANNING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class AgentType(str, enum.Enum):
    GROUND_ROBOT = "GROUND_ROBOT"
    UAV = "UAV"


class AvailabilityStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"


class ZoneStatus(str, enum.Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RouteStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REASSIGNED = "REASSIGNED"
