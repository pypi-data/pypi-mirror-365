import pytest
from czechfabric_sdk.client import CzechFabricClient

@pytest.fixture
def client():
    return CzechFabricClient(api_key="test-key", base_url="http://localhost:8000")

@pytest.mark.asyncio
async def test_plan_trip(client):
    result = await client.plan_trip("Florenc", "Karlovo náměstí")
    assert "trip_plans" in result

@pytest.mark.asyncio
async def test_get_departures(client):
    result = await client.get_departures("Anděl", when="in 10 minutes")
    assert "departures" in result

@pytest.mark.asyncio
async def test_geocode(client):
    result = await client.geocode("Florenc")
    assert "coordinates" in result

@pytest.mark.asyncio
async def test_departures_by_coordinates(client):
    result = await client.departures_by_coordinates(50.087, 14.420)
    assert "departures" in result

@pytest.mark.asyncio
async def test_reverse_geocode(client):
    result = await client.reverse_geocode(50.087, 14.420)
    assert "place_name" in result

@pytest.mark.asyncio
async def test_find_all_stops_near(client):
    result = await client.find_all_stops_near(50.087, 14.420, radius=300)
    assert "stops" in result

@pytest.mark.asyncio
async def test_get_stop_metadata(client):
    result = await client.get_stop_metadata(stop_name="Dejvická")
    assert "metadata" in result

@pytest.mark.asyncio
async def test_list_all_stops(client):
    result = await client.list_all_stops(name_contains="And", zone="P")
    assert "stops" in result
