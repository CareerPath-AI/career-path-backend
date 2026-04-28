from typing import List, Optional, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, **kwargs) -> ModelType:
        try:
            instance = self.model(**kwargs)
            self.session.add(instance)
            await self.session.flush()
            await self.session.commit()
            await self.session.refresh(instance)
            return instance
        except Exception:
            await self.session.rollback()
            raise

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        try:
            obj = await self.get_by_id(id)
            if not obj:
                return None
            
            for key, value in kwargs.items():
                setattr(obj, key, value)

            self.session.add(obj)
            await self.session.flush()
            await self.session.commit()
            
            await self.session.refresh(obj)
            return obj
            
        except Exception:
            await self.session.rollback()
            raise
    
    async def delete(self, id: int) -> None:
        try:
            await self.session.execute(
                delete(self.model).where(self.model.id == id)
            )
            await self.session.flush()
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise