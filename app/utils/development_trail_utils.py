from app.schemas.development_trail_schema import UserData
import json
import re


def create_development_trail_prompt(user_data: UserData) -> str:
    """Cria o prompt estruturado para o Gemini"""
    
    return f"""
Você é um especialista em desenvolvimento de carreira em tecnologia. 
Analise os dados do usuário e retorne APENAS um objeto JSON válido, sem nenhum texto adicional.

**DADOS DO USUÁRIO:**
- Nome: {user_data.name}
- Idade: {user_data.age or 'Não informada'}
- Formação: {user_data.education or 'Não informada'}
- Área Atual: {user_data.current_area or 'Não informada'}
- Experiência: {user_data.experience_in_years or 0} anos
- Habilidades: {', '.join(user_data.skills)}
- Tecnologias de Interesse: {', '.join(user_data.interested_technologies) if user_data.interested_technologies else 'Não informado'}
- Nível Atual: {user_data.current_level or 'Não informado'}
- Objetivo Profissional: {user_data.professional_goal}
- Disponibilidade Semanal: {user_data.available_time_week or 'Não informada'}
- Prazo para Objetivo: {user_data.goal_timeframe or 'Não informado'}
- Informações Adicionais: {user_data.additional_information or 'Nenhuma'}

**FORMATO EXATO DO JSON:**

{{
    "user_profile_summary": {{
        "current_profile": "Resumo do perfil atual em 2-3 frases",
        "strengths": ["ponto forte 1", "ponto forte 2", "ponto forte 3"],
        "improvement_areas": ["área de melhoria 1", "área de melhoria 2"]
    }},
    "development_phases": [
        {{
            "phase": "FASE 1: FUNDAÇÕES",
            "duration": "4-6 semanas",
            "topics": ["tópico 1", "tópico 2", "tópico 3"],
            "resources": ["recurso 1", "recurso 2"],
            "projects": ["projeto prático 1", "projeto prático 2"],
            "learning_outcomes": ["resultado 1", "resultado 2"]
        }},
        {{
            "phase": "FASE 2: ESPECIALIZAÇÃO",
            "duration": "2-3 meses", 
            "topics": ["tópico 1", "tópico 2"],
            "resources": ["recurso 1", "recurso 2"],
            "projects": ["projeto 1", "projeto 2"],
            "learning_outcomes": ["resultado 1", "resultado 2"]
        }},
        {{
            "phase": "FASE 3: APROFUNDAMENTO",
            "duration": "2-3 meses",
            "topics": ["tópico 1", "tópico 2"],
            "resources": ["recurso 1", "recurso 2"], 
            "projects": ["projeto 1", "projeto 2"],
            "learning_outcomes": ["resultado 1", "resultado 2"]
        }}
    ],
    "recommended_resources": {{
        "courses": ["curso 1", "curso 2", "curso 3"],
        "tools": ["ferramenta 1", "ferramenta 2"],
        "communities": ["comunidade 1", "comunidade 2"],
        "books": ["livro 1", "livro 2"]
    }},
    "milestones": [
        {{
            "month": 1,
            "goals": ["meta específica 1", "meta específica 2"],
            "success_indicators": ["indicador 1", "indicador 2"]
        }},
        {{
            "month": 3,
            "goals": ["meta específica 1", "meta específica 2"], 
            "success_indicators": ["indicador 1", "indicador 2"]
        }},
        {{
            "month": 6,
            "goals": ["meta específica 1", "meta específica 2"],
            "success_indicators": ["indicador 1", "indicador 2"]
        }}
    ],
    "career_tips": [
        "dica prática 1",
        "dica prática 2", 
        "dica prática 3",
        "dica prática 4"
    ]
}}

**INSTRUÇÕES IMPORTANTES:**
- Seja específico, prático e realista
- Adapte às horas disponíveis: {user_data.available_time_week or 'Não especificada'}
- Considere o prazo: {user_data.goal_timeframe or 'Não especificado'}
- Alinhe com o nível: {user_data.current_level or 'Não especificado'}
- Foque nas tecnologias de interesse: {user_data.interested_technologies or 'Todas'}
- BASEIE-SE APENAS NAS INFORMAÇÕES FORNECIDAS PELO USUÁRIO.
"""

def extract_json_from_response(response_text: str) -> dict:
    """Extrai JSON da resposta do Gemini"""
    
    # Limpa a resposta
    cleaned_text = response_text.strip()
    
    # Tenta parsear diretamente primeiro
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        # Tenta encontrar JSON dentro do texto usando regex
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned_text, re.DOTALL)
        
        if json_match:
            try:
                json_str = json_match.group()
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"Falha ao parsear JSON extraído: {e}")
