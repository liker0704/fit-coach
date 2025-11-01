"""WaterIntake model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.day import Day


class WaterIntake(Base):
    """Water intake tracking model."""

    __tablename__ = "water_intakes"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    day_id = Column(Integer, ForeignKey("days.id", ondelete="CASCADE"), nullable=False)

    # Water info
    amount = Column(Numeric(3, 2), nullable=False)  # liters
    time = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    day = relationship("Day", back_populates="water_intakes")

    def __repr__(self):
        return f"<WaterIntake {self.amount}L at {self.time}>"
