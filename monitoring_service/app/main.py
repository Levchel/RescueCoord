from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .api import telemetry, agents, alerts, health
from .config import settings
from .database import engine
# Import all models so SQLAlchemy includes them in metadata
from .models.telemetry import Base
from .models import telemetry as telemetry_model, agent_status, alert, sensor_event  # noqa: F401
from .telemetry import record_startup, setup_opentelemetry, StatsMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    record_startup()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="RescueCoord Monitoring Service",
    description="Сервис мониторинга и ситуационной осведомлённости для поисково-спасательных робототехнических средств",
    version="1.0.0",
    lifespan=lifespan,
)

setup_opentelemetry(app, settings.OTEL_ENDPOINT)
app.add_middleware(StatsMiddleware)
Instrumentator().instrument(app).expose(app, include_in_schema=False)

app.include_router(telemetry.router)
app.include_router(agents.router)
app.include_router(alerts.router)
app.include_router(health.router)
