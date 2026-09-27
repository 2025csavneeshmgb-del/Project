# app/schemas/location.py
#
# Purpose:
#   Defines the Pydantic models for the Location entity — new in this app
#   compared to the IT Service Desk. Facility requests are tied to a
#   physical workplace location expressed as Building -> Floor -> Room,
#   so a ServiceRequest references a location_id (see
#   app/schemas/service_request.py) instead of describing "where" in free text.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LocationCreate(BaseModel):
    """Data required from the client when creating a new location (POST /locations)."""

    building: str = Field(..., min_length=1, max_length=100, description="Building name/code, e.g. 'Tower A'")
    floor: str = Field(..., min_length=1, max_length=50, description="Floor label, e.g. '3rd Floor'")
    room: Optional[str] = Field(default=None, max_length=50, description="Room number/name, e.g. 'Conference Room B'")


class LocationUpdate(BaseModel):
    """
    Data a client MAY send when updating a location (PUT /locations/{id}).
    All fields Optional — only sent fields are changed.
    """

    building: Optional[str] = Field(default=None, min_length=1, max_length=100)
    floor: Optional[str] = Field(default=None, min_length=1, max_length=50)
    room: Optional[str] = Field(default=None, max_length=50)


class LocationResponse(BaseModel):
    """Shape of a location as returned by the API."""

    id: str
    building: str
    floor: str
    room: Optional[str] = None
    created_at: datetime
