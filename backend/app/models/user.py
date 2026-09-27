# app/models/user.py
#
# Purpose:
#   Describes the fixed set of roles a User can have in the Corporate
#   Facility Management System.

from enum import Enum


class UserRole(str, Enum):
    EMPLOYEE = "employee"
    SUPPORT_STAFF = "support_staff"
    FACILITY_MANAGER = "facility_manager"
    ADMIN = "admin"
