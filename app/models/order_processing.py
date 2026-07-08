from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Enum
from datetime import datetime
import enum
from app.core.database import Base


class ShipmentStatus(str, enum.Enum):
    PLANNED = "planned"
    SHIPPED = "shipped"
    DELIVERED = "delivered"


class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    carrier = Column(String(100), nullable=True)
    tracking_number = Column(String(100), nullable=True)
    status = Column(Enum(ShipmentStatus), default=ShipmentStatus.PLANNED)
    created_at = Column(DateTime, default=datetime.utcnow)


class ReturnRequest(Base):
    __tablename__ = "return_requests"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    quantity = Column(Numeric(18, 2), nullable=False)
    reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Refund(Base):
    __tablename__ = "refunds"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    return_request_id = Column(Integer, ForeignKey("return_requests.id"), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    status = Column(String(50), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)
