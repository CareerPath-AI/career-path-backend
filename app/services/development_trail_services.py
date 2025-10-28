from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.utils.development_trail_utils import (
    create_adaptive_development_trail_prompt,
    extract_json_from_response,
)
from app.schemas.development_trail_schema import (
    DevelopmentTrailRequest,
    DevelopmentTrailResponse,
)
from app.models.user import User
from app.models.development_trail import DevelopmentTrail
import google.generativeai as genai


class DevelopmentTrailService:
    async def generate_development_trail_with_gemini_service(
        self, user_data: DevelopmentTrailRequest, current_user: User, db: Session
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
            db.commit()
            db.refresh(development_trail)

            return DevelopmentTrailResponse(
                id=development_trail.id,
                development_trail=development_trail.development_trail,
            )

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno ao gerar trilha de desenvolvimento: {str(e)}",
            )


development_trail_service = DevelopmentTrailService()
