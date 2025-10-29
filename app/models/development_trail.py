from sqlalchemy import Column, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime


class DevelopmentTrail(Base):
    __tablename__ = "development_trails"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    development_trail = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    user = relationship("User", back_populates="development_trails")

    def __init__(self, user_id: int, development_trail: dict, created_at: datetime):
        self.user_id = user_id
        self.development_trail = development_trail
        self.created_at = created_at
