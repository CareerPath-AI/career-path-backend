from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import google.generativeai as genai
import io
import os
import json
import re

load_dotenv()

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente")

genai.configure(api_key=GEMINI_API_KEY)

@app.post("/analyze-resume/")
async def analyze_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF")

    try:
        # Lê e extrai texto do PDF
        contents = await file.read()
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="O arquivo está vazio")

        pdf_file = io.BytesIO(contents)
        reader = PdfReader(pdf_file)

        if reader.is_encrypted:
            raise HTTPException(status_code=400, detail="PDF criptografado não é suportado")

        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if not text.strip():
            raise HTTPException(status_code=400, detail="Nenhum texto foi encontrado no PDF")

        # Analisa o currículo com Gemini
        analysis_result = await analyze_with_gemini(text)

        return JSONResponse({
            "filename": file.filename,
            "total_pages": len(reader.pages),
            "analysis": analysis_result
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar o currículo: {str(e)}"
        )

def extract_json_from_text(text: str) -> dict:
    """Extrai JSON do texto de resposta"""
    try:
        # Tenta parsear diretamente
        return json.loads(text)
    except json.JSONDecodeError:
        # Tenta encontrar JSON dentro do texto
        json_match = re.search(r'\{[^{}]*\{[^{}]*\}[^{}]*\}|\{[^{}]*\}', text, re.DOTALL)
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
            "cloud_services": []
        },
        "career_recommendations": [],
        "skill_gaps": [],
        "suggested_roles": [],
        "market_insights": "Análise textual realizada com sucesso"
    }

async def analyze_with_gemini(resume_text: str) -> dict:
    """Analisa o currículo usando Google Gemini com modelos disponíveis"""
    
    truncated_text = resume_text[:6000]
    
    prompt = """
    Você é um especialista em análise de currículos para carreiras em tecnologia. 
    Analise este currículo e retorne APENAS um objeto JSON válido, sem nenhum texto adicional.

    FORMATO EXATO DO JSON:
    {
        "professional_summary": "Resumo profissional em 2-3 frases",
        "experience_level": "Júnior | Pleno | Sênior | Especialista",
        "technical_skills": {
            "programming_lendations": [
            "Aprofundar conhecimentos em arquitetura de sistemas distribuídos.",anguages": ["lista de linguagens encontradas"],
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
        model = genai.GenerativeModel('gemini-2.0-flash-001')
        
        response = model.generate_content(
            f"{prompt}\n\nTEXTO DO CURRÍCULO:\n{truncated_text}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=1500,
                top_p=0.8,
                top_k=40
            )
        )
        
        response_text = response.text.strip()
        print(f"Resposta do Gemini: {response_text}")
        
        return extract_json_from_text(response_text)

    except Exception as e:
        print(f"Erro no Gemini: {str(e)}")
        # Fallback para análise local
        return local_resume_analysis(truncated_text)

def local_resume_analysis(resume_text: str) -> dict:
    """Análise local de fallback caso o Gemini falhe"""
    text_lower = resume_text.lower()
    
    # Detecta habilidades baseado em palavras-chave
    programming_languages = detect_skills(text_lower, [
        "python", "java", "javascript", "typescript", "c#", "c++", "php", "ruby", 
        "go", "rust", "swift", "kotlin", "dart", "r", "matlab"
    ])
    
    frameworks = detect_skills(text_lower, [
        "django", "flask", "fastapi", "spring", "react", "angular", "vue", "node.js",
        "express", "laravel", "ruby on rails", "asp.net", "next.js", "nuxt.js"
    ])
    
    tools = detect_skills(text_lower, [
        "git", "docker", "kubernetes", "jenkins", "github", "gitlab", "jira", 
        "confluence", "postman", "figma", "photoshop", "illustrator"
    ])
    
    databases = detect_skills(text_lower, [
        "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle", "sql server",
        "cassandra", "dynamodb", "firebase"
    ])
    
    cloud_services = detect_skills(text_lower, [
        "aws", "azure", "gcp", "google cloud", "amazon web services", "lambda",
        "ec2", "s3", "cloud functions", "heroku", "digital ocean"
    ])
    
    # Determina nível de experiência
    experience_level = determine_experience_level(resume_text)
    
    # Gera recomendações baseadas nas habilidades encontradas
    recommendations = generate_recommendations(programming_languages, frameworks, experience_level)
    
    return {
        "professional_summary": f"Perfil analisado com {experience_level} nível de experiência em tecnologia",
        "experience_level": experience_level,
        "technical_skills": {
            "programming_languages": programming_languages,
            "frameworks": frameworks,
            "tools": tools,
            "databases": databases,
            "cloud_services": cloud_services
        },
        "career_recommendations": recommendations,
        "skill_gaps": [
            "Considere aprender Docker e containers para modernizar desenvolvimento",
            "Habilidades em cloud computing são valorizadas no mercado atual"
        ],
        "suggested_roles": suggest_roles(programming_languages, frameworks, experience_level),
        "market_insights": "Mercado de tecnologia em constante crescimento, com alta demanda por profissionais qualificados"
    }

def detect_skills(text, skill_list):
    """Detecta habilidades no texto"""
    return [skill for skill in skill_list if skill in text]

def determine_experience_level(text):
    """Determina nível de experiência baseado no texto"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ["sênior", "senior", "sr.", "especialista", "lead", "principal", "architect"]):
        return "Sênior"
    elif any(word in text_lower for word in ["pleno", "mid-level", "experienced", "analista"]):
        return "Pleno"
    elif any(word in text_lower for word in ["júnior", "junior", "jr.", "estagiário", "estagiario", "trainee"]):
        return "Júnior"
    else:
        # Tenta inferir por anos de experiência
        years_match = re.search(r'(\d+)\s*(ano|anos|year|years)', text_lower)
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
        recommendations.append("Aprenda uma linguagem de programação principal como Python ou JavaScript")
    
    if "python" in languages and "django" not in frameworks and "flask" not in frameworks:
        recommendations.append("Explore frameworks Python como Django ou Flask para desenvolvimento web")
    
    if level == "Júnior":
        recommendations.append("Fortaleça fundamentos de algoritmos e estruturas de dados")
        recommendations.append("Participe de projetos open source para ganhar experiência prática")
    elif level == "Pleno":
        recommendations.append("Desenvolva habilidades em arquitetura de software e design patterns")
        recommendations.append("Aprenda sobre DevOps e CI/CD para entrega contínua")
    elif level == "Sênior":
        recommendations.append("Mentore desenvolvedores juniores e contribua para decisões técnicas")
        recommendations.append("Aprimore habilidades em arquitetura de sistemas distribuídos")
    
    recommendations.append("Mantenha-se atualizado com as tendências do mercado de tecnologia")
    
    return recommendations[:3]  # Retorna apenas as 3 principais

def suggest_roles(languages, frameworks, level):
    """Sugere cargos baseados nas habilidades"""
    roles = []
    
    has_frontend = any(fw in frameworks for fw in ["react", "angular", "vue"])
    has_backend = any(fw in frameworks for fw in ["django", "flask", "spring", "express"])
    
    if has_frontend and has_backend:
        roles.append("Desenvolvedor Full Stack")
    elif has_frontend:
        roles.append("Desenvolvedor Frontend")
    elif has_backend:
        roles.append("Desenvolvedor Backend")
    
    if "python" in languages and not has_backend:
        roles.append("Analista de Dados")
        roles.append("Cientista de Dados")
    
    if any(tool in ["docker", "kubernetes", "aws", "azure"] for tool in (languages + frameworks)):
        roles.append("Engenheiro de DevOps")
    
    # Adiciona nível aos cargos
    level_roles = []
    for role in roles[:2]:  # Pega até 2 cargos principais
        level_roles.append(f"{role} {level}")
    
    if not level_roles:
        level_roles = [f"Desenvolvedor de Software {level}"]
    
    return level_roles

# Endpoint para listar modelos disponíveis
@app.get("/models")
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

# Endpoint de healthcheck
@app.get("/")
async def root():
    return {
        "message": "API de Análise de Currículos com Google Gemini",
        "status": "online",
        "model": "gemini-2.0-flash-001"
    }