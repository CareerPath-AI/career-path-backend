from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.tasks import start_token_cleanup_scheduler, scheduler
from app.routes.resume_analysis_routes import analyze_resume_router
from app.routes.check_routes import check_router
from app.routes.interview_guide_routes import interview_guide_router
from app.routes.development_trail_routes import development_trail_router
from app.routes.auth_routes import auth_router
import os

os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_POLL_STRATEGY"] = "poll"


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_token_cleanup_scheduler()

    yield

    if scheduler and scheduler.running:
        scheduler.shutdown()


app = FastAPI(
    title=settings.APP_NAME,
    description="CareerPath-AI Swagger",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(check_router)
app.include_router(analyze_resume_router)
app.include_router(interview_guide_router)
app.include_router(development_trail_router)
app.include_router(auth_router)
