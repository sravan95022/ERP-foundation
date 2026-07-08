# Phase 3 — System Architecture

## 1. High-Level Design (HLD)

```mermaid
graph TB
    Client[Client Apps<br/>Web / Mobile] --> Gateway[API Gateway / FastAPI App]
    Gateway --> Auth[Auth & RBAC Middleware]
    Auth --> Modules

    subgraph Modules[Business Modules]
        direction LR
        Org[Org & Tenant]
        Proc[Procurement]
        Sales[Sales]
        Inv[Inventory]
        Fin[Finance]
    end

    Modules --> DB[(Relational DB<br/>SQLite / MySQL / PostgreSQL)]
    Modules --> Cache[(Redis Cache)]
    Modules --> Queue[Background Jobs<br/>APScheduler / Celery]
```

## 2. Low-Level Design (LLD) — Layered pattern per module

```mermaid
graph LR
    Router[Router Layer<br/>FastAPI routes] --> Service[Service Layer<br/>business logic]
    Service --> Repo[Repository Layer<br/>data access]
    Repo --> Model[SQLAlchemy Models]
    Model --> DB[(Database)]
    Service --> Schema[Pydantic Schemas<br/>validation/serialization]
```

Every module (Procurement, Sales, Inventory, Finance, etc.) follows this same four-layer
pattern: **Router → Service → Repository → Model**, so the codebase stays predictable
as it grows to 35 phases.

## 3. Component Diagram

```mermaid
graph TB
    subgraph Core["app/core"]
        Config[config.py]
        DB2[database.py]
        Security[security.py]
        Deps[deps.py]
    end

    subgraph Foundation["Foundation Modules"]
        Tenant[Tenant/Org]
        UserAuth[User/Auth/RBAC]
    end

    subgraph Business["Business Modules (future)"]
        Procurement
        SalesM[Sales]
        InventoryM[Inventory]
        FinanceM[Finance]
    end

    Core --> Foundation
    Foundation --> Business
```

## 4. Sequence Diagram — Login flow

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Auth Router
    participant S as Auth Service
    participant DB as Database

    C->>R: POST /auth/login {email, password}
    R->>S: authenticate_user()
    S->>DB: query User by email
    DB-->>S: User row
    S->>S: verify_password (bcrypt)
    S-->>R: User object
    R->>S: issue_tokens()
    S-->>R: {access_token, refresh_token}
    R-->>C: 200 OK {tokens}
```

## 5. Sequence Diagram — Purchase Request → PO approval (future module)

```mermaid
sequenceDiagram
    participant E as Employee
    participant WF as Workflow Engine
    participant M as Manager
    participant PO as Procurement Service

    E->>PO: create Purchase Request
    PO->>WF: submit for approval
    WF->>M: notify pending approval
    M->>WF: approve
    WF->>PO: mark request approved
    PO->>PO: convert to Purchase Order
```

## 6. Deployment Architecture

```mermaid
graph TB
    subgraph Docker["Docker Compose"]
        API[FastAPI App Container]
        DBc[(Database Container)]
        Redisc[(Redis Container)]
    end
    Nginx[Reverse Proxy / Nginx + SSL] --> API
    API --> DBc
    API --> Redisc
    Users((Users)) --> Nginx
```

**Target production setup**: Nginx reverse proxy with SSL termination in front of the
FastAPI app, MySQL/PostgreSQL as the primary database, Redis for caching and as the
Celery/APScheduler broker, all orchestrated via Docker Compose for the MVP stage.
