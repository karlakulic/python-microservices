import uuid
from sqlalchemy import Column, String, Boolean, Integer, Numeric, Text, DateTime, func, UniqueConstraint, Index
from app.db.session import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    sku = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="EUR")
    stock = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_products_user_name"),
        UniqueConstraint("user_id", "sku",  name="uq_products_user_sku"),
        Index("ix_products_created_at", "created_at"),
    )
