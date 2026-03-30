# RescueCoord

Микросервисная система диспетчеризации и мониторинга в мультиагентной системе поисково-спасательных робототехнических средств.

## Архитектура

Система состоит из двух микросервисов:

- **Coordination Service** (порт 8001) — управление миссиями, распределение зон поиска и маршрутов между роботами и БПЛА
- **Monitoring Service** (порт 8002) — сбор телеметрии, отслеживание состояния агентов, формирование тревожных событий

Каждый сервис использует собственную базу данных PostgreSQL. Межсервисное взаимодействие — через REST API (HTTPX).

```
┌──────────────┐     HTTP/REST      ┌──────────────────┐
│  Coordination │ ──────────────────►│   Monitoring      │
│  Service      │◄──────────────────│   Service         │
│  :8001        │                    │   :8002           │
└──────┬───────┘                    └───────┬──────────┘
       │                                     │
       ▼                                     ▼
┌──────────────┐                    ┌──────────────────┐
│  coord_db    │                    │  monitoring_db    │
│  PostgreSQL  │                    │  PostgreSQL       │
│  :5433       │                    │  :5434            │
└──────────────┘                    └──────────────────┘
```

## Технологический стек

| Компонент | Технология |
|-----------|------------|
| Язык | Python 3.11 |
| Веб-фреймворк | FastAPI |
| ASGI-сервер | Uvicorn |
| Валидация | Pydantic v2 |
| ORM | SQLAlchemy 2.0 (async) |
| Миграции | Alembic |
| СУБД | PostgreSQL 16 |
| HTTP-клиент | HTTPX |
| Контейнеризация | Docker, Docker Compose |
| Тестирование | pytest, pytest-asyncio |

## Быстрый старт

### Запуск через Docker Compose

```bash
docker-compose up --build
```

Сервисы будут доступны:
- Coordination Service: http://localhost:8001
- Monitoring Service: http://localhost:8002
- Swagger UI: http://localhost:8001/docs и http://localhost:8002/docs

### Применение миграций

```bash
# Coordination Service
cd coordination_service
alembic upgrade head

# Monitoring Service
cd monitoring_service
alembic upgrade head
```

## API

### Coordination Service (порт 8001)

| Метод | URI | Описание |
|-------|-----|----------|
| POST | `/api/v1/missions` | Создание новой миссии |
| GET | `/api/v1/missions/{id}` | Получение информации о миссии |
| POST | `/api/v1/missions/{id}/plan` | Формирование плана распределения зон |
| GET | `/api/v1/missions/{id}/assignments` | Получение назначений по агентам и зонам |
| PATCH | `/api/v1/routes/{id}/reassign` | Перераспределение маршрута |
| GET | `/health` | Проверка работоспособности |

### Monitoring Service (порт 8002)

| Метод | URI | Описание |
|-------|-----|----------|
| POST | `/api/v1/telemetry` | Приём телеметрии от робота или БПЛА |
| GET | `/api/v1/agents/{id}/status` | Получение состояния агента |
| GET | `/api/v1/agents/available` | Список доступных агентов |
| POST | `/api/v1/alerts` | Регистрация тревожного события |
| GET | `/api/v1/alerts` | Получение списка тревог |
| GET | `/health` | Проверка работоспособности |

## Примеры запросов

### Создание миссии

```bash
curl -X POST http://localhost:8001/api/v1/missions \
  -H "Content-Type: application/json" \
  -d '{"incident_type": "BUILDING_COLLAPSE", "location": "Sector A", "priority": "HIGH", "required_agents": 6}'
```

### Отправка телеметрии

```bash
curl -X POST http://localhost:8002/api/v1/telemetry \
  -H "Content-Type: application/json" \
  -d '{"agent_id": 12, "latitude": 55.753, "longitude": 37.621, "battery_level": 41.5, "speed": 2.1, "link_status": "ONLINE", "mission_status": "IN_PROGRESS"}'
```

## Python SDK клиент

```python
import asyncio
from client.coordination_client import CoordinationClient
from client.monitoring_client import MonitoringClient

async def main():
    # Coordination
    async with CoordinationClient("http://localhost:8001") as coord:
        mission = await coord.create_mission("FIRE", "Building B", "HIGH", 3)
        zones = await coord.plan_mission(mission.id)
        assignments = await coord.get_assignments(mission.id)

    # Monitoring
    async with MonitoringClient("http://localhost:8002") as mon:
        telemetry = await mon.send_telemetry(
            agent_id=1, latitude=55.75, longitude=37.62,
            battery_level=85.0, speed=2.0,
            link_status="ONLINE", mission_status="IN_PROGRESS"
        )
        status = await mon.get_agent_status(1)
        alerts = await mon.get_alerts()

asyncio.run(main())
```

## Тестирование

### Установка зависимостей для тестов

```bash
pip install fastapi uvicorn sqlalchemy[asyncio] asyncpg aiosqlite pydantic pydantic-settings httpx alembic pytest pytest-asyncio
```

### Запуск модульных тестов

```bash
# Monitoring Service
cd monitoring_service
pytest tests/ -v

# Coordination Service
cd coordination_service
pytest tests/ -v

# Client + Integration tests
cd ..  # корень проекта
pytest tests/ -v
```

## Структура проекта

```
RescueCoord/
├── docker-compose.yml
├── README.md
├── coordination_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   └── services/
│   └── tests/
├── monitoring_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   └── services/
│   └── tests/
├── client/
│   ├── coordination_client.py
│   ├── monitoring_client.py
│   └── models.py
└── tests/
    ├── test_coordination_client.py
    ├── test_monitoring_client.py
    └── test_integration.py
```



docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build	Разработка (hot-reload, volumes)
docker compose -f docker-compose.yml -f docker-compose.test.yml up --build	Тестирование
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build	Продакшен (без открытых портов БД, restart: always)