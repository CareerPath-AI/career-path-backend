# app/services/interview_guide_services.py
from app.utils.utils import extract_json_from_text, generate_fallback_interview_guide
from app.core.config import settings
import google.generativeai as genai
from PyPDF2 import PdfReader
import io


async def generate_interview_guide_service(file_contents: bytes, filename: str, job_description: str) -> dict:
    """
    Service para geração de guia de entrevista
    """
    # Lê e extrai texto do PDF
    if len(file_contents) == 0:
        raise ValueError("O arquivo está vazio")

    pdf_file = io.BytesIO(file_contents)
    reader = PdfReader(pdf_file)

    if reader.is_encrypted:
        raise ValueError("PDF criptografado não é suportado")

    resume_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            resume_text += page_text + "\n"

    if not resume_text.strip():
        raise ValueError("Nenhum texto foi encontrado no PDF")

    # Gera o guia de entrevista com Gemini
    interview_guide = await generate_interview_guide_with_gemini(resume_text, job_description)

    return {
        "filename": filename,
        "job_description_preview": job_description[:100] + "..." if len(job_description) > 100 else job_description,
        "interview_guide": interview_guide
    }


async def generate_interview_guide_with_gemini(resume_text: str, job_description: str) -> dict:
    """Gera um roteiro de entrevista personalizado usando Google Gemini"""
    
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    truncated_resume = resume_text[:6000]
    truncated_job_desc = job_description[:2000]
    
    prompt = """
    VOCÊ É UM ESPECIALISTA EM PREPARAÇÃO PARA ENTREVISTAS DE TECNOLOGIA. 
    Com base no currículo do candidato e na descrição da vaga, crie um roteiro 
    OBJETIVO e DETALHADO para preparação para a entrevista.

    **IMPORTANTE: RETORNE APENAS UM OBJETO JSON VÁLIDO, SEM TEXTO ADICIONAL, SEM COMENTÁRIOS, SEM MARKDOWN.**

    FORMATO EXATO DO JSON:
    {
        "preparation_overview": "string",
        "strength_analysis": {
            "key_strengths": ["string", "string", "string"],
            "alignment_points": ["string", "string"]
        },
        "technical_preparation": {
            "programming_languages": [
                {
                    "topic": "string",
                    "focus_points": ["string", "string", "string"],
                    "expected_level": "string"
                }
            ],
            "frameworks_tools": [
                {
                    "topic": "string",
                    "key_concepts": ["string", "string"],
                    "practical_examples": ["string", "string"]
                }
            ],
            "system_design": [
                {
                    "topic": "string",
                    "preparation_guide": "string"
                }
            ]
        },
        "behavioral_preparation": {
            "storytelling_points": [
                {
                    "situation": "string",
                    "key_achievements": ["string", "string"],
                    "metrics": "string"
                }
            ],
            "common_questions": [
                {
                    "question": "string",
                    "preparation_tips": "string",
                    "resume_connection": "string"
                }
            ]
        },
        "company_specific_preparation": {
            "research_topics": ["string", "string"],
            "questions_to_ask": ["string", "string", "string"]
        },
        "study_plan_timeline": {
            "immediate_24h": ["string", "string"],
            "next_3_days": ["string", "string", "string"],
            "week_before": ["string", "string"]
        }
    }

    BASEIE-SE APENAS NAS INFORMAÇÕES DO CURRÍCULO E DA DESCRIÇÃO DA VAGA.
    SEJA ESPECÍFICO E PRÁTICO.
    """

    try:
        model = genai.GenerativeModel('gemini-2.0-flash-001')
        
        response = model.generate_content(
            f"{prompt}\n\nTEXTO DO CURRÍCULO:\n{truncated_resume}\n\nDESCRIÇÃO DA VAGA:\n{truncated_job_desc}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=2000,
                top_p=0.8,
                top_k=40
            )
        )
        
        response_text = response.text.strip()
        print(f"Resposta bruta do Gemini (Interview Guide): {response_text}")
        
        parsed_response = extract_json_from_text(response_text)
        print(f"Resposta parseada: {parsed_response}")
        
        return parsed_response

    except Exception as e:
        print(f"Erro no Gemini (Interview Guide): {str(e)}")
        return generate_fallback_interview_guide(resume_text, job_description)