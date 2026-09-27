# app/seed_data.py
#
# use facility_management
# db.users.deleteMany({})
# db.categories.deleteMany({})
# db.locations.deleteMany({})
# db.service_requests.deleteMany({})
# db.comments.deleteMany({})
# db.attachments.deleteMany({})
# db.audit_logs.deleteMany({})
#
# Purpose:
#   Populates MongoDB with sample data for every entity (User, Category,
#   Location, ServiceRequest, Comment, Attachment, AuditLog) — at least 8
#   records each — with realistic cross-references (a request's category_id
#   and location_id point to a real category/location, a comment's
#   request_id points to a real request, etc.), so the API and frontend
#   have something meaningful to show right away.
#
# This is a one-off maintenance script. It lives in app/ (a sibling of
# app/database.py) rather than a separate scripts/ package, so it reuses
# the exact same shared MongoDB connection the API itself uses.
#
# Run it from the backend project root with:
#   python -m app.seed_data
#
# WARNING: this clears the 7 collections below before inserting, so it's
# meant for a fresh/dev database, not production data.

from datetime import datetime, timedelta

from app.database import database  # the same shared connection app/database.py builds

# ---------------------------------------------------------------------------
# IDs are plain, readable strings (not real uuid4 values) on purpose — the
# app's schemas only require "id" to be a string, they never validate uuid
# *format*. Readable ids make it far easier to see how records cross-reference
# each other in this seed file.
# ---------------------------------------------------------------------------

NOW = datetime.utcnow()


def days_ago(n: int) -> datetime:
    """Small helper so seeded timestamps look realistic and spread out."""
    return NOW - timedelta(days=n)


# --- 1. Users (8) — covering all four roles ---------------------------------
USERS = [
    {"id": "user-emp-1", "name": "Priya Sharma", "email": "priya.sharma@company.com",
     "password": "password123", "role": "employee", "created_at": days_ago(30)},
    {"id": "user-emp-2", "name": "Rahul Verma", "email": "rahul.verma@company.com",
     "password": "password123", "role": "employee", "created_at": days_ago(29)},
    {"id": "user-emp-3", "name": "Ananya Gupta", "email": "ananya.gupta@company.com",
     "password": "password123", "role": "employee", "created_at": days_ago(28)},
    {"id": "user-emp-4", "name": "Karan Mehta", "email": "karan.mehta@company.com",
     "password": "password123", "role": "employee", "created_at": days_ago(27)},
    {"id": "user-fm-1", "name": "Neha Singh", "email": "neha.singh@company.com",
     "password": "password123", "role": "facility_manager", "created_at": days_ago(60)},
    {"id": "user-staff-1", "name": "Arjun Nair", "email": "arjun.nair@company.com",
     "password": "password123", "role": "support_staff", "created_at": days_ago(50)},
    {"id": "user-staff-2", "name": "Divya Iyer", "email": "divya.iyer@company.com",
     "password": "password123", "role": "support_staff", "created_at": days_ago(45)},
    {"id": "user-admin-1", "name": "Vikram Rao", "email": "vikram.rao@company.com",
     "password": "password123", "role": "admin", "created_at": days_ago(90)},
]

# --- 2. Categories (6) — matches the fixed request categories from the spec -
CATEGORIES = [
    {"id": "cat-ac", "name": "AC Issue", "description": "Air conditioning problems", "created_at": days_ago(90)},
    {"id": "cat-electrical", "name": "Electrical Issue", "description": "Wiring, sockets, lighting problems", "created_at": days_ago(90)},
    {"id": "cat-housekeeping", "name": "Housekeeping", "description": "Cleaning and upkeep requests", "created_at": days_ago(90)},
    {"id": "cat-meeting-room", "name": "Meeting Room", "description": "Meeting room setup/equipment issues", "created_at": days_ago(90)},
    {"id": "cat-security", "name": "Security", "description": "Access, badges, and safety concerns", "created_at": days_ago(90)},
    {"id": "cat-it", "name": "IT", "description": "Network, hardware and software issues", "created_at": days_ago(90)},
]

# --- 3. Locations (8) — Building -> Floor -> Room ----------------------------
LOCATIONS = [
    {"id": "loc-1", "building": "Tower A", "floor": "1st Floor", "room": "Reception", "created_at": days_ago(90)},
    {"id": "loc-2", "building": "Tower A", "floor": "3rd Floor", "room": "Conference Room B", "created_at": days_ago(90)},
    {"id": "loc-3", "building": "Tower A", "floor": "5th Floor", "room": None, "created_at": days_ago(90)},
    {"id": "loc-4", "building": "Tower B", "floor": "2nd Floor", "room": "Server Room", "created_at": days_ago(90)},
    {"id": "loc-5", "building": "Tower B", "floor": "4th Floor", "room": "Cafeteria", "created_at": days_ago(90)},
    {"id": "loc-6", "building": "Tower B", "floor": "6th Floor", "room": None, "created_at": days_ago(90)},
    {"id": "loc-7", "building": "Tower C", "floor": "Ground Floor", "room": "Security Desk", "created_at": days_ago(90)},
    {"id": "loc-8", "building": "Tower C", "floor": "2nd Floor", "room": "Meeting Room 2A", "created_at": days_ago(90)},
]

# --- 4. Service requests (8) — spans every lifecycle status at least once ---
SERVICE_REQUESTS = [
    {"id": "req-1", "title": "AC not cooling in Conference Room B", "description": "AC blows warm air even at lowest setting.",
     "category_id": "cat-ac", "location_id": "loc-2", "status": "new", "created_by": "user-emp-1", "assigned_to": None,
     "created_at": days_ago(6), "updated_at": days_ago(6)},
    {"id": "req-2", "title": "Flickering lights on 5th floor", "description": "Overhead lights flicker constantly near the east wing.",
     "category_id": "cat-electrical", "location_id": "loc-3", "status": "assigned", "created_by": "user-emp-2", "assigned_to": "user-staff-1",
     "created_at": days_ago(5), "updated_at": days_ago(4)},
    {"id": "req-3", "title": "Reception restroom needs cleaning", "description": "Restroom near reception hasn't been cleaned today.",
     "category_id": "cat-housekeeping", "location_id": "loc-1", "status": "in_progress", "created_by": "user-emp-3", "assigned_to": "user-staff-2",
     "created_at": days_ago(5), "updated_at": days_ago(3)},
    {"id": "req-4", "title": "Need projector setup in Conference Room B", "description": "Projector cable is missing for tomorrow's client demo.",
     "category_id": "cat-meeting-room", "location_id": "loc-2", "status": "on_hold", "created_by": "user-emp-4", "assigned_to": "user-staff-1",
     "created_at": days_ago(4), "updated_at": days_ago(2)},
    {"id": "req-5", "title": "Unauthorized badge access alert", "description": "Badge reader logged an access attempt after hours.",
     "category_id": "cat-security", "location_id": "loc-7", "status": "resolved", "created_by": "user-emp-1", "assigned_to": "user-staff-2",
     "created_at": days_ago(10), "updated_at": days_ago(1)},
    {"id": "req-6", "title": "Wi-Fi down in cafeteria", "description": "Cafeteria Wi-Fi has been unreachable since this morning.",
     "category_id": "cat-it", "location_id": "loc-5", "status": "closed", "created_by": "user-emp-2", "assigned_to": "user-staff-1",
     "created_at": days_ago(12), "updated_at": days_ago(1)},
    {"id": "req-7", "title": "Broken chair in Meeting Room 2A", "description": "One of the chairs has a broken wheel base.",
     "category_id": "cat-meeting-room", "location_id": "loc-8", "status": "new", "created_by": "user-emp-3", "assigned_to": None,
     "created_at": days_ago(1), "updated_at": days_ago(1)},
    {"id": "req-8", "title": "Server room AC failure", "description": "Server room temperature is rising, AC unit seems to have stalled.",
     "category_id": "cat-ac", "location_id": "loc-4", "status": "assigned", "created_by": "user-emp-4", "assigned_to": "user-staff-2",
     "created_at": days_ago(2), "updated_at": days_ago(1)},
]

# --- 5. Comments (8) — spread across several requests ------------------------
COMMENTS = [
    {"id": "comment-1", "request_id": "req-1", "author_id": "user-emp-1",
     "content": "It's been like this since this morning's meeting.", "created_at": days_ago(6)},
    {"id": "comment-2", "request_id": "req-2", "author_id": "user-staff-1",
     "content": "Heading up now to check the ballast on those fixtures.", "created_at": days_ago(4)},
    {"id": "comment-3", "request_id": "req-2", "author_id": "user-emp-2",
     "content": "Thanks, it's the row closest to the stairwell.", "created_at": days_ago(4)},
    {"id": "comment-4", "request_id": "req-3", "author_id": "user-staff-2",
     "content": "On it, will be done within the hour.", "created_at": days_ago(3)},
    {"id": "comment-5", "request_id": "req-4", "author_id": "user-emp-4",
     "content": "Demo is at 3pm tomorrow, any update on the cable?", "created_at": days_ago(2)},
    {"id": "comment-6", "request_id": "req-5", "author_id": "user-staff-2",
     "content": "Confirmed with security footage, was an authorized contractor. Closing out.", "created_at": days_ago(1)},
    {"id": "comment-7", "request_id": "req-6", "author_id": "user-emp-2",
     "content": "Confirmed, Wi-Fi is back. Thank you!", "created_at": days_ago(1)},
    {"id": "comment-8", "request_id": "req-8", "author_id": "user-staff-2",
     "content": "Vendor has been called for an emergency AC repair.", "created_at": days_ago(1)},
]

# --- 6. Attachments (8) — metadata only, spread across several requests -----
ATTACHMENTS = [
    {"id": "attachment-1", "request_id": "req-1", "uploaded_by": "user-emp-1",
     "filename": "ac_unit_photo.jpg", "url": "https://files.example.com/ac_unit_photo.jpg",
     "size": 204800, "created_at": days_ago(6)},
    {"id": "attachment-2", "request_id": "req-2", "uploaded_by": "user-emp-2",
     "filename": "flickering_lights.mp4", "url": "https://files.example.com/flickering_lights.mp4",
     "size": 5242880, "created_at": days_ago(5)},
    {"id": "attachment-3", "request_id": "req-3", "uploaded_by": "user-emp-3",
     "filename": "restroom_photo.jpg", "url": "https://files.example.com/restroom_photo.jpg",
     "size": 153600, "created_at": days_ago(5)},
    {"id": "attachment-4", "request_id": "req-4", "uploaded_by": "user-emp-4",
     "filename": "projector_request.pdf", "url": "https://files.example.com/projector_request.pdf",
     "size": 81920, "created_at": days_ago(4)},
    {"id": "attachment-5", "request_id": "req-5", "uploaded_by": "user-staff-2",
     "filename": "badge_log_export.csv", "url": "https://files.example.com/badge_log_export.csv",
     "size": 30720, "created_at": days_ago(9)},
    {"id": "attachment-6", "request_id": "req-6", "uploaded_by": "user-emp-2",
     "filename": "wifi_error_screenshot.png", "url": "https://files.example.com/wifi_error_screenshot.png",
     "size": 174080, "created_at": days_ago(12)},
    {"id": "attachment-7", "request_id": "req-7", "uploaded_by": "user-emp-3",
     "filename": "broken_chair_photo.jpg", "url": "https://files.example.com/broken_chair_photo.jpg",
     "size": 245760, "created_at": days_ago(1)},
    {"id": "attachment-8", "request_id": "req-8", "uploaded_by": "user-staff-2",
     "filename": "server_room_temp_log.pdf", "url": "https://files.example.com/server_room_temp_log.pdf",
     "size": 92160, "created_at": days_ago(1)},
]

# --- 7. Audit logs (8) — matching real actions taken on the requests above ---
AUDIT_LOGS = [
    {"id": "audit-1", "request_id": "req-1", "action": "created", "performed_by": "user-emp-1",
     "details": "Request created with status 'new'.", "created_at": days_ago(6)},
    {"id": "audit-2", "request_id": "req-2", "action": "created", "performed_by": "user-emp-2",
     "details": "Request created with status 'new'.", "created_at": days_ago(5)},
    {"id": "audit-3", "request_id": "req-2", "action": "assigned", "performed_by": "user-fm-1",
     "details": "Assigned to user 'user-staff-1'. Status moved from 'new' to 'assigned'.", "created_at": days_ago(4)},
    {"id": "audit-4", "request_id": "req-3", "action": "created", "performed_by": "user-emp-3",
     "details": "Request created with status 'new'.", "created_at": days_ago(5)},
    {"id": "audit-5", "request_id": "req-3", "action": "assigned", "performed_by": "user-fm-1",
     "details": "Assigned to user 'user-staff-2'. Status moved from 'new' to 'assigned'.", "created_at": days_ago(4)},
    {"id": "audit-6", "request_id": "req-3", "action": "status_changed", "performed_by": "user-staff-2",
     "details": "Status changed from 'assigned' to 'in_progress'.", "created_at": days_ago(3)},
    {"id": "audit-7", "request_id": "req-5", "action": "status_changed", "performed_by": "user-staff-2",
     "details": "Status changed from 'in_progress' to 'resolved'.", "created_at": days_ago(1)},
    {"id": "audit-8", "request_id": "req-6", "action": "status_changed", "performed_by": "user-emp-2",
     "details": "Status changed from 'resolved' to 'closed'.", "created_at": days_ago(1)},
]


def seed() -> None:
    """Clears the 7 collections and inserts the fixed seed data above."""
    collections_and_data = [
        ("users", USERS),
        ("categories", CATEGORIES),
        ("locations", LOCATIONS),
        ("service_requests", SERVICE_REQUESTS),
        ("comments", COMMENTS),
        ("attachments", ATTACHMENTS),
        ("audit_logs", AUDIT_LOGS),
    ]

    for collection_name, documents in collections_and_data:
        collection = database[collection_name]
        deleted = collection.delete_many({}).deleted_count
        collection.insert_many(documents)
        print(f"{collection_name}: cleared {deleted} old record(s), inserted {len(documents)} new record(s)")


if __name__ == "__main__":
    seed()
    print("\nSeeding complete.")
