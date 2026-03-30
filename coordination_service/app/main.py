from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import missions, routes, health
from .database import engine
# Import all models so SQLAlchemy includes them in metadata
from .models.mission import Base
from .models import agent, mission, route, search_zone, task_reassignment  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="RescueCoord Coordination Service",
    description="Сервис координации и распределения задач для поисково-спасательных робототехнических средств",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(missions.router)
app.include_router(routes.router)
app.include_router(health.router)
