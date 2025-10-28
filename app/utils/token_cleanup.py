from app.models.token_blacklist import TokenBlacklist
from sqlalchemy.orm import Session
from datetime import datetime, timezone

def cleanup_expired_tokens(db: Session) -> int:
    """
    Remove tokens expirados da blacklist
    """
    now = datetime.now(timezone.utc)
    deleted_count = db.query(TokenBlacklist).filter(
        TokenBlacklist.expires_at < now
    ).delete()
    db.commit()
    return deleted_count