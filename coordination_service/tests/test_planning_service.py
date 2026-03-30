import pytest

from app.services.planning_service import _generate_grid_zones, _generate_route_points


def test_generate_grid_zones():
    zones = _generate_grid_zones(4)
    assert len(zones) == 4
    codes = [z["zone_code"] for z in zones]
    assert codes == ["ZONE-A", "ZONE-B", "ZONE-C", "ZONE-D"]
    for z in zones:
        assert z["geometry"]["type"] == "Polygon"
        assert len(z["geometry"]["coordinates"]) == 5  # closed polygon


def test_generate_grid_zones_single():
    zones = _generate_grid_zones(1)
    assert len(zones) == 1
    assert zones[0]["zone_code"] == "ZONE-A"


def test_generate_route_points():
    geometry = {
        "type": "Polygon",
        "coordinates": [
            [37.62, 55.75],
            [37.625, 55.75],
            [37.625, 55.755],
            [37.62, 55.755],
            [37.62, 55.75],
        ],
    }
    points = _generate_route_points(geometry)
    assert len(points) == 4


def test_generate_route_points_short():
    geometry = {"coordinates": [[1, 2]]}
    points = _generate_route_points(geometry)
    assert len(points) == 1
