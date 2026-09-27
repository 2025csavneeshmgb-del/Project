# app/routers/service_requests.py
#
# Purpose:
#   HTTP endpoints for the ServiceRequest entity — the core entity of this
#   system.
#   GET    /service-requests                  -> list all requests
#   GET    /service-requests/{id}             -> read one request
#   POST   /service-requests                  -> create a request (Employee raises an issue)
#   PUT    /service-requests/{id}             -> update request details (title/description/category/location)
#   PATCH  /service-requests/{id}/assign      -> assign/reassign support staff (Facility Manager)
#   PATCH  /service-requests/{id}/status      -> move the request through its lifecycle
#   DELETE /service-requests/{id}             -> remove a request
#
# Every state change that matters (create / assign / status change) also
# writes an AuditLog entry, so there is always a readable history of what
# happened to a request and who did it.

from datetime import datetime
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.collection import Collection

from app.dependencies import (
    get_service_requests_collection,
    get_categories_collection,
    get_locations_collection,
    get_users_collection,
    get_audit_logs_collection,
)
from app.models.service_request import RequestStatus, is_valid_transition
from app.models.audit_log import AuditAction, build_audit_log_doc
from app.schemas.service_request import (
    ServiceRequestCreate,
    ServiceRequestUpdate,
    ServiceRequestAssign,
    ServiceRequestStatusUpdate,
    ServiceRequestResponse,
)

router = APIRouter(prefix="/service-requests", tags=["Service Requests"])


@router.post("", response_model=ServiceRequestResponse, status_code=status.HTTP_201_CREATED)
def create_service_request(
    payload: ServiceRequestCreate,
    service_requests_collection: Collection = Depends(get_service_requests_collection),
    categories_collection: Collection = Depends(get_categories_collection),
    locations_collection: Collection = Depends(get_locations_collection),
    users_collection: Collection = Depends(get_users_collection),
    audit_logs_collection: Collection = Depends(get_audit_logs_collection),
):
    """
    Create a new service request.
    POST -> create, per REST convention.
    Every new request always starts at status NEW and unassigned — the
    client cannot set these directly, which is why they aren't fields on
    ServiceRequestCreate.
    """
    # Data-integrity checks: the referenced category, location and user must actually exist.
    if not categories_collection.find_one({"id": payload.category_id}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="category_id does not match any existing category.",
        )
    if not locations_collection.find_one({"id": payload.location_id}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="location_id does not match any existing location.",
        )
    if not users_collection.find_one({"id": payload.created_by}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="created_by does not match any existing user.",
        )

    now = datetime.utcnow()
    request_doc = {
        "id": str(uuid4()),
        "title": payload.title,
        "description": payload.description,
        "category_id": payload.category_id,
        "location_id": payload.location_id,
        "status": RequestStatus.NEW,
        "created_by": payload.created_by,
        "assigned_to": None,
        "created_at": now,
        "updated_at": now,
    }
    service_requests_collection.insert_one(request_doc)

    audit_logs_collection.insert_one(
        build_audit_log_doc(
            request_id=request_doc["id"],
            action=AuditAction.CREATED,
            performed_by=payload.created_by,
            details="Request created with status 'new'.",
        )
    )
    return request_doc


@router.get("", response_model=List[ServiceRequestResponse])
def list_service_requests(service_requests_collection: Collection = Depends(get_service_requests_collection)):
    """List all service requests. GET -> read, per REST convention."""
    return list(service_requests_collection.find())


@router.get("/{request_id}", response_model=ServiceRequestResponse)
def get_service_request(
    request_id: str,
    service_requests_collection: Collection = Depends(get_service_requests_collection),
):
    """Get a single service request by id ("request_id" is a path parameter)."""
    request_doc = service_requests_collection.find_one({"id": request_id})
    if not request_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service request not found")
    return request_doc


@router.put("/{request_id}", response_model=ServiceRequestResponse)
def update_service_request(
    request_id: str,
    payload: ServiceRequestUpdate,
    service_requests_collection: Collection = Depends(get_service_requests_collection),
    categories_collection: Collection = Depends(get_categories_collection),
    locations_collection: Collection = Depends(get_locations_collection),
):
    """
    Update request details (title/description/category/location) only.
    Status and assignment are changed through their own dedicated endpoints
    below, so this endpoint deliberately does not touch them.
    """
    existing = service_requests_collection.find_one({"id": request_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service request not found")

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return existing

    if "category_id" in update_data and not categories_collection.find_one({"id": update_data["category_id"]}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="category_id does not match any existing category.",
        )
    if "location_id" in update_data and not locations_collection.find_one({"id": update_data["location_id"]}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="location_id does not match any existing location.",
        )

    update_data["updated_at"] = datetime.utcnow()
    service_requests_collection.update_one({"id": request_id}, {"$set": update_data})
    return service_requests_collection.find_one({"id": request_id})


@router.patch("/{request_id}/assign", response_model=ServiceRequestResponse)
def assign_service_request(
    request_id: str,
    payload: ServiceRequestAssign,
    service_requests_collection: Collection = Depends(get_service_requests_collection),
    users_collection: Collection = Depends(get_users_collection),
    audit_logs_collection: Collection = Depends(get_audit_logs_collection),
):
    """
    Assign or reassign support staff to a request (Facility Manager
    responsibility).

    Lifecycle rule applied here: assigning staff to a brand-new request
    naturally moves it from NEW -> ASSIGNED. If the request is being
    *reassigned* later on (already past NEW), we only change the assignee
    and leave the current status untouched — reassignment shouldn't reset
    progress that's already been made.
    """
    existing = service_requests_collection.find_one({"id": request_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service request not found")

    if not users_collection.find_one({"id": payload.assigned_to}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="assigned_to does not match any existing user.",
        )

    update_data = {"assigned_to": payload.assigned_to, "updated_at": datetime.utcnow()}
    if existing["status"] == RequestStatus.NEW:
        update_data["status"] = RequestStatus.ASSIGNED

    service_requests_collection.update_one({"id": request_id}, {"$set": update_data})

    audit_logs_collection.insert_one(
        build_audit_log_doc(
            request_id=request_id,
            action=AuditAction.ASSIGNED,
            performed_by=payload.assigned_to,
            details=f"Assigned to user '{payload.assigned_to}'.",
        )
    )
    return service_requests_collection.find_one({"id": request_id})


@router.patch("/{request_id}/status", response_model=ServiceRequestResponse)
def update_service_request_status(
    request_id: str,
    payload: ServiceRequestStatusUpdate,
    service_requests_collection: Collection = Depends(get_service_requests_collection),
    audit_logs_collection: Collection = Depends(get_audit_logs_collection),
):
    """
    Move a request through its lifecycle.
    Enforces the ALLOWED_TRANSITIONS rules from app/models/service_request.py —
    e.g. a request cannot jump straight from NEW to RESOLVED, and nothing
    can leave CLOSED once it gets there.
    """
    existing = service_requests_collection.find_one({"id": request_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service request not found")

    current_status = RequestStatus(existing["status"])
    new_status = payload.status

    if not is_valid_transition(current_status, new_status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot move request from '{current_status.value}' to '{new_status.value}'.",
        )

    service_requests_collection.update_one(
        {"id": request_id},
        {"$set": {"status": new_status, "updated_at": datetime.utcnow()}},
    )

    performed_by = existing.get("assigned_to") or existing["created_by"]
    audit_logs_collection.insert_one(
        build_audit_log_doc(
            request_id=request_id,
            action=AuditAction.STATUS_CHANGED,
            performed_by=performed_by,
            details=f"Status changed from '{current_status.value}' to '{new_status.value}'.",
        )
    )
    return service_requests_collection.find_one({"id": request_id})


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service_request(
    request_id: str,
    service_requests_collection: Collection = Depends(get_service_requests_collection),
):
    """Delete a service request by id. DELETE -> remove, per REST convention."""
    result = service_requests_collection.delete_one({"id": request_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service request not found")
    return None
