from sqlalchemy.orm import Session
from app.models.notification import NotificationLog, TEMPLATES


def _send_email(to: str, message: str) -> None:
    print(f"[EMAIL STUB] to={to} :: {message}")


def _send_sms(to: str, message: str) -> None:
    print(f"[SMS STUB] to={to} :: {message}")


def _send_push(to: str, message: str) -> None:
    print(f"[PUSH STUB] to={to} :: {message}")


def notify(db: Session, tenant_id: int, channel: str, template: str, detail: str, to: str = "system") -> NotificationLog:
    """Dispatches on the requested channel (email/sms/push are stubs — real
    providers plug in here later) and always logs to NotificationLog for
    in-app notification history + audit."""
    message = TEMPLATES.get(template, "{detail}").format(detail=detail)

    dispatch = {"email": _send_email, "sms": _send_sms, "push": _send_push}
    if channel in dispatch:
        dispatch[channel](to, message)

    log = NotificationLog(tenant_id=tenant_id, channel=channel, template=template, detail=detail)
    db.add(log); db.commit(); db.refresh(log)
    return log
