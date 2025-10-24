from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.schemas.development_trail_schema import UserData, DevelopmentTrailResponse, DevelopmentTrailListResponse
from app.services.development_trail_services import (
    generate_development_trail_with_gemini_service,
)
from app.utils.development_trail_utils import create_adaptive_development_trail_prompt
from app.models.user import User
from app.models.development_trail import DevelopmentTrail
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

    prompt = create_adaptive_development_trail_prompt(test_data)

    return {
        "prompt_structure": "valid",
        "prompt_length": len(prompt),
        "has_user_data": True,
        "sample_prompt_preview": prompt[:500] + "..." if len(prompt) > 500 else prompt,
    }


@development_trail_router.get("/", response_model=DevelopmentTrailListResponse)
async def get_my_development_trails(
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de itens para pular"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de itens por página")
):
    """
    Retorna todas as trilhas de desenvolvimento do usuário autenticado.
    """
    try:
        development_trails = db.query(DevelopmentTrail).filter(
            DevelopmentTrail.user_id == current_user.id
        ).order_by(
            DevelopmentTrail.created_at.desc()
        ).offset(skip).limit(limit).all()

        total_count = db.query(DevelopmentTrail).filter(
            DevelopmentTrail.user_id == current_user.id
        ).count()

        return DevelopmentTrailListResponse(
            development_trails=development_trails,
            total_count=total_count
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar análises: {str(e)}"
        )
    

@development_trail_router.get("/{development_trail_id}", response_model=DevelopmentTrailResponse)
async def get_development_trail(
    development_trail_id: int,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Retorna uma trilha de desenvolvimento específica do usuário
    """
    development_trails = db.query(DevelopmentTrail).filter(
        DevelopmentTrail.id == development_trail_id,
        DevelopmentTrail.user_id == current_user.id
    ).first()

    if not development_trails:
        raise HTTPException(
            status_code=404,
            detail="Trilha de desenvolvimento não encontrada"
        )

    return development_trails

