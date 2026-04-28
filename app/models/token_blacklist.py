from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime, timezone

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    def __init__(self, token: str, expires_at: datetime):
        # Grante que expires_at tem timezone
        if expires_at.tzinfo is None:
            self.expires_at = expires_at.replace(tzinfo=timezone.utc)
        else:
            self.expires_at = expires_at
        self.token = token
        