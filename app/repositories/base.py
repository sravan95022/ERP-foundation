from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Generic repository providing common CRUD data-access, so every module's
    repository just declares `model = <SomeModel>` and inherits the rest.
    """

    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model

    def get(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, tenant_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[ModelType]:
        query = self.db.query(self.model)
        if tenant_id is not None and hasattr(self.model, "tenant_id"):
            query = query.filter(self.model.tenant_id == tenant_id)
        return query.offset(skip).limit(limit).all()

    def create(self, obj_in: dict) -> ModelType:
        obj = self.model(**obj_in)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, db_obj: ModelType, updates: dict) -> ModelType:
        for field, value in updates.items():
            setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: ModelType) -> None:
        self.db.delete(db_obj)
        self.db.commit()
