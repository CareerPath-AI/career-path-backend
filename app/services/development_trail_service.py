from fastapi import HTTPException
from app.utils.development_trail_utils import create_development_trail_prompt, extract_json_from_response
from app.schemas.development_trail_schema import UserData
import google.generativeai as genai


async def generate_development_trail_with_gemini_service(user_data: UserData) -> dict:
    """Gera trilha de desenvolvimento usando Google Gemini"""
    # Cria prompt
    prompt = create_development_trail_prompt(user_data)
    
    try:
        model = genai.GenerativeModel("gemini-2.0-flash-001")
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=2000,
                top_p=0.8,
                top_k=40
            )
        )
        
        response_text = response.text.strip()
        
        # Processa a resposta
        return extract_json_from_response(response_text)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no serviço de IA: {str(e)}"
        )