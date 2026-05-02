from app.schemas.development_trail_schema import DevelopmentTrailRequest
from app.core.logging_config import logger
import json
import re


def create_adaptive_development_trail_prompt(user_data: DevelopmentTrailRequest) -> str:
    """Cria um prompt adaptável baseado no tempo disponível do usuário"""

    # Calcula meses totais baseado no timeframe
    total_months = calculate_timeframe_months(user_data.goal_timeframe)

    # Calcula número total de sprints baseado no tempo disponível
    total_sprints = get_sprints_structure(total_months)

    return f"""
Você é um especialista em desenvolvimento de carreira em tecnologia. 
Analise os dados do usuário e retorne APENAS um objeto JSON válido, sem nenhum texto adicional.

**DADOS DO USUÁRIO:**
- Formação: {user_data.education or "Não informada"}
- Área Atual: {user_data.current_area or "Não informada"}
- Experiência: {user_data.experience_in_years or 0} anos
- Habilidades: {", ".join(user_data.skills)}
- Tecnologias de Interesse: {", ".join(user_data.interested_technologies) if user_data.interested_technologies else "Não informado"}
- Nível Atual: {user_data.current_level or "Não informado"}
- Objetivo Profissional: {user_data.professional_goal}
- Disponibilidade Semanal: {user_data.available_time_week or "Não informada"}
- Prazo para Objetivo: {user_data.goal_timeframe or "Não informado"}
- Informações Adicionais: {user_data.additional_information or "Nenhuma"}

**ESTRUTURA ADAPTATIVA:**
Total de Sprints a gerar: {total_sprints} sprints de 15 dias cada.

**FORMATO EXATO DO JSON:**

{{
    "user_profile_summary": {{
        "current_profile": "Resumo de 2-3 frases SEM nome ou idade",
        "strengths": ["ponto forte 1", "ponto forte 2", "ponto forte 3"],
        "improvement_areas": ["área de melhoria 1", "área de melhoria 2"]
    }},
    "trail_metadata": {{
        "total_sprints": {total_sprints},
        "total_duration_days": {total_sprints * 15},
        "difficulty_progression": "iniciante → intermediário",
        "focus_technologies": ["Tecnologia 1", "Tecnologia 2"]
    }},
    "sprints": [
        {{
            "sprint_number": 1,
            "title": "Título resumindo o foco da sprint",
            "duration": "15 dias",
            "days": [
                {{
                    "day": 1,
                    "topic": "Título específico do tópico",
                    "description": "Breve explicação do que será estudado neste dia",
                    "study_type": "theory | practice | review"
                }}
            ],
            "practical_exercises": [
                {{
                    "title": "Título do exercício",
                    "description": "Instruções claras sobre o que construir ou resolver",
                    "difficulty": "beginner | intermediate | advanced"
                }}
            ],
            "sprint_goal": "O que o estudante deve ser capaz de fazer ao final desta sprint",
            "revision_project": {{
                "title": "Título do projeto",
                "description": "Projeto prático que reforça tópicos das sprints anteriores",
                "covers_sprints": [1, 2],
                "estimated_hours": 6
            }}
        }}
    ],
    "recommended_resources": {{
        "courses": ["curso 1", "curso 2", "curso 3"],
        "tools": ["ferramenta 1", "ferramenta 2"],
        "communities": ["comunidade 1", "comunidade 2"],
        "books": ["livro 1", "livro 2"]
    }},
    "career_tips": [
        "dica prática 1",
        "dica prática 2", 
        "dica prática 3",
        "dica prática 4"
    ],
    "study_plan_adaptation": {{
        "weekly_recommendation": "Recomendação de estudo semanal adaptada considerando {user_data.available_time_week}",
        "acceleration_tips": ["Dica para acelerar 1", "Dica para acelerar 2"]
    }}
}}

**INSTRUÇÕES ADAPTATIVAS:**

DURAÇÃO TOTAL: {total_months} MESES ({total_sprints} SPRINTS)
- Se {total_months} <= 3 meses: Foque em objetivos imediatos e habilidades essenciais
- Se 4 <= {total_months} <= 6 meses: Inclua fundamentos + especialização básica  
- Se {total_months} >= 7 meses: Crie um plano completo com múltiplas fases de aprofundamento

DISPONIBILIDADE: {user_data.available_time_week or "Não especificada"}
- Se < 10h/semana: Priorize micro-learning e projetos pequenos
- Se 10-20h/semana: Mantenha ritmo moderado com projetos medianos
- Se > 20h/semana: Inclua projetos complexos e aprendizagem aprofundada

NÍVEL: {user_data.current_level or "Não especificado"}
- Iniciante: Foque em fundamentos e projetos guiados
- Intermediário: Balance fundamentos com especialização
- Avançado: Foque em tópicos avançados e projetos complexos

**REGRAS ESTRITAS:**
1. BASEIE-SE APENAS NAS INFORMAÇÕES FORNECIDAS. NUNCA mencione o nome ou idade do usuário.
2. SEJA REALISTA com o tempo disponível.
3. PRIORIZE as tecnologias de interesse: {user_data.interested_technologies or "Todas"}
4. ADAPTE a complexidade ao nível do usuário.
5. CRIE EXATAMENTE {total_sprints} SPRINTS.
6. CADA SPRINT DEVE CONTER EXATAMENTE 15 DIAS DE ESTUDO com tópicos distintos e focados.
7. Tópicos muito amplos devem ser divididos em múltiplas sprints.
8. INCLUA NO MÍNIMO 2 EXERCÍCIOS PRÁTICOS EM CADA SPRINT.
9. O campo revision_project é OBRIGATÓRIO a partir da sprint 3 e opcional nas sprints 1 e 2.
10. RETORNE APENAS JSON VÁLIDO. NÃO INCLUA comentários do tipo // ou blocos de texto fora do JSON.
"""


def calculate_timeframe_months(timeframe: str) -> int:
    """Calcula meses totais baseado no timeframe informado"""
    if not timeframe:
        return 6  # default

    timeframe_lower = timeframe.lower()

    if any(term in timeframe_lower for term in ["1 mes", "1 mês", "30 dias", "um mes"]):
        return 1
    elif any(term in timeframe_lower for term in ["3 meses", "trimestre", "90 dias"]):
        return 3
    elif any(term in timeframe_lower for term in ["6 meses", "semestre", "180 dias"]):
        return 6
    elif any(term in timeframe_lower for term in ["1 ano", "12 meses", "365 dias"]):
        return 12
    elif any(term in timeframe_lower for term in ["2 anos", "24 meses"]):
        return 24
    else:
        numbers = re.findall(r"\d+", timeframe)
        if numbers:
            return min(int(numbers[0]), 36)
        return 6 


def get_sprints_structure(total_months: int) -> int:
    """Calcula o número total de sprints baseado na duração total"""
    # Fórmula de cálculo: (meses * 30 dias) / 15 dias por sprint
    total_sprints = (total_months * 30) // 15
    # Limita a 3 sprints (45 dias detalhados dia a dia) para garantir que NUNCA estoure os 8192 tokens
    return min(total_sprints, 3)


def extract_json_from_response(response_text: str) -> dict:
    """Extrai JSON da resposta do Gemini com tratamento robusto"""
    if not response_text:
        raise ValueError("Texto vazio não pode ser convertido para JSON")
    
    # Limpa o texto - remove code blocks markdown e comentários inline
    cleaned_text = response_text.strip()
    cleaned_text = re.sub(r'^```json\s*', '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'^```\s*', '', cleaned_text)
    cleaned_text = re.sub(r'\s*```$', '', cleaned_text)
    cleaned_text = re.sub(r'(?m)^\s*//.*$', '', cleaned_text) # Remove comentários // em inícios de linha
    cleaned_text = cleaned_text.strip()
    
    logger.debug(f"Texto limpo para extração JSON (primeiros 300 chars): {cleaned_text[:300]}")
    
    try:
        # Tenta parsear diretamente
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        logger.error(f"Erro no parse JSON direto: {e}")
        
        # Tenta encontrar JSON dentro do texto usando regex
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, cleaned_text, re.DOTALL)
        
        if matches:
            # Pega o maior match (provavelmente o JSON completo)
            json_str = max(matches, key=len)
            logger.debug(f"JSON encontrado via regex (primeiros 300 chars): {json_str[:300]}")
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e2:
                logger.error(f"Erro no parse do JSON regex: {e2}")
                
                # Tenta reparar JSON truncado
                try:
                    repaired_json = repair_truncated_json(json_str, e2)
                    if repaired_json:
                        return json.loads(repaired_json)
                except Exception as repair_error:
                    logger.error(f"Falha ao reparar JSON: {repair_error}")
        
        # Se nada funcionar, levanta exceção
        raise ValueError(f"Não foi possível extrair JSON válido do texto. Erro: {str(e)}")


def repair_truncated_json(json_str: str, error: json.JSONDecodeError = None) -> str:
    """
    Tenta reparar JSON truncado ou com erros de sintaxe
    """
    repaired = json_str.strip()
    
    # Se temos informação sobre o erro, usa para guiar o reparo
    error_pos = None
    if error and hasattr(error, 'pos'):
        error_pos = error.pos
        logger.debug(f"Tentando reparar JSON na posição do erro: {error_pos}")
    
    # Passo 1: Se temos posição do erro, tenta truncar e fechar estruturas nesse ponto
    if error_pos and error_pos > 0:
        truncated = repaired[:error_pos].rstrip()
        while truncated and truncated[-1] in [',', ':', '"']:
            truncated = truncated[:-1].rstrip()
        repaired = truncated
    
    # Passo 2: Repara strings não terminadas
    if repaired.count('"') % 2 != 0:
        last_quote_idx = repaired.rfind('"')
        if last_quote_idx > 0:
            remaining = repaired[last_quote_idx+1:].strip()
            if remaining and not any(c in remaining for c in [':', ',', '}', ']']):
                repaired = repaired[:last_quote_idx+1] + '"' + repaired[last_quote_idx+1:]
    
    # Passo 3: Conta e fecha estruturas não fechadas
    open_braces = repaired.count('{')
    close_braces = repaired.count('}')
    open_brackets = repaired.count('[')
    close_brackets = repaired.count(']')
    
    for _ in range(open_braces - close_braces):
        repaired += '}'
    for _ in range(open_brackets - close_brackets):
        repaired += ']'
    
    # Passo 4: Remove vírgulas finais desnecessárias
    repaired = re.sub(r',\s*}', '}', repaired)
    repaired = re.sub(r',\s*]', ']', repaired)
    
    # Passo 5: Adiciona vírgulas faltantes em padrões comuns
    repaired = re.sub(r'"\s*\n\s*"', '",\n"', repaired)
    repaired = re.sub(r'}\s*"', '}, "', repaired)
    repaired = re.sub(r']\s*"', '], "', repaired)
    repaired = re.sub(r'"\s*{', '", {', repaired)
    repaired = re.sub(r'"\s*\[', '", [', repaired)
    
    return repaired
