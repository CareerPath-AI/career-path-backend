from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.development_trail import DevelopmentTrail
from typing import Optional, List, Tuple
from app.repository.base_repository import BaseRepository


class DevelopmentTrailRepository(BaseRepository[DevelopmentTrail]):
    def __init__(self, session: AsyncSession):
        super().__init__(DevelopmentTrail, session)

    async def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[DevelopmentTrail], int]:
        """
        Busca trilhas de desenvolvimento por user_id com paginação e count total
        """
        result = await self.session.execute(
            select(DevelopmentTrail)
            .where(DevelopmentTrail.user_id == user_id)
            .order_by(DevelopmentTrail.created_at.desc())
            .offset(skip)
            .limit(limit) 
        )
        development_trails = result.scalars().all()

        count_result = await self.session.execute(
            select(func.count(DevelopmentTrail.id))
            .where(DevelopmentTrail.user_id == user_id)
        )
        total_count = count_result.scalar_one()

        return development_trails, total_count
    
    async def get_by_id_and_user_id(
        self,
        development_trail_id: int,
        user_id: int
    ) -> Optional[DevelopmentTrail]:
        """
        Busca trilha de desenvolvimento por ID e user_id
        """
        result = await self.session.execute(
            select(DevelopmentTrail)
            .where(
                DevelopmentTrail.id == development_trail_id,
                DevelopmentTrail.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    