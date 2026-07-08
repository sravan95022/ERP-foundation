from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class DeadLetterTask(Base):
    """Tasks that failed after max retries land here for manual inspection."""
    __tablename__ = "dead_letter_tasks"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    task_name = Column(String(150), nullable=False)
    error = Column(String(1000), nullable=True)
    attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
