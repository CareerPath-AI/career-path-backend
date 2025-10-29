from app.core.database import AsyncSessionLocal
from app.core.database import SessionLocal


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_db_sync():
    """
    Dependency para obter uma sessão de banco de dados síncrona
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
