from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class MovementType(str, enum.Enum):
    RECEIPT = "receipt"
    DISPATCH = "dispatch"
    ADJUSTMENT = "adjustment"
    TRANSFER = "transfer"


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    name = Column(String(150), nullable=False)
    location = Column(String(255), nullable=True)

    stock_entries = relationship("Stock", back_populates="warehouse")


class Stock(Base):
    """Current quantity of a product at a warehouse. One row per (product, warehouse)."""
    __tablename__ = "stock"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)

    quantity = Column(Numeric(18, 2), nullable=False, default=0)
    batch_number = Column(String(100), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="stock_entries")
    warehouse = relationship("Warehouse", back_populates="stock_entries")


class StockMovement(Base):
    """Immutable ledger of every stock change — source of truth for reconciliation."""
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)

    movement_type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Numeric(18, 2), nullable=False)  # positive for in, negative for out
    reference = Column(String(150), nullable=True)  # e.g. PO number, order number
    batch_number = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
