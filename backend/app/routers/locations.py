# app/routers/locations.py
#
# Purpose:
#   HTTP endpoints for the Location entity (new in this app) — a physical
#   workplace location expressed as Building -> Floor -> Room.
#   GET    /locations        -> list all locations
#   GET    /locations/{id}   -> read one location
#   POST   /locations        -> create a location
#   PUT    /locations/{id}   -> update a location
#   DELETE /locations/{id}   -> remove a location

from datetime import datetime
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.collection import Collection

from app.dependencies import get_locations_collection
from app.schemas.location import LocationCreate, LocationUpdate, LocationResponse

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(
    payload: LocationCreate,
    locations_collection: Collection = Depends(get_locations_collection),
):
    """Create a new location. POST -> create, per REST convention."""
    # Enforce a unique building/floor/room combination at the application level.
    if locations_collection.find_one(
        {"building": payload.building, "floor": payload.floor, "room": payload.room}
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A location with this building/floor/room already exists.",
        )

    location_doc = {
        "id": str(uuid4()),
        "building": payload.building,
        "floor": payload.floor,
        "room": payload.room,
        "created_at": datetime.utcnow(),
    }
    locations_collection.insert_one(location_doc)
    return location_doc


@router.get("", response_model=List[LocationResponse])
def list_locations(locations_collection: Collection = Depends(get_locations_collection)):
    """List all locations. GET -> read, per REST convention."""
    return list(locations_collection.find())


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(
    location_id: str,
    locations_collection: Collection = Depends(get_locations_collection),
):
    """Get a single location by id."""
    location_doc = locations_collection.find_one({"id": location_id})
    if not location_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return location_doc


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: str,
    payload: LocationUpdate,
    locations_collection: Collection = Depends(get_locations_collection),
):
    """Update an existing location. PUT -> update, per REST convention."""
    existing = locations_collection.find_one({"id": location_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return existing

    locations_collection.update_one({"id": location_id}, {"$set": update_data})
    return locations_collection.find_one({"id": location_id})


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: str,
    locations_collection: Collection = Depends(get_locations_collection),
):
    """Delete a location by id. DELETE -> remove, per REST convention."""
    result = locations_collection.delete_one({"id": location_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return None
