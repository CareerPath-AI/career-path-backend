# career-path-backend
Repositório do BackEnd do CareerPath-AI.

## Descrição
API para análise de currículos utilizando Google Gemini AI. A aplicação extrai informações de PDFs e fornece análise detalhada de habilidades, nível de experiência, recomendações de carreira e insights de mercado.

## Pré-requisitos
- Python 3.13
- Chave de API do Google Gemini

## Configuração e Execução

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd career-path-backend
```

### 2. Instalar o gerenciador de pacotes uv
#### No Linux/Mac
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### No Windows 
```bash
irm https://astral.sh/uv/install.ps1 | iex
```

#### Em seguida, verifique se o uv foi instalado corretamente:
```bash
uv --version
```

### 3. Instalar as dependências e ativar ambiente virtual
```bash
uv sync
```

#### No Windows:
```bash
.venv\Scripts\activate
```

#### No Linux/Mac:
```bash
source .venv/bin/activate
```

### 4. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:
```bash
# Copie o arquivo de exemplo
cp .env.example .env
```

Edite o arquivo `.env` e adicione sua chave da API Gemini:
```env
GEMINI_API_KEY=sua_chave_api_gemini_aqui
```

### 5. Execute a aplicação
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Acesse a documentação da API
Após executar a aplicação, acesse:
- **Swagger UI**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

## Testando a API

### 1. Acesse o Swagger UI
Navegue até http://localhost:8000/docs para ver todos os endpoints disponíveis.

### 2. Teste o endpoint de análise de currículo
1. No Swagger UI, expanda o endpoint `POST /analyze-resume/`
2. Clique em "Try it out"
3. Selecione um arquivo PDF de currículo
4. Clique em "Execute"

### 3. Endpoints disponíveis
- `GET /` - Health check da API
- `GET /models` - Lista modelos Gemini disponíveis
- `POST /analyze-resume/` - Analisa um currículo em PDF

## Estrutura do Projeto
```
career-path-backend/
├── app.py              # Aplicação FastAPI principal
├── .env.example        # Exemplo de variáveis de ambiente
├── .gitignore          # Arquivos ignorados pelo Git
├── .python-version     # Versão do Python
└── requirements.txt    # Dependências do projeto
```

## Funcionalidades
- ✅ Extração de texto de PDFs
- ✅ Análise de currículos com Google Gemini AI
- ✅ Detecção de habilidades técnicas
- ✅ Determinação de nível de experiência
- ✅ Recomendações de carreira personalizadas
- ✅ Identificação de lacunas de habilidades
- ✅ Insights de mercado
- ✅ Fallback para análise local caso a API falhe

## Tecnologias Utilizadas
- **FastAPI** - Framework web moderno
- **Google Gemini AI** - IA generativa para análise
- **PyPDF2** - Extração de texto de PDFs
- **Python-dotenv** - Gerenciamento de variáveis de ambiente
- **Uvicorn** - Servidor ASGI

## Troubleshooting

### Erro de chave de API
Certifique-se de que a variável `GEMINI_API_KEY` está configurada corretamente no arquivo `.env`.

### Problemas com PDF
- A API suporta apenas PDFs não criptografados
- PDFs devem conter texto extraível (não apenas imagens)

### Porta em uso
Se a porta 8000 estiver em uso, altere a porta no comando de execução:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```