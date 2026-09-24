"""ORM models for M16 Settings. See ERD in architecture doc Section 5.3.

User Management and Role Management (the part of M16 built so far) need
no new tables — they operate on the existing auth.models.User and
auth.models.Role tables, since those already are the app's users/roles.

SAP Configuration, Mail Configuration, QR Configuration, and Audit Logs
are the remaining parts of M16 per the KT notes and are not yet
implemented; those will need their own tables when built."""
