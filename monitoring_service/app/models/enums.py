import enum


class LinkStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"


class MissionStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABORTED = "ABORTED"


class HealthState(str, enum.Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    OFFLINE = "OFFLINE"


class SensorType(str, enum.Enum):
    CAMERA = "CAMERA"
    THERMAL = "THERMAL"
    GAS = "GAS"


class AlertType(str, enum.Enum):
    HUMAN_DETECTED = "HUMAN_DETECTED"
    OBSTACLE = "OBSTACLE"
    GAS_LEAK = "GAS_LEAK"
    OVERHEAT = "OVERHEAT"
    LOW_BATTERY = "LOW_BATTERY"
    LINK_LOST = "LINK_LOST"
    MALFUNCTION = "MALFUNCTION"
    FIRE = "FIRE"


class AlertSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
