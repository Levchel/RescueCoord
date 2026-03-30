from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.telemetry import TelemetryCreate, TelemetryResponse
from ..services import telemetry_service

router = APIRouter(prefix="/api/v1", tags=["telemetry"])


@router.post("/telemetry", response_model=TelemetryResponse, status_code=status.HTTP_201_CREATED)
async def post_telemetry(data: TelemetryCreate, db: AsyncSession = Depends(get_db)):
    record = await telemetry_service.save_telemetry(db, data)
    return record
