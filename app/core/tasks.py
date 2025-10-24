from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.token_cleanup import cleanup_expired_tokens
from app.dependencies.database import get_db

scheduler = BackgroundScheduler()

def start_token_cleanup_scheduler():
    """
    Inicia o scheduler de limpeza de tokens
    """
    if not scheduler.running:
        scheduler.add_job(
            cleanup_expired_tokens,
            "interval",
            hours=24,
            args=[next(get_db())]
        )
        scheduler.start()
