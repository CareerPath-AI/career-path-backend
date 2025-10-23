from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.utils.development_trail_utils import (
    create_development_trail_prompt,
    extract_json_from_response,
)
from app.schemas.development_trail_schema import UserData
from app.models.user import User
from app.models.development_trail import DevelopmentTrail
import google.generativeai as genai


async def generate_development_trail_with_gemini_service(
    user_data: UserData, user: User, db: Session
) -> dict:
    """Gera trilha de desenvolvimento usando Google Gemini"""
    # Cria prompt
    prompt = create_development_trail_prompt(user_data)

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
            user_id=user.id,
            development_trail=development_trail_result,
        )

        db.add(development_trail)
        db.commit()
        db.refresh(development_trail)

        return {
            "id": development_trail.id,
            "development_trail": development_trail_result,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro no serviço de IA: {str(e)}")
