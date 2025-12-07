from pydantic import BaseModel

class Route(BaseModel):
    distance: int
    duration: int
    polyline: str

class Address(BaseModel):
    origin_lat: float
    origin_lng: float
    destination_lat: float
    destination_lng: float