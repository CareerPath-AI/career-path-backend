from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.development_trail_schema import UserData, DevelopmentTrailResponse
from app.services.development_trail_services import (
    generate_development_trail_with_gemini_service,
)
from app.utils.development_trail_utils import create_development_trail_prompt
from app.models.user import User
from app.dependencies.security import verify_token
from app.dependencies.database import get_db


development_trail_router = APIRouter(
    prefix="/development-trail", tags=["development-trail"]
)


@development_trail_router.post("/", response_model=DevelopmentTrailResponse)
async def generate_development_trail(
    user_data: UserData, current_user: User = Depends(verify_token), db: Session = Depends(get_db)
):
    """
    Recebe dados do usuário e retorna trilha de desenvolvimento personalizada.
    """

    try:
        # Gera trilha com Gemini
        development_trail = await generate_development_trail_with_gemini_service(
            user_data, current_user, db
        )

        return development_trail

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao gerar trilha de desenvolvimento: {str(e)}",
        )


@development_trail_router.get("/test-prompt")
async def test_prompt_structure(current_user: User = Depends(verify_token)):
    """Endpoint para testar a estrutura do prompt (apenas desenvolvimento)"""
    test_data = UserData(
        name="João Teste",
        age=25,
        education="Graduação em Sistemas de Informação",
        current_area="Desenvolvedor Júnior",
        experience_in_years=2,
        skills=["Python", "Django", "PostgreSQL"],
        interested_technologies=["Back-End", "DevOps"],
        current_level="Júnior",
        professional_goal="Tornar-se Desenvolvedor Pleno",
        available_time_week="20 horas semanais",
        goal_timeframe="8 meses",
        additional_information="Tenho interesse em aprender Docker e AWS",
    )

    prompt = create_development_trail_prompt(test_data)

    return {
        "prompt_structure": "valid",
        "prompt_length": len(prompt),
        "has_user_data": True,
        "sample_prompt_preview": prompt[:500] + "..." if len(prompt) > 500 else prompt,
    }
