from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.schemas.development_trail_schema import UserData, DevelopmentTrailResponse
from app.services.development_trail_service import generate_development_trail_with_gemini_service
from app.utils.development_trail_utils import create_development_trail_prompt


development_trail_router = APIRouter(prefix="/development-trail", tags=["development-trail"])


@development_trail_router.post("/", response_model=DevelopmentTrailResponse)
async def generate_development_trail(user_data: UserData):
    """
    Recebe dados do usuário e retorna trilha de desenvolvimento personalizada.
    """
    
    try:
        # Gera trilha com Gemini
        development_trail = await generate_development_trail_with_gemini_service(user_data)
        
        return JSONResponse(
            content={
                "status": "success",
                "user_data_received": {
                    "name": user_data.name,
                    "professional_goal": user_data.professional_goal,
                    "skills_count": len(user_data.skills),
                    "has_additional_info": bool(user_data.additional_information)
                },
                "development_trail": development_trail
            },
            status_code=200
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao gerar trilha de desenvolvimento: {str(e)}"
        )

@development_trail_router.get("/test-prompt")
async def test_prompt_structure():
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
        additional_information="Tenho interesse em aprender Docker e AWS"
    )
    
    prompt = create_development_trail_prompt(test_data)
    
    return {
        "prompt_structure": "valid",
        "prompt_length": len(prompt),
        "has_user_data": True,
        "sample_prompt_preview": prompt[:500] + "..." if len(prompt) > 500 else prompt
    }