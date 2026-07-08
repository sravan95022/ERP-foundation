import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.core.database import SessionLocal
from app.models.background_job import DeadLetterTask

logger = logging.getLogger("erp.scheduler")
scheduler = BackgroundScheduler()


def with_retry(max_attempts: int = 3):
    """Decorator: retries a job function; on final failure, logs to DeadLetterTask
    instead of silently dropping the job (Phase 27 requirement)."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            last_error = None
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    last_error = str(e)
                    logger.warning(f"Job {func.__name__} failed (attempt {attempts}/{max_attempts}): {e}")
            db = SessionLocal()
            try:
                db.add(DeadLetterTask(task_name=func.__name__, error=last_error, attempts=attempts))
                db.commit()
            finally:
                db.close()
        return wrapper
    return decorator


@with_retry(max_attempts=3)
def escalate_overdue_approvals_job():
    """Example scheduled job: runs the workflow escalation check for all tenants."""
    from app.services.workflow_service import check_and_escalate_overdue
    from app.models.organization import Tenant

    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        for t in tenants:
            check_and_escalate_overdue(db, t.id)
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(escalate_overdue_approvals_job, "interval", hours=1, id="escalate_overdue", replace_existing=True)
    scheduler.start()
