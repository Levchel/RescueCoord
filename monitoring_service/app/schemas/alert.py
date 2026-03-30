from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..models.enums import AlertType, AlertSeverity, AlertStatus


class AlertCreate(BaseModel):
    agent_id: int
    mission_id: Optional[int] = None
    alert_type: AlertType
    severity: AlertSeverity
    message: str = Field(..., max_length=500)


class AlertResponse(BaseModel):
    id: int
    agent_id: int
    mission_id: Optional[int] = None
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    created_at: datetime
    status: AlertStatus

    model_config = {"from_attributes": True}
