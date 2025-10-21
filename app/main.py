# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes.analyze_resume_routes import analyze_resume_router
from app.routes.check_routes import check_router
import os

os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_POLL_STRATEGY"] = "poll"

app = FastAPI(
    title=settings.APP_NAME,
    description="CareerPath-AI Swagger",
    version="1.0.0",
    debug=settings.DEBUG,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_resume_router)
app.include_router(check_router)
