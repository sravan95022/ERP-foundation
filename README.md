# Enterprise ERP System — Foundation

This is the **foundation layer** of a 35-phase Enterprise ERP system. Phases completed so far:

- **Phase 1 — BRD**: `docs/01_BRD.md` (stakeholders, functional/non-functional requirements, use cases, acceptance criteria)
- **Phase 2 — SRS**: `docs/02_SRS.md` (user stories, business rules, constraints, edge cases)
- **Phase 3 — System Architecture**: `docs/03_ARCHITECTURE.md` (HLD, LLD, component diagram, sequence diagrams, deployment architecture — all as Mermaid diagrams)
- **Phase 4 — Database Architecture**: `docs/04_DATABASE_ARCHITECTURE.md` (ER diagram, index/partitioning/archival strategy, normalization pattern for future tables)
- **Phase 5 — Enterprise Project Structure**: modular layout + **Repository Pattern** (`app/repositories/base.py` and per-entity repositories) + service layer + dependency injection, all live in the auth flow
- **Phase 6 — Configuration Framework**: multi-environment support, secrets validation (refuses insecure boot in production), feature flags, all in `app/core/config.py`
- **Phase 7 — Authentication Platform**: register, login, JWT + refresh tokens
- **Phase 8 — Authorization Engine**: RBAC via role-based route guards
- **Phase 9 — Multi-Tenant Architecture**: shared-DB pattern with `tenant_id` scoping
- **Phase 10 — Organization Management**: Company → Branch → Department models
- **Phase 11 — User Management**: profile, preferences, activity tracking, forgot/reset password, account deactivation/reactivation (all in `app/routers/users.py`)
- **Phase 15 — Product Management**: categories, brands, products with variants, pricing (`app/routers/products.py`)
- **Phase 16 — Inventory & Warehouse**: multi-warehouse stock, stock movement ledger, batch tracking, negative-stock guard, reconciliation endpoint (`app/routers/inventory.py`)
- **Phase 12 — Employee Management**: employee records, attendance, leave requests + approval, performance reviews (`app/routers/employees.py`)
- **Phase 13 — Customer & CRM**: leads (with convert-to-customer), customers, opportunities, interaction history (`app/routers/crm.py`)
- **Phase 14 — Vendor & Supplier Management**: vendors, contracts, evaluations, compliance field (`app/routers/vendors.py`)

All future business modules (Procurement, Sales, Inventory, Finance, etc.) plug into
this foundation: every new table gets a `tenant_id`, every new route reuses
`get_current_user` / `require_role` from `app/core/deps.py`, and every new module gets
its own repository extending `BaseRepository`.

## Setup

```bash
pip install -r requirements.txt --break-system-packages
cp .env.example .env
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive Swagger UI.

## Tested flow

1. `POST /api/v1/tenants/` — create a tenant (organization)
2. `POST /api/v1/auth/register` — register a user under that tenant
3. `POST /api/v1/auth/login` — get access + refresh tokens
4. `GET /api/v1/auth/me` — access protected route with `Authorization: Bearer <token>`
5. `POST /api/v1/auth/refresh` — get a new access token using refresh token

All five confirmed working.

## Project structure

```
app/
  core/        # config, database, security (JWT/bcrypt), deps (auth guards)
  models/      # SQLAlchemy models (organization.py, user.py)
  schemas/     # Pydantic request/response schemas
  routers/     # FastAPI route definitions
  services/    # business logic (kept separate from routes)
  repositories/# (reserved for data-access layer as modules grow)
```

## What's NOT built yet (by design, for a fast MVP)

- MFA / OTP, session tracking, account locking (Phase 7/11 extras)
- Dynamic permission matrix / policy engine (Phase 8 extras — currently just role-name checks)
- Dedicated-DB-per-tenant option (Phase 9 extra — currently shared DB + tenant_id)
- All Phase 12–35 business/platform modules (Inventory, Sales, Finance, Reporting, etc.)

## Next steps (recommended build order)

1. Phase 11: full User Management (profile, preferences, activity log)
2. Phase 12–14: Employee, CRM, Vendor modules (reuse tenant + RBAC pattern)
3. Phase 15–16: Product + Inventory
4. Phase 17–20: Procurement → Sales → Orders → Finance
5. Everything else per the master roadmap

## Adding a new module (pattern to follow)

1. Add model(s) in `app/models/<module>.py` with a `tenant_id` FK
2. Add schema(s) in `app/schemas/<module>.py`
3. Add service in `app/services/<module>_service.py`
4. Add router in `app/routers/<module>.py`, protect routes with
   `Depends(require_role('admin', 'manager'))` as needed
5. Register router in `app/main.py`
