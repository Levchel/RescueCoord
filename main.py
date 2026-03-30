import asyncio
from client.coordination_client import CoordinationClient
from client.monitoring_client import MonitoringClient

async def main():
    # Регистрация агента через Monitoring SDK
    async with MonitoringClient("http://localhost:8002") as mon:
        await mon.send_telemetry(
            agent_id=1,
            latitude=55.7558,
            longitude=37.6173,
            battery_level=85.0,
            speed=0.0,
            link_status="ONLINE",
            mission_status="PENDING",
        )
        agents = await mon.get_available_agents()
        print(f"Доступно агентов: {len(agents)}")

    # Создание и планирование миссии через Coordination SDK
    async with CoordinationClient("http://localhost:8001") as coord:
        mission = await coord.create_mission(
            incident_type="FIRE",
            location="Sector A, Building 5",
            priority="HIGH",
            required_agents=2,
        )
        print(f"Создана миссия #{mission.id}, статус: {mission.status}")

        zones = await coord.plan_mission(mission.id)
        print(f"Спланировано зон: {len(zones)}")

        assignments = await coord.get_assignments(mission.id)
        for a in assignments:
            print(f"  Зона {a.zone_code} -> агент {a.agent_name}")

asyncio.run(main())