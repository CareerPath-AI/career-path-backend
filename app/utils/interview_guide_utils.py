from app.core.config import settings
from app.core.logging_config import logger
import google.generativeai as genai
import re
import json


async def generate_interview_guide_with_gemini(resume_text: str, job_description: str) -> dict:
    """Gera um roteiro de entrevista personalizado usando Google Gemini"""
    
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    truncated_resume = resume_text[:6000]
    truncated_job_desc = job_description[:2000]
    
    prompt = """
    VOCÊ É UM ESPECIALISTA EM PREPARAÇÃO PARA ENTREVISTAS DE TECNOLOGIA. 

    **INSTRUÇÃO CRÍTICA: RETORNE APENAS UM OBJETO JSON VÁLIDO. NADA MAIS. SEM TEXTOS EXPLICATIVOS, SEM COMENTÁRIOS, SEM MARKDOWN.**

    ANALISE O CURRÍCULO E A DESCRIÇÃO DA VAGA E RETORNE UM ROTEIRO COMPLETO DE ENTREVISTA NO SEGUINTE FORMATO EXATO:

    {
        "preparation_overview": "string com visão geral de 2-3 frases",
        "strength_analysis": {
            "key_strengths": ["string1", "string2", "string3"],
            "alignment_points": ["string1", "string2"]
        },
        "technical_preparation": {
            "programming_languages": [
                {
                    "topic": "string",
                    "focus_points": ["string1", "string2", "string3"],
                    "expected_level": "string"
                }
            ],
            "frameworks_tools": [
                {
                    "topic": "string",
                    "key_concepts": ["string1", "string2"],
                    "practical_examples": ["string1", "string2"]
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
                    "key_achievements": ["string1", "string2"],
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
            "research_topics": ["string1", "string2"],
            "questions_to_ask": ["string1", "string2", "string3"]
        },
        "study_plan_timeline": {
            "immediate_24h": ["string1", "string2"],
            "next_3_days": ["string1", "string2", "string3"],
            "week_before": ["string1", "string2"]
        }
    }

    **REGRAS:**
    - PREENCHA TODOS OS CAMPOS
    - BASEIE-SE APENAS NAS INFORMAÇÕES DO CURRÍCULO E VAGA
    - SEJA ESPECÍFICO E DIRETO
    - NÃO INCLUA TEXTOS EXPLICATIVOS FORA DO JSON
    - MANTENHA O FORMATO EXATO ACIMA
    """

    model = genai.GenerativeModel('gemini-2.0-flash-001')
    
    full_prompt = f"""
    {prompt}

    CURRÍCULO:
    {truncated_resume}

    DESCRIÇÃO DA VAGA:
    {truncated_job_desc}

    RESPOSTA (APENAS JSON):
    """
    
    response = model.generate_content(
        full_prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.2,
            max_output_tokens=4000,
            top_p=0.7,
            top_k=40
        )
    )
    
    response_text = response.text.strip()
    logger.debug(f"Resposta bruta do Gemini: {response_text}")
    
    # Extrai JSON da resposta
    parsed_response = extract_interview_json_from_text(response_text)
    
    return parsed_response


def extract_interview_json_from_text(text: str) -> dict:
    """
    Extrai JSON de texto que pode conter markdown ou outros elementos
    """
    if not text:
        raise ValueError("Texto vazio não pode ser convertido para JSON")
    
    # Limpa o texto - remove code blocks markdown
    cleaned_text = text.strip()
    cleaned_text = re.sub(r'^```json\s*', '', cleaned_text)
    cleaned_text = re.sub(r'\s*```$', '', cleaned_text)
    cleaned_text = cleaned_text.strip()
    
    logger.debug(f"Texto limpo para extração JSON: {cleaned_text[:500]}...")  # Debug
    
    try:
        # Tenta parsear diretamente como JSON
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        logger.error(f"Erro no parse JSON direto: {e}")
        
        # Tenta encontrar JSON dentro do texto usando regex
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, cleaned_text, re.DOTALL)
        
        if matches:
            # Pega o maior match (provavelmente o JSON completo)
            json_str = max(matches, key=len)
            logger.debug(f"JSON encontrado via regex: {json_str[:500]}...")  # Debug
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e2:
                logger.error(f"Erro no parse do JSON regex: {e2}")
        
        # Se nada funcionar, levanta exceção
        raise ValueError(f"Não foi possível extrair JSON válido do texto: {text[:500]}")


# Função auxiliar para detectar skills (se ainda precisar)
def detect_skills(text: str, skills_list: list) -> list:
    """Detecta habilidades mencionadas no texto"""
    found_skills = []
    text_lower = text.lower()
    
    for skill in skills_list:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return found_skills
