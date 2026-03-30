"""
simulate_agents.py — полная демонстрация сценария работы RescueCoord

Сценарий:
  1. Регистрация агентов (дронов/роботов) через Monitoring Service
  2. Клиент создаёт миссию в Coordination Service
  3. Coordination Service планирует миссию: назначает подзоны агентам
  4. Каждый назначенный агент параллельно выполняет свою подзону,
     периодически отправляя телеметрию в Monitoring Service

Запуск (сервисы должны быть подняты через docker compose up):
    python simulate_agents.py
"""

import asyncio
import math
import random

from client.coordination_client import CoordinationClient
from client.monitoring_client import MonitoringClient
from client.models import AssignmentModel

# ─── Настройки ────────────────────────────────────────────────────────────────
COORD_URL      = "http://localhost:8001"
MONITOR_URL    = "http://localhost:8002"

NUM_AGENTS     = 3       # сколько агентов зарегистрировать
REQUIRED       = 3       # сколько агентов нужно для миссии
INTERVAL_SEC   = 3       # интервал между отправками телеметрии (сек)
STEPS          = 6       # шагов движения в подзоне

# ─── Консольные цвета ─────────────────────────────────────────────────────────
_COLORS = ["\033[94m", "\033[92m", "\033[93m", "\033[96m", "\033[95m"]
RESET   = "\033[0m"
BOLD    = "\033[1m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"

def color(agent_id: int) -> str:
    return _COLORS[(agent_id - 1) % len(_COLORS)]

def section(title: str) -> None:
    print(f"\n{BOLD}{CYAN}{'─' * 55}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'─' * 55}{RESET}")


# ─── Шаг 1: регистрация агентов ───────────────────────────────────────────────
async def register_agents(mon: MonitoringClient) -> None:
    """Отправить первичную телеметрию, чтобы агенты появились в Monitoring Service."""
    section("Шаг 1: Регистрация агентов в Monitoring Service")
    for agent_id in range(1, NUM_AGENTS + 1):
        battery = 90.0 - (agent_id - 1) * 5.0
        await mon.send_telemetry(
            agent_id=agent_id,
            latitude=55.7550 + agent_id * 0.001,
            longitude=37.6170 + agent_id * 0.001,
            battery_level=battery,
            speed=0.0,
            link_status="ONLINE",
            mission_status="PENDING",
        )
        print(f"  {color(agent_id)}[Агент-{agent_id}]{RESET} зарегистрирован | "
              f"battery={battery:.0f}% | ONLINE | PENDING")

    available = await mon.get_available_agents()
    print(f"\n  {GREEN}✓ Доступно агентов: {len(available)}{RESET}")


# ─── Шаг 2+3: создание и планирование миссии ──────────────────────────────────
async def create_and_plan_mission(coord: CoordinationClient) -> list[AssignmentModel]:
    """Создать миссию и запустить планирование — координатор назначает подзоны."""
    section("Шаг 2: Клиент создаёт миссию в Coordination Service")

    mission = await coord.create_mission(
        incident_type="BUILDING_COLLAPSE",
        location="Район Сокольники, кв. 7",
        priority="HIGH",
        required_agents=REQUIRED,
    )
    print(f"  {GREEN}✓ Миссия #{mission.id} создана{RESET}")
    print(f"    Тип: {mission.incident_type}")
    print(f"    Район: {mission.location}")
    print(f"    Приоритет: {mission.priority}")
    print(f"    Статус: {mission.status}")

    section("Шаг 3: Coordination Service планирует миссию")
    print(f"  Запрос доступных агентов из Monitoring Service...")

    zones = await coord.plan_mission(mission.id)
    print(f"  {GREEN}✓ Спланировано подзон: {len(zones)}{RESET}")

    assignments = await coord.get_assignments(mission.id)
    print(f"\n  Распределение подзон по агентам:")
    for a in assignments:
        print(f"    {color(a.agent_id or 0)}[Агент-{a.agent_id} «{a.agent_name}»]{RESET}"
              f" → подзона {BOLD}{a.zone_code}{RESET}"
              f" (маршрут #{a.route_id}, статус: {a.route_status})")

    return assignments


# ─── Шаг 4: агент выполняет подзону и шлёт телеметрию ─────────────────────────
async def fly_agent(
    agent_id: int,
    zone_code: str,
    agent_name: str,
    mon: MonitoringClient,
) -> None:
    """Имитирует движение агента по подзоне с периодической отправкой телеметрии."""
    c     = color(agent_id)
    label = f"{c}[{agent_name} → {zone_code}]{RESET}"

    lat     = 55.7550 + agent_id * 0.001
    lon     = 37.6170 + agent_id * 0.001
    dlat    = random.choice([0.0004, -0.0003, 0.0005])
    dlon    = random.choice([0.0006, 0.0008, -0.0004])
    battery = 90.0 - (agent_id - 1) * 5.0

    # Небольшой разброс чтобы агенты стартовали не одновременно
    await asyncio.sleep(random.uniform(0, 1.0))

    print(f"  {label} {YELLOW}выдвигается на позицию...{RESET}")

    for step in range(1, STEPS + 1):
        lat     += dlat + random.uniform(-0.0001, 0.0001)
        lon     += dlon + random.uniform(-0.0001, 0.0001)
        battery  = max(5.0, battery - 2.0 + random.uniform(-0.5, 0.5))
        speed    = round(random.uniform(1.5, 4.0), 1)
        link     = "ONLINE" if battery > 20 else "DEGRADED"

        await mon.send_telemetry(
            agent_id=agent_id,
            latitude=round(lat, 5),
            longitude=round(lon, 5),
            battery_level=round(battery, 1),
            speed=speed,
            link_status=link,
            mission_status="IN_PROGRESS",
        )

        bar  = "█" * math.ceil(battery / 100 * 10) + "░" * (10 - math.ceil(battery / 100 * 10))
        print(f"  {label} шаг {step}/{STEPS} | "
              f"({lat:.4f}, {lon:.4f}) | "
              f"⚡[{bar}]{battery:.1f}% | "
              f"{speed} m/s | {link}")

        if step < STEPS:
            await asyncio.sleep(INTERVAL_SEC)

    # Завершение подзоны
    await mon.send_telemetry(
        agent_id=agent_id,
        latitude=round(lat, 5),
        longitude=round(lon, 5),
        battery_level=round(battery, 1),
        speed=0.0,
        link_status="ONLINE",
        mission_status="COMPLETED",
    )
    print(f"  {label} {GREEN}{BOLD}✓ подзона {zone_code} выполнена{RESET}"
          f" | итог battery={battery:.1f}%")


# ─── Главный сценарий ─────────────────────────────────────────────────────────
async def main() -> None:
    print(f"\n{BOLD}{'═' * 55}")
    print(f"  RescueCoord — полная демонстрация сценария")
    print(f"{'═' * 55}{RESET}")

    async with MonitoringClient(MONITOR_URL) as mon, \
               CoordinationClient(COORD_URL) as coord:

        # 1. Зарегистрировать агентов
        await register_agents(mon)

        # 2+3. Создать миссию и получить назначения
        assignments = await create_and_plan_mission(coord)

        if not assignments:
            print(f"\n{YELLOW}Нет назначений — агентов не хватает или нет доступных.{RESET}")
            return

        # 4. Запустить всех назначенных агентов параллельно
        section("Шаг 4: Агенты выполняют подзоны, передавая телеметрию")

        tasks = [
            asyncio.create_task(
                fly_agent(
                    agent_id=a.agent_id,
                    zone_code=a.zone_code,
                    agent_name=a.agent_name or f"Agent-{a.agent_id}",
                    mon=mon,
                )
            )
            for a in assignments
            if a.agent_id is not None
        ]
        await asyncio.gather(*tasks)

    print(f"\n{BOLD}{GREEN}{'═' * 55}")
    print(f"  Миссия завершена. Все агенты выполнили задание.")
    print(f"{'═' * 55}{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
