from app.core.config import settings
import google.generativeai as genai
import json
import re


def extract_json_from_text(text: str) -> dict:
    """Extrai JSON do texto de resposta"""
    try:
        # Tenta parsear diretamente
        return json.loads(text)
    except json.JSONDecodeError:
        # Tenta encontrar JSON dentro do texto
        json_match = re.search(
            r"\{[^{}]*\{[^{}]*\}[^{}]*\}|\{[^{}]*\}", text, re.DOTALL
        )
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

    return {
        "professional_summary": "Análise concluída - formato de resposta inesperado",
        "experience_level": "Não determinado",
        "technical_skills": {
            "programming_languages": [],
            "frameworks": [],
            "tools": [],
            "databases": [],
            "cloud_services": [],
        },
        "career_recommendations": [],
        "skill_gaps": [],
        "suggested_roles": [],
        "market_insights": "Análise textual realizada com sucesso",
    }


def local_resume_analysis(resume_text: str) -> dict:
    """Análise local de fallback caso o Gemini falhe"""
    text_lower = resume_text.lower()

    # Detecta habilidades baseado em palavras-chave
    programming_languages = detect_skills(
        text_lower,
        [
            "python",
            "java",
            "javascript",
            "typescript",
            "c#",
            "c++",
            "php",
            "ruby",
            "go",
            "rust",
            "swift",
            "kotlin",
            "dart",
            "r",
            "matlab",
        ],
    )

    frameworks = detect_skills(
        text_lower,
        [
            "django",
            "flask",
            "fastapi",
            "spring",
            "react",
            "angular",
            "vue",
            "node.js",
            "express",
            "laravel",
            "ruby on rails",
            "asp.net",
            "next.js",
            "nuxt.js",
        ],
    )

    tools = detect_skills(
        text_lower,
        [
            "git",
            "docker",
            "kubernetes",
            "jenkins",
            "github",
            "gitlab",
            "jira",
            "confluence",
            "postman",
            "figma",
            "photoshop",
            "illustrator",
        ],
    )

    databases = detect_skills(
        text_lower,
        [
            "mysql",
            "postgresql",
            "mongodb",
            "redis",
            "sqlite",
            "oracle",
            "sql server",
            "cassandra",
            "dynamodb",
            "firebase",
        ],
    )

    cloud_services = detect_skills(
        text_lower,
        [
            "aws",
            "azure",
            "gcp",
            "google cloud",
            "amazon web services",
            "lambda",
            "ec2",
            "s3",
            "cloud functions",
            "heroku",
            "digital ocean",
        ],
    )

    # Determina nível de experiência
    experience_level = determine_experience_level(resume_text)

    # Gera recomendações baseadas nas habilidades encontradas
    recommendations = generate_recommendations(
        programming_languages, frameworks, experience_level
    )

    return {
        "professional_summary": f"Perfil analisado com {experience_level} nível de experiência em tecnologia",
        "experience_level": experience_level,
        "technical_skills": {
            "programming_languages": programming_languages,
            "frameworks": frameworks,
            "tools": tools,
            "databases": databases,
            "cloud_services": cloud_services,
        },
        "career_recommendations": recommendations,
        "skill_gaps": [
            "Considere aprender Docker e containers para modernizar desenvolvimento",
            "Habilidades em cloud computing são valorizadas no mercado atual",
        ],
        "suggested_roles": suggest_roles(
            programming_languages, frameworks, experience_level
        ),
        "market_insights": "Mercado de tecnologia em constante crescimento, com alta demanda por profissionais qualificados",
    }


def detect_skills(text, skill_list):
    """Detecta habilidades no texto"""
    return [skill for skill in skill_list if skill in text]


def determine_experience_level(text):
    """Determina nível de experiência baseado no texto"""
    text_lower = text.lower()

    if any(
        word in text_lower
        for word in [
            "sênior",
            "senior",
            "sr.",
            "especialista",
            "lead",
            "principal",
            "architect",
        ]
    ):
        return "Sênior"
    elif any(
        word in text_lower for word in ["pleno", "mid-level", "experienced", "analista"]
    ):
        return "Pleno"
    elif any(
        word in text_lower
        for word in ["júnior", "junior", "jr.", "estagiário", "estagiario", "trainee"]
    ):
        return "Júnior"
    else:
        # Tenta inferir por anos de experiência
        years_match = re.search(r"(\d+)\s*(ano|anos|year|years)", text_lower)
        if years_match:
            years = int(years_match.group(1))
            if years >= 5:
                return "Sênior"
            elif years >= 2:
                return "Pleno"
        return "Júnior"


def generate_recommendations(languages, frameworks, level):
    """Gera recomendações baseadas nas habilidades"""
    recommendations = []

    if not languages:
        recommendations.append(
            "Aprenda uma linguagem de programação principal como Python ou JavaScript"
        )

    if (
        "python" in languages
        and "django" not in frameworks
        and "flask" not in frameworks
    ):
        recommendations.append(
            "Explore frameworks Python como Django ou Flask para desenvolvimento web"
        )

    if level == "Júnior":
        recommendations.append(
            "Fortaleça fundamentos de algoritmos e estruturas de dados"
        )
        recommendations.append(
            "Participe de projetos open source para ganhar experiência prática"
        )
    elif level == "Pleno":
        recommendations.append(
            "Desenvolva habilidades em arquitetura de software e design patterns"
        )
        recommendations.append("Aprenda sobre DevOps e CI/CD para entrega contínua")
    elif level == "Sênior":
        recommendations.append(
            "Mentore desenvolvedores juniores e contribua para decisões técnicas"
        )
        recommendations.append(
            "Aprimore habilidades em arquitetura de sistemas distribuídos"
        )

    recommendations.append(
        "Mantenha-se atualizado com as tendências do mercado de tecnologia"
    )

    return recommendations[:3]  # Retorna apenas as 3 principais


def suggest_roles(languages, frameworks, level):
    """Sugere cargos baseados nas habilidades"""
    roles = []

    has_frontend = any(fw in frameworks for fw in ["react", "angular", "vue"])
    has_backend = any(
        fw in frameworks for fw in ["django", "flask", "spring", "express"]
    )

    if has_frontend and has_backend:
        roles.append("Desenvolvedor Full Stack")
    elif has_frontend:
        roles.append("Desenvolvedor Frontend")
    elif has_backend:
        roles.append("Desenvolvedor Backend")

    if "python" in languages and not has_backend:
        roles.append("Analista de Dados")
        roles.append("Cientista de Dados")

    if any(
        tool in ["docker", "kubernetes", "aws", "azure"]
        for tool in (languages + frameworks)
    ):
        roles.append("Engenheiro de DevOps")

    # Adiciona nível aos cargos
    level_roles = []
    for role in roles[:2]:  # Pega até 2 cargos principais
        level_roles.append(f"{role} {level}")

    if not level_roles:
        level_roles = [f"Desenvolvedor de Software {level}"]

    return level_roles


def generate_fallback_interview_guide(resume_text: str, job_description: str) -> dict:
    """Guia de entrevista de fallback caso o Gemini falhe"""
    
    text_lower = resume_text.lower()
    job_desc_lower = job_description.lower()
    
    # Detecta habilidades relevantes
    programming_languages = detect_skills(text_lower, [
        "python", "java", "javascript", "typescript", "c#", "c++", "php", "ruby", 
        "go", "rust", "swift", "kotlin", "dart", "r", "matlab"
    ])
    
    frameworks = detect_skills(text_lower, [
        "django", "flask", "fastapi", "spring", "react", "angular", "vue", "node.js",
        "express", "laravel", "ruby on rails", "asp.net", "next.js", "nuxt.js"
    ])
    
    # Análise básica de alinhamento
    matching_skills = []
    for skill in programming_languages + frameworks:
        if skill in job_desc_lower:
            matching_skills.append(skill)
    
    return {
        "preparation_overview": f"Perfil com {len(matching_skills)} habilidades alinhadas com a vaga. Foque em destacar experiências específicas.",
        "strength_analysis": {
            "key_strengths": matching_skills[:3],
            "alignment_points": ["Experiência técnica compatível", "Habilidades transferíveis relevantes"]
        },
        "technical_preparation": {
            "programming_languages": [
                {
                    "topic": lang,
                    "focus_points": ["Conceitos fundamentais", "Melhores práticas", "Projetos relevantes"],
                    "expected_level": "Revisar conceitos avançados" if len(matching_skills) > 3 else "Fortalecer fundamentos"
                } for lang in programming_languages[:2]
            ],
            "frameworks_tools": [
                {
                    "topic": framework,
                    "key_concepts": ["Arquitetura", "Padrões de projeto", "Casos de uso comuns"],
                    "practical_examples": ["Descrever projeto usando esta tecnologia"]
                } for framework in frameworks[:2]
            ],
            "system_design": [
                {
                    "topic": "Design de sistemas escaláveis",
                    "preparation_guide": "Revisar conceitos de escalabilidade e resiliência"
                }
            ]
        },
        "behavioral_preparation": {
            "storytelling_points": [
                {
                    "situation": "Projeto técnico desafiador",
                    "key_achievements": ["Entregas realizadas", "Problemas resolvidos"],
                    "metrics": "Resultados alcançados"
                }
            ],
            "common_questions": [
                {
                    "question": "Conte sobre um projeto complexo que você liderou",
                    "preparation_tips": "Use a metodologia STAR (Situação, Tarefa, Ação, Resultado)",
                    "resume_connection": "Relacione com projetos mencionados no currículo"
                }
            ]
        },
        "company_specific_preparation": {
            "research_topics": ["Produtos/serviços da empresa", "Cultura organizacional"],
            "questions_to_ask": [
                "Quais são os maiores desafios técnicos atuais?",
                "Como é o ciclo de desenvolvimento na equipe?",
                "Quais as oportunidades de aprendizado e crescimento?"
            ]
        },
        "study_plan_timeline": {
            "immediate_24h": ["Revisar projetos do currículo", "Praticar conceitos técnicos básicos"],
            "next_3_days": ["Estudar tópicos específicos da vaga", "Preparar exemplos comportamentais"],
            "week_before": ["Revisão geral", "Simular entrevista com colega"]
        }
    }


def build_fallback_response(text: str) -> dict:
    """Constrói uma resposta de fallback quando o JSON não pode ser parseado"""
    # Análise básica do texto para extrair informações
    lines = text.split('\n')
    key_strengths = []
    alignment_points = []
    
    # Procura por padrões comuns na resposta
    for line in lines:
        line_lower = line.lower()
        if any(word in line_lower for word in ['força', 'strength', 'ponto forte', 'habilidade']):
            if len(line) > 10:  # Evita linhas muito curtas
                key_strengths.append(line.strip())
        elif any(word in line_lower for word in ['alinhamento', 'alignment', 'compatível', 'match']):
            if len(line) > 10:
                alignment_points.append(line.strip())
    
    # Se não encontrou nada, usa valores padrão
    if not key_strengths:
        key_strengths = ["Habilidades técnicas relevantes", "Experiência em projetos de dados"]
    if not alignment_points:
        alignment_points = ["Perfil compatível com a vaga", "Experiência alinhada com os requisitos"]
    
    return {
        "preparation_overview": "Análise realizada com sucesso. Foque em destacar suas experiências técnicas durante a entrevista.",
        "strength_analysis": {
            "key_strengths": key_strengths[:3],
            "alignment_points": alignment_points[:2]
        },
        "technical_preparation": {
            "programming_languages": [
                {
                    "topic": "Python",
                    "focus_points": ["Estruturas de dados", "Bibliotecas de análise (Pandas, NumPy)", "Automação de scripts"],
                    "expected_level": "Intermediário"
                }
            ],
            "frameworks_tools": [
                {
                    "topic": "Power BI",
                    "key_concepts": ["Criação de dashboards", "DAX para cálculos", "Modelagem de dados"],
                    "practical_examples": ["Prepare exemplos de relatórios que criou"]
                }
            ],
            "system_design": [
                {
                    "topic": "Arquitetura de BI",
                    "preparation_guide": "Estude conceitos de ETL e modelagem dimensional"
                }
            ]
        },
        "behavioral_preparation": {
            "storytelling_points": [
                {
                    "situation": "Projeto de análise de dados",
                    "key_achievements": ["Automação de processos", "Geração de insights", "Otimização de relatórios"],
                    "metrics": "Redução de tempo de análise em X%"
                }
            ],
            "common_questions": [
                {
                    "question": "Como você lida com prazos apertados?",
                    "preparation_tips": "Destaque sua organização e priorização",
                    "resume_connection": "Mencione projetos com entregas rápidas do currículo"
                }
            ]
        },
        "company_specific_preparation": {
            "research_topics": ["Setor de atuação da empresa", "Cultura de dados da organização"],
            "questions_to_ask": [
                "Quais são os principais desafios de dados atuais?",
                "Como é o fluxo de trabalho da equipe de BI?",
                "Quais ferramentas complementares são utilizadas?"
            ]
        },
        "study_plan_timeline": {
            "immediate_24h": ["Revisar projetos de Power BI", "Praticar consultas SQL"],
            "next_3_days": ["Estudar conceitos de storytelling com dados", "Preparar casos de uso"],
            "week_before": ["Revisar portfólio", "Simular entrevista técnica"]
        }
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
