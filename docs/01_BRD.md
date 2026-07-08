# Phase 1 — Business Requirement Analysis (BRD)

## 1. Stakeholder Analysis

| Stakeholder | Role | Key Interest |
|---|---|---|
| Business Owner / Sponsor | Funds and owns the ERP rollout | ROI, adoption, reduced manual work |
| Admin (Tenant Owner) | Configures the org, manages users/roles | Full control, security, audit visibility |
| Branch Manager | Oversees a branch's operations | Accurate reports, approval workflows |
| Employee (Procurement/Sales/Finance staff) | Daily transactional user | Simple UI, fast workflows, few errors |
| Customer (in CRM/Sales context) | External party interacting via orders/invoices | Accurate orders, timely delivery, clear invoices |
| Vendor/Supplier | External party fulfilling purchase orders | Clear POs, timely payment |
| IT/DevOps team | Deploys and maintains the system | Stability, observability, easy deployment |
| Auditor/Compliance | Reviews financial and access records | Complete audit trail, data integrity |

## 2. Functional Requirements (by module)

- **Auth & Org**: Users must register under a tenant, log in via JWT, and be assigned exactly one role that governs access.
- **Procurement**: Staff can raise purchase requests, convert them to POs after approval, and record goods receipt against a PO.
- **Sales**: Staff can create quotations, convert to sales orders, and generate invoices with tax/discount rules applied.
- **Inventory**: Stock levels must update automatically on goods receipt, sales dispatch, and manual adjustment, with full movement history.
- **Finance**: Every transaction that has a monetary impact (invoice, payment, refund) must generate a corresponding journal entry in the general ledger.
- **Reporting**: Authorized users can view/export dashboards and reports scoped to their tenant and role.

## 3. Non-Functional Requirements

- **Multi-tenancy**: Complete data isolation between tenants at the query level.
- **Security**: Passwords hashed (bcrypt), tokens signed (JWT/HS256), role-based access enforced on every protected route.
- **Performance**: API responses under 300ms for CRUD operations at expected load (target, not yet load-tested).
- **Availability**: System designed to support containerized, horizontally-scalable deployment.
- **Auditability**: State-changing actions (create/update/delete on financial and inventory records) must be logged with actor, timestamp, and action.
- **Extensibility**: New modules must be addable without modifying existing modules' internals (enforced via the router/service/repository pattern).

## 4. Use Cases (representative sample)

- **UC-01**: As an Admin, I create a Tenant so my organization can start using the system.
- **UC-02**: As an Employee, I register and log in so I can access my tenant's data.
- **UC-03**: As a Procurement Officer, I raise a Purchase Request so it can be routed for approval.
- **UC-04**: As a Sales Rep, I convert a Quotation into a Sales Order so fulfillment can begin.
- **UC-05**: As a Finance Officer, I view the General Ledger so I can reconcile monthly accounts.
- **UC-06**: As an Admin, I assign roles to users so access is restricted appropriately.

## 5. Acceptance Criteria (representative sample)

- **UC-01**: Given a unique slug, a Tenant is created and returned with `is_active=true`. Duplicate slugs are rejected with a 400 error.
- **UC-02**: Given valid credentials, a user receives a valid access + refresh token pair. Invalid credentials return 401 without revealing whether the email or password was wrong.
- **UC-03**: A Purchase Request cannot be converted to a PO unless its status is `approved`.
- **UC-04**: Converting a Quotation to a Sales Order is only allowed once; a second attempt returns an error.
- **UC-05**: The General Ledger balance (debits − credits) must equal zero at all times for a closed period.
- **UC-06**: A user with role `employee` cannot access admin-only routes (403 Forbidden).
