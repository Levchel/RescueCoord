from fastapi import APIRouter

from ..telemetry import get_stats

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/stats", summary="Service statistics")
async def stats():
    """Возвращает версию сервиса, дату запуска и счётчики HTTP-ответов."""
    return get_stats()
