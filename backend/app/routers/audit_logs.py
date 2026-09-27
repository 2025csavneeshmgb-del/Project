# app/routers/audit_logs.py
#
# Purpose:
#   Read-only HTTP endpoints for the AuditLog entity.
#   GET /audit-logs                            -> list every audit log entry in the system
#   GET /service-requests/{request_id}/audit-logs -> list audit log entries for one request
#
# There is intentionally no POST/PUT/DELETE here — entries are only ever
# written by app/routers/service_requests.py when a request is created,
# assigned, or changes status.

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.collection import Collection

from app.dependencies import get_audit_logs_collection, get_service_requests_collection
from app.schemas.audit_log import AuditLogResponse

router = APIRouter(tags=["Audit Logs"])


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def list_all_audit_logs(audit_logs_collection: Collection = Depends(get_audit_logs_collection)):
    """List every audit log entry, most recent first."""
    return list(audit_logs_collection.find().sort("created_at", -1))


@router.get("/service-requests/{request_id}/audit-logs", response_model=List[AuditLogResponse])
def list_audit_logs_for_request(
    request_id: str,
    audit_logs_collection: Collection = Depends(get_audit_logs_collection),
    service_requests_collection: Collection = Depends(get_service_requests_collection),
):
    """List the audit trail for one specific request, oldest first (a readable history)."""
    if not service_requests_collection.find_one({"id": request_id}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service request not found")
    return list(audit_logs_collection.find({"request_id": request_id}).sort("created_at", 1))
