from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base


class Payment(Base):
    """Payment record model for audit and revocation."""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(String(255), unique=True, nullable=False, index=True)  # Gumroad sale_id
    gateway_transaction_id = Column(String(255), nullable=True)                # Gumroad sale_id
    email = Column(String(255), nullable=False, index=True)
    amount = Column(Integer, nullable=False)   # in cents (USD)
    product_tier = Column(Integer, nullable=False)  # 1, 2, or 3
    granted_resources = Column(Text, nullable=False)  # JSON array of sheet IDs
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Payment(payment_id={self.payment_id}, email={self.email}, tier={self.product_tier})>"
