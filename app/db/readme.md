# SMS DB Blueprint & Business Rules

This document summarizes the key business rules, deletion/retention policies, and model relationships for the School Management System (SMS) backend. Use this as a reference for model, API, and business logic decisions.

---

## User
- Users belong to a tenant (organization or solo teacher).
- Roles: `owner`, `admin`, `teacher`, `student`, `guardian`.
- Roles are immutable after creation.
- Users in organizations cannot delete their own accounts; only admins/owners can remove users.
- Duplicate emails are not allowed (unique constraint).
- If a tenant is deleted, users' `tenant_id` is set to NULL.
- If a user is the owner of a tenant and requests deletion, a 90-day grace period begins. All users are notified to back up data. After 90 days, teachers can migrate to solo accounts if they opt in.

## Tenant
- Represents an organization or solo teacher.
- Must always have an owner (`owner_user_id` is required after creation).
- Only one owner per tenant (super admin).
- Cannot be moved or deleted unless the owner initiates deletion.
- If the owner is deleted, a 90-day grace period applies before final deletion and data migration.
- **Circular Dependency Note:** To avoid circular FK issues between `User` and `Tenant`, we make `owner_user_id` nullable in the DB, create the tenant first, then the owner user, and finally update the tenant with the owner's ID. Business logic ensures every tenant has an owner after

## Class
- Belongs to a tenant and is taught by a teacher.
- Can be reassigned to another teacher (with audit trail).
- Can be soft-deleted (restorable within 30 days).
- Inactive classes (60+ days) are auto-removed.
- Class names can be duplicated within a tenant.
- Students can be removed and may download their data before removal.

## Quiz
- Belongs to a class and has a creator (teacher).
- Cannot be deleted if any student has taken it; can only be archived.
- Can be unpublished if no student has taken it.
- If the creator is deleted, the quiz is deleted, but attempts remain as metadata for reporting.
- If a student exceeds the time limit, the attempt is auto-submitted.
- Some quizzes contribute to overall scores; this can be updated anytime.

## AttendanceRecord
- Tracks attendance for students in classes.
- Attendance can be for online or in-person classes (consider adding a `mode` field).
- Duplicate attendance for the same student/class/date should be prevented.
- Attendance corrections should be auditable.
- Notes may be required for certain statuses (e.g., late/absent).

---

## General Policies
- All deletions that affect other users/data should be soft-deletes with grace periods and notifications.
- All business rules must be enforced in the service/API layer, not just the DB.
- Audit trails should be maintained for all critical actions (deletion, transfer, restoration).
- REST API docs and frontend must reflect these rules and flows.

---

_This file is the canonical reference for SMS backend data and business rules. Update as the system evolves._
