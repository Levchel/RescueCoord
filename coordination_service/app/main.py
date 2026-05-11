from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .api import missions, routes, health
from .config import settings
from .database import engine
# Import all models so SQLAlchemy includes them in metadata
from .models.mission import Base
from .models import agent, mission, route, search_zone, task_reassignment  # noqa: F401
from .telemetry import record_startup, setup_opentelemetry, StatsMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    record_startup()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="RescueCoord Coordination Service",
    description="Сервис координации и распределения задач для поисково-спасательных робототехнических средств",
    version="1.0.0",
    lifespan=lifespan,
)

setup_opentelemetry(app, settings.OTEL_ENDPOINT)
app.add_middleware(StatsMiddleware)
Instrumentator().instrument(app).expose(app, include_in_schema=False)

app.include_router(missions.router)
app.include_router(routes.router)
app.include_router(health.router)
