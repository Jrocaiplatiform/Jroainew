from fastapi import APIRouter
from backend.database.database import check_db
from backend.core.config import settings

router = APIRouter()

@router.get("/health")
def health():
    from backend.api.main import runtime
    db_ok = check_db()
    return {"system": "J-ROC", "status": "online" if db_ok and runtime.started else "degraded", "runtime": runtime.started, "database": db_ok}

@router.get("/live")
def live():
    return {"status": "alive", "system": "J-ROC"}

@router.get("/ready")
def ready():
    from backend.api.main import runtime
    db_ok = check_db()
    ready_state = bool(db_ok and runtime.started)
    return {"status": "ready" if ready_state else "not_ready", "database": db_ok, "runtime": runtime.started, "environment": settings.environment}
