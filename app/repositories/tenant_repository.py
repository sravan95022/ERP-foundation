from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.organization import Tenant


class TenantRepository(BaseRepository[Tenant]):
    def __init__(self, db: Session):
        super().__init__(db, Tenant)

    def get_by_slug(self, slug: str) -> Optional[Tenant]:
        return self.db.query(Tenant).filter(Tenant.slug == slug).first()
