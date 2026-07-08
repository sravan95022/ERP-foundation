# Phase 34 — Production Deployment

## Reverse Proxy + SSL
See `deploy/nginx.conf` — Nginx terminates SSL (Let's Encrypt via certbot) and
proxies to the FastAPI container over the internal Docker network.

## Backup Strategy
- **Database**: nightly `mysqldump`/`pg_dump` to a separate volume, retained 30 days locally, shipped to off-site/object storage weekly.
- **Uploaded documents** (`uploads/`): synced to object storage (S3-compatible) on a schedule, since these aren't in the DB.
- **Config/secrets**: `.env` values stored in a secrets manager, never committed to git (see `.gitignore`).

## Disaster Recovery
- Recovery Point Objective (RPO): last nightly backup (~24h data loss worst case at MVP stage).
- Recovery Time Objective (RTO): re-provision via `docker-compose up` on a fresh host + restore latest DB dump — target under 1 hour.
- Keep the CI-built Docker image tagged by commit SHA so a known-good image can always be redeployed without rebuilding.

## Zero-Downtime Deployment
- Run two API container replicas behind Nginx; deploy the new version to one, health-check it (`/api/v1/monitoring/health-detailed`), then swap traffic before updating the second (rolling deploy).
- Database migrations (via Alembic) must be backward-compatible with the previous app version for the duration of a rolling deploy — additive changes only in the same release that ships the code using them.

## Environment Promotion
- `development` → `staging` → `production`, gated by the `ENVIRONMENT` setting (Phase 6), each with its own `.env` and database.
- CI (Phase 33) runs tests on every PR; only a green build on `main` is eligible for promotion to staging, then production.
