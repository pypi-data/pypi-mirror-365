from pydantic import BaseModel
from typing import Optional


class TripRequest(BaseModel):
    from_place: str
    to_place: str
    departure_time: Optional[str] = None


class DeparturesRequest(BaseModel):
    stop_name: str
    when: Optional[str] = None
    arrive_by: Optional[str] = None
    mode: Optional[str] = None


class CoordinatesRequest(BaseModel):
    latitude: float
    longitude: float


class NearbyStopsRequest(CoordinatesRequest):
    radius: Optional[int] = 500


class GeocodeRequest(BaseModel):
    name: str


class StopMetadataRequest(BaseModel):
    stop_id: Optional[str] = None
    stop_name: Optional[str] = None


class ListStopsRequest(BaseModel):
    name_contains: Optional[str] = None
    zone: Optional[str] = None
