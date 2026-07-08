from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    version = Column(Integer, default=1)
    entity_type = Column(String(100), nullable=True)  # e.g. "vendor_contract"
    entity_id = Column(Integer, nullable=True)
    metadata_json = Column(String(1000), nullable=True)  # simple JSON-as-text metadata index
    created_at = Column(DateTime, default=datetime.utcnow)
