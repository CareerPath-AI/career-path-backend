from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.utils.development_trail_utils import (
    create_adaptive_development_trail_prompt,
    extract_json_from_response,
)
from app.schemas.development_trail_schema import (
    DevelopmentTrailRequest,
    DevelopmentTrailResponse,
    DevelopmentTrailListResponse,
    DevelopmentTrailDeleteResponse
)
from app.models.user import User
from app.models.development_trail import DevelopmentTrail
import google.generativeai as genai


class DevelopmentTrailService:
    async def generate_development_trail_with_gemini_service(
        self, user_data: DevelopmentTrailRequest, current_user: User, db: AsyncSession
    ) -> dict:
        """Serviço que gera trilha de desenvolvimento usando Google Gemini"""
        # Cria prompt
        prompt = create_adaptive_development_trail_prompt(user_data)

        try:
            model = genai.GenerativeModel("gemini-2.0-flash-001")

            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3, max_output_tokens=2000, top_p=0.8, top_k=40
                ),
            )

            response_text = response.text.strip()

            development_trail_result = extract_json_from_response(response_text)

            development_trail = DevelopmentTrail(
                user_id=current_user.id,
                development_trail=development_trail_result,
            )

            db.add(development_trail)
            await db.commit()
            await db.refresh(development_trail)

            return DevelopmentTrailResponse(
                id=development_trail.id,
                development_trail=development_trail.development_trail,
            )

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno ao gerar trilha de desenvolvimento: {str(e)}",
            )
        
    async def get_development_trail_service(
        self, current_user: User, db: AsyncSession, skip: int, limit: int
    ):
        """
        Serviço que retorna todas as trilhas de desenvolvimento do usuário
        """
        try:
            result = await db.execute(
                select(DevelopmentTrail)
                .where(DevelopmentTrail.user_id == current_user.id)
                .order_by(DevelopmentTrail.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            development_trails = result.scalars().all() 

            if not development_trails:
                raise HTTPException(
                    status_code=404, detail="Nenhuma trilha de desenvolvimento encontrada"
                )

            count_result = await db.execute(
                select(func.count(DevelopmentTrail.id))
                .where(DevelopmentTrail.user_id == current_user.id)
            )
            total_count = count_result.scalar_one()

            return DevelopmentTrailListResponse(
                development_trails=development_trails, 
                total_count=total_count
            )
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar trilhas de desenvolvimento: {str(e)}"
            )

    async def get_development_trail_by_id_service(
        self, development_trail_id: int, current_user: User, db: AsyncSession
    ):
        """
        Serviço que retorna uma trlha de desenvolvimento específica do usuário
        """
        try:
            result = await db.execute(
                select(DevelopmentTrail)
                .where(
                    DevelopmentTrail.id == development_trail_id,
                    DevelopmentTrail.user_id == current_user.id
                )
            )
            development_trail = result.scalar_one_or_none() 

            if not development_trail:
                raise HTTPException(
                    status_code=404,
                    detail="Trilha de desenvolvimento não encontrada"
                )
            
            return DevelopmentTrailResponse(
                id=development_trail.id,
                development_trail=development_trail.development_trail,
            )
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar trilha de desenvolvimento: {str(e)}"
            )
        
    async def delete_development_trail_service(
        self, development_trail_id: int, current_user: User, db: AsyncSession
    ):
        """
        Serviço para deletar uma trilha de desenvolvimento do usuário
        """
        try:
            result = await db.execute(
                select(DevelopmentTrail)
                .where(
                    DevelopmentTrail.id == development_trail_id,
                    DevelopmentTrail.user_id == current_user.id
                )
            )
            development_trail = result.scalar_one_or_none()

            if not development_trail:
                raise HTTPException(
                    status_code=404, detail="Trilha de desenvolvimento não encontrada"
                )
            
            await db.delete(development_trail)
            await db.commit()

            return DevelopmentTrailDeleteResponse(
                message="Trilha de desenvolvimento deletada com sucesso",
                deleted_id=development_trail_id,
            )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao deletar trilha de desenvolvimento: {str(e)}"
            )


development_trail_service = DevelopmentTrailService()
