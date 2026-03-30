from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import telemetry, agents, alerts, health
from .database import engine
# Import all models so SQLAlchemy includes them in metadata
from .models.telemetry import Base
from .models import telemetry as telemetry_model, agent_status, alert, sensor_event  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="RescueCoord Monitoring Service",
    description="Сервис мониторинга и ситуационной осведомлённости для поисково-спасательных робототехнических средств",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(telemetry.router)
app.include_router(agents.router)
app.include_router(alerts.router)
app.include_router(health.router)
