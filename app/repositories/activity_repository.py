from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.user import ActivityLog


class ActivityRepository(BaseRepository[ActivityLog]):
    def __init__(self, db: Session):
        super().__init__(db, ActivityLog)

    def log(self, user_id: int, action: str, detail: str = None, ip_address: str = None) -> ActivityLog:
        return self.create({
            "user_id": user_id,
            "action": action,
            "detail": detail,
            "ip_address": ip_address,
        })

    def get_for_user(self, user_id: int, limit: int = 50):
        return (
            self.db.query(ActivityLog)
            .filter(ActivityLog.user_id == user_id)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
            .all()
        )
