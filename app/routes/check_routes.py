from fastapi import APIRouter
from fastapi.responses import JSONResponse
import google.generativeai as genai

check_router = APIRouter(prefix="/check", tags=["check"])

@check_router.get("/models")
async def list_models():
    """Lista todos os modelos Gemini disponíveis"""
    try:
        models = genai.list_models()
        model_list = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                model_list.append({
                    "name": model.name,
                    "supported_methods": model.supported_generation_methods
                })
        return JSONResponse({"available_models": model_list})
    except Exception as e:
        return JSONResponse({"error": str(e)})
    

@check_router.get("/")
async def root():
    """
    Rota para fazer o healthcheck e obter informações gerais da API.
    """
    return {
        "message": "API de Análise de Currículos com Google Gemini",
        "status": "online",
        "model": "gemini-2.0-flash-001"
    }