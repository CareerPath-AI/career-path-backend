# app/services/analyze_services.py
from app.utils.utils import extract_json_from_text, local_resume_analysis
from app.core.config import settings
import google.generativeai as genai
from PyPDF2 import PdfReader
import io


async def analyze_resume_service(file_contents: bytes, filename: str) -> dict:
    """
    Service para análise de currículo
    """
    # Lê e extrai texto do PDF
    if len(file_contents) == 0:
        raise ValueError("O arquivo está vazio")

    pdf_file = io.BytesIO(file_contents)
    reader = PdfReader(pdf_file)

    if reader.is_encrypted:
        raise ValueError("PDF criptografado não é suportado")

    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    if not text.strip():
        raise ValueError("Nenhum texto foi encontrado no PDF")

    # Analisa o currículo com Gemini
    analysis_result = await analyze_with_gemini(text)

    return {
        "filename": filename,
        "total_pages": len(reader.pages),
        "analysis": analysis_result,
    }


async def analyze_with_gemini(resume_text: str) -> dict:
    """Analisa o currículo usando Google Gemini com modelos disponíveis"""

    genai.configure(api_key=settings.GEMINI_API_KEY)

    truncated_text = resume_text[:6000]

    prompt = """
    Você é um especialista em análise de currículos para carreiras em tecnologia. 
    Analise este currículo e retorne APENAS um objeto JSON válido, sem nenhum texto adicional.

    FORMATO EXATO DO JSON:
    {
        "professional_summary": "Resumo profissional em 2-3 frases",
        "experience_level": "Júnior | Pleno | Sênior | Especialista",
        "technical_skills": {
            "programming_languages": ["lista de linguagens encontradas"],
            "frameworks": ["lista de frameworks encontrados"],
            "tools": ["lista de ferramentas encontradas"],
            "databases": ["lista de bancos de dados encontrados"],
            "cloud_services": ["lista de serviços cloud encontrados"]
        },
        "career_recommendations": [
            "Recomendação 1 para crescimento profissional",
            "Recomendação 2 para desenvolvimento de carreira",
            "Recomendação 3 baseada nas habilidades atuais"
        ],
        "skill_gaps": [
            "Habilidade em falta 1 que impediria promoção",
            "Habilidade em falta 2 para mercado atual"
        ],
        "suggested_roles": [
            "Cargo sugerido 1 baseado nas habilidades",
            "Cargo sugerido 2 para próximo nível",
            "Cargo sugerido 3 alinhado com experiência"
        ],
        "market_insights": "Insight sobre mercado de tecnologia para este perfil em 2-3 frases"
    }

    BASEIE-SE APENAS NAS INFORMAÇÕES DO CURRÍCULO.
    """

    try:
        model = genai.GenerativeModel("gemini-2.0-flash-001")

        response = model.generate_content(
            f"{prompt}\n\nTEXTO DO CURRÍCULO:\n{truncated_text}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.2, max_output_tokens=1500, top_p=0.8, top_k=40
            ),
        )

        response_text = response.text.strip()
        print(f"Resposta do Gemini: {response_text}")

        return extract_json_from_text(response_text)

    except Exception as e:
        print(f"Erro no Gemini: {str(e)}")
        # Fallback para análise local
        return local_resume_analysis(truncated_text)