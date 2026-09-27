# app/schemas/service_request.py
#
# Purpose:
#   Defines the Pydantic models for the ServiceRequest entity. Requests are
#   split into several narrow input schemas (instead of one big
#   "update everything" schema) because different roles change different
#   things:
#     - ServiceRequestCreate       -> Employee raises a new request
#     - ServiceRequestUpdate       -> edit request details (title/description/category/location)
#     - ServiceRequestAssign       -> Facility Manager assigns/reassigns support staff
#     - ServiceRequestStatusUpdate -> Support Staff/Facility Manager moves the
#                                     request through its lifecycle (NEW -> ASSIGNED -> ...)
#
# Concepts demonstrated here:
#   - Field validation  -> Field(...) rules below
#   - Custom validators -> field_validator on title/description (reject blank text)
#   - Optional/default  -> ServiceRequestUpdate fields default to None

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.service_request import RequestStatus


class ServiceRequestCreate(BaseModel):
    """Data required from the client when raising a new request (POST /service-requests)."""

    title: str = Field(..., min_length=3, max_length=150, description="Short summary of the issue")
    description: str = Field(..., min_length=5, max_length=2000, description="Full details of the issue")
    category_id: str = Field(..., description="id of an existing Category")
    location_id: str = Field(..., description="id of an existing Location (Building/Floor/Room)")
    created_by: str = Field(..., description="id of the Employee raising this request")

    @field_validator("title", "description")
    @classmethod
    def not_blank(cls, value: str) -> str:
        """
        Custom validator: rejects a title/description that is empty or only
        whitespace (e.g. "   "), which Field(min_length=...) alone would not
        catch since it counts whitespace characters too.
        """
        if not value.strip():
            raise ValueError("This field cannot be blank or just whitespace.")
        return value.strip()


class ServiceRequestUpdate(BaseModel):
    """
    Edit request details (NOT status or assignment — those have their own
    dedicated endpoints/schemas below). All fields Optional.
    """

    title: Optional[str] = Field(default=None, min_length=3, max_length=150)
    description: Optional[str] = Field(default=None, min_length=5, max_length=2000)
    category_id: Optional[str] = Field(default=None)
    location_id: Optional[str] = Field(default=None)


class ServiceRequestAssign(BaseModel):
    """Used by a Facility Manager to assign or reassign support staff to a request."""

    assigned_to: str = Field(..., description="id of the Support Staff to assign")


class ServiceRequestStatusUpdate(BaseModel):
    """
    Used to move a request through its lifecycle.
    Note: this schema only checks that "status" is one of the valid enum
    values. Whether the specific FROM -> TO move is legal (e.g. you can't
    jump from NEW straight to RESOLVED) depends on the request's *current*
    status in the database, so that check happens in the router, using
    app.models.service_request.is_valid_transition().
    """

    status: RequestStatus = Field(..., description="The status to move this request to")


class ServiceRequestResponse(BaseModel):
    """Shape of a service request as returned by the API."""

    id: str
    title: str
    description: str
    category_id: str
    location_id: str
    status: RequestStatus
    created_by: str
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime
