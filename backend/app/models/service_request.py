# app/models/service_request.py
#
# Purpose:
#   Describes the shape of a "service_request" document as stored in
#   MongoDB, and defines the request lifecycle rules (which status can
#   move to which). A ServiceRequest is what an Employee raises to report
#   an AC/electrical/housekeeping/meeting room/security/IT issue.
#
# Lifecycle:
#   NEW -> ASSIGNED -> IN_PROGRESS -> RESOLVED -> CLOSED
#   Plus the branch:
#   IN_PROGRESS -> ON_HOLD -> IN_PROGRESS
#
# A service_request document in MongoDB looks like this:
#   {
#       "id": "「uuid4 string」",
#       "title": "AC not cooling in Conference Room B",
#       "description": "...",
#       "category_id": "「category's uuid4 string」",
#       "location_id": "「location's uuid4 string」",
#       "status": "new",
#       "created_by": "「employee user's uuid4 string」",
#       "assigned_to": None,               # set once a Facility Manager assigns staff
#       "created_at": "2026-09-22T10:00:00",
#       "updated_at": "2026-09-22T10:00:00"
#   }

from enum import Enum


class RequestStatus(str, Enum):
    """The fixed set of statuses a service request can be in."""
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    RESOLVED = "resolved"
    CLOSED = "closed"


# ---------------------------------------------------------------------------
# ALLOWED_TRANSITIONS is the single source of truth for the request
# lifecycle.
# Key   = current status
# Value = set of statuses it is legal to move to from there
#
# Used by the custom validation logic in app/routers/service_requests.py
# (the status-transition endpoint) to reject illegal jumps, e.g. going
# straight from NEW to RESOLVED, or moving out of CLOSED.
# ---------------------------------------------------------------------------
ALLOWED_TRANSITIONS: dict[RequestStatus, set[RequestStatus]] = {
    RequestStatus.NEW: {RequestStatus.ASSIGNED},
    RequestStatus.ASSIGNED: {RequestStatus.IN_PROGRESS},
    RequestStatus.IN_PROGRESS: {RequestStatus.ON_HOLD, RequestStatus.RESOLVED},
    RequestStatus.ON_HOLD: {RequestStatus.IN_PROGRESS},
    RequestStatus.RESOLVED: {RequestStatus.CLOSED},
    RequestStatus.CLOSED: set(),  # CLOSED is terminal — no further transitions allowed
}


def is_valid_transition(current_status: RequestStatus, new_status: RequestStatus) -> bool:
    """
    Custom application-specific rule: is moving from current_status to
    new_status allowed by the request lifecycle?
    Used by the status-transition endpoint before writing to the database.
    """
    return new_status in ALLOWED_TRANSITIONS.get(current_status, set())
