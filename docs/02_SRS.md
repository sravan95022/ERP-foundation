# Phase 2 — Software Requirement Specification (SRS)

## 1. Purpose
This SRS translates the BRD (Phase 1) into concrete, testable software requirements for the ERP platform's foundation and subsequent modules.

## 2. Scope
Covers a multi-tenant, role-based ERP system built on FastAPI + SQLAlchemy, with modules for Procurement, Sales, Inventory, Finance, and supporting platform capabilities (workflow, notifications, search, reporting).

## 3. User Stories (representative sample)

- As a **new organization**, I want to register as a Tenant so my company's data is isolated from other tenants.
- As an **Admin**, I want to create roles and assign them to users so I can control what each person can access.
- As an **Employee**, I want to log in once and have my session refresh automatically (via refresh token) so I'm not repeatedly asked to re-enter my password.
- As a **Procurement Officer**, I want to see the status of my purchase requests so I know where they are in the approval chain.
- As a **Finance Officer**, I want every transaction to auto-post to the ledger so I never have to manually reconcile entries.
- As an **Auditor**, I want to see who changed what and when so I can verify compliance.

## 4. Business Rules

- A user belongs to exactly one Tenant and one Role.
- A Tenant must exist before any User can register under it.
- Financial transactions (invoices, payments, refunds) are immutable once posted — corrections are made via reversing entries, not edits.
- Stock quantity can never go negative; a dispatch/withdrawal that would breach zero stock must be rejected.
- Every monetary amount is stored as a decimal (never float) to avoid rounding errors.

## 5. Constraints

- Must run on Python 3.12 + FastAPI, matching the existing team's stack (Django/FastAPI/MySQL/SQLite background).
- Initial development targets SQLite for local/dev; production target is MySQL/PostgreSQL.
- Must be deployable via Docker Compose without cloud-provider lock-in.
- Solo/small-team build — architecture must favor simplicity and convention over highly abstracted enterprise patterns that would slow a small team down.

## 6. Edge Cases (representative sample)

- Duplicate tenant slug on registration → reject with clear error, do not silently overwrite.
- Refresh token used after expiry → reject, force full re-login.
- Concurrent stock deduction from two simultaneous orders → must not oversell (requires row-level locking or optimistic concurrency at the inventory service layer).
- User's role is deleted/changed while they hold an active token → the token remains valid until expiry (documented tradeoff for MVP; revocation list is a future enhancement).
- Purchase Request approved, then the requesting user is deactivated before PO conversion → PO conversion should still be allowed by another authorized user.
