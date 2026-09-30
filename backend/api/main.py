from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.responses import JSONResponse
from time import monotonic
from uuid import uuid4
from backend.core.config import settings
from backend.core.logging import configure_logging
from backend.core.runtime import JROCRuntime
from backend.database.database import init_db
from backend.api.routes.health import router as health_router
from backend.api.routes.system import router as system_router
from backend.api.routes.auth import router as auth_router
from backend.api.routes.memory import router as memory_router
from backend.api.routes.missions import router as missions_router
from backend.api.routes.departments import router as departments_router
from backend.api.routes.agents import router as agents_router
from backend.api.routes.agent_control import router as agent_control_router
from backend.api.routes.agent_routing import router as agent_routing_router
from backend.api.routes.swarm import router as swarm_router
from backend.api.routes.telemetry import router as telemetry_router
from backend.api.routes.orchestrator import router as orchestrator_router
from backend.api.routes.knowledge import router as knowledge_router
from backend.api.routes.workflows import router as workflows_router
from backend.api.routes.tools import router as tools_router
from backend.api.routes.decisions import router as decisions_router
from backend.api.routes.recovery import router as recovery_router
from backend.api.routes.optimization import router as optimization_router
from backend.api.routes.mission_management import router as mission_management_router
from backend.api.routes.os import router as os_router
from backend.api.routes.organizations import router as organizations_router
from backend.api.routes.apps import router as apps_router
from backend.api.routes.marketplace import router as marketplace_router
from backend.api.routes.academy import router as academy_router
from backend.api.routes.economy import router as economy_router
from backend.api.routes.network import router as network_router
from backend.api.routes.ecosystem import router as ecosystem_router
from backend.api.routes.endgame import router as endgame_router
from backend.api.routes.civilization import router as civilization_router
from backend.api.routes.commercial import router as commercial_router
from backend.api.routes.business_os import router as business_os_router
from backend.api.routes.personal_os import router as personal_os_router
from backend.api.routes.voice import router as voice_router
from backend.api.routes.notifications import router as notifications_router
from backend.api.routes.production import router as production_router
from backend.api.routes.chairman import router as chairman_router
from backend.api.routes.connectors import router as connectors_router
from backend.api.routes.secrets import router as secrets_router
from backend.api.routes.healing import router as healing_router
from backend.api.routes.auto_repair import router as auto_repair_router
from backend.api.routes.repair_gateway import router as repair_gateway_router
from backend.api.routes.deploy_recovery import router as deploy_recovery_router
from backend.api.routes.public_status import router as public_status_router
from backend.api.routes.public_intelligence import router as public_intelligence_router
from backend.api.routes.brain import router as brain_router
from backend.api.routes.executives import router as executives_router
from backend.api.routes.intelligence import router as intelligence_router
from backend.api.routes.engineering import router as engineering_router
from backend.api.routes.git_workers import router as git_workers_router
from backend.api.routes.agents_catalog import router as agents_catalog_router
from backend.workforce.runtime import get_workforce_runtime
from backend.api.routes.cloud import router as cloud_router
from backend.api.routes.compute import router as compute_router

configure_logging()
runtime = JROCRuntime()

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_runtime()
    init_db()
    from backend.database.database import SessionLocal
    db = SessionLocal()
    try:
        get_workforce_runtime().hydrate(db)
    finally:
        db.close()
    await runtime.start()
    yield
    await runtime.stop()

app = FastAPI(title="J-ROC AI Platform Core", version="0.35.0", lifespan=lifespan)
if settings.require_https:
    app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_host_list)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"], allow_headers=["Authorization","Content-Type","X-Request-ID"])

_rate_window: dict[str, tuple[float, int]] = {}
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    client = request.client.host if request.client else "unknown"
    now = monotonic()
    start, count = _rate_window.get(client, (now, 0))
    if now - start >= 60: start, count = now, 0
    count += 1
    _rate_window[client] = (start, count)
    if count > settings.rate_limit_per_minute:
        return JSONResponse(status_code=429, content={"error":"rate_limit_exceeded","request_id":request_id}, headers={"X-Request-ID":request_id})
    try: response = await call_next(request)
    except Exception: response = JSONResponse(status_code=500, content={"error":"internal_server_error","request_id":request_id})
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(self), geolocation=()"
    if settings.require_https: response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

app.include_router(health_router)
app.include_router(system_router, prefix="/api/system", tags=["system"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(memory_router, prefix="/api/memory", tags=["memory"])
app.include_router(missions_router, prefix="/api/missions", tags=["missions"])
app.include_router(departments_router, prefix="/api/departments", tags=["departments"])
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
app.include_router(agent_control_router, prefix="/api/agent-control", tags=["agent-control"])
app.include_router(agent_routing_router, prefix="/api/agent-routing", tags=["agent-routing"])
app.include_router(swarm_router, prefix="/api/swarms", tags=["swarms"])
app.include_router(telemetry_router, prefix="/api/telemetry", tags=["telemetry"])
app.include_router(orchestrator_router, prefix="/api/orchestrator", tags=["orchestrator"])
app.include_router(knowledge_router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(workflows_router, prefix="/api/workflows", tags=["workflows"])
app.include_router(tools_router, prefix="/api/tools", tags=["tools"])
app.include_router(decisions_router, prefix="/api/decisions", tags=["decisions"])
app.include_router(recovery_router, prefix="/api/recovery", tags=["recovery"])
app.include_router(optimization_router, prefix="/api/optimization", tags=["optimization"])
app.include_router(mission_management_router, prefix="/api/mission-management", tags=["mission-management"])
app.include_router(os_router, prefix="/api/os", tags=["jroc-os"])
app.include_router(organizations_router, prefix="/api/organizations", tags=["organizations"])
app.include_router(apps_router, prefix="/api/apps", tags=["apps"])
app.include_router(marketplace_router, prefix="/api/marketplace", tags=["marketplace"])
app.include_router(academy_router, prefix="/api/academy", tags=["academy"])
app.include_router(economy_router, prefix="/api/economy", tags=["economy"])
app.include_router(network_router, prefix="/api/network", tags=["network"])
app.include_router(ecosystem_router, prefix="/api/ecosystem", tags=["ecosystem"])
app.include_router(endgame_router, prefix="/api/endgame", tags=["endgame"])
app.include_router(civilization_router, prefix="/api/civilization", tags=["civilization"])
app.include_router(commercial_router, prefix="/api/commercial", tags=["commercial-os"])
app.include_router(business_os_router, prefix="/api/business-os", tags=["business-os"])
app.include_router(personal_os_router, prefix="/api/personal-os", tags=["personal-os"])
app.include_router(voice_router, prefix="/api/voice", tags=["voice"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["notifications"])
app.include_router(production_router, prefix="/api/production", tags=["production"])
app.include_router(chairman_router, prefix="/api/chairman", tags=["chairman"])
app.include_router(connectors_router, prefix="/api/connectors", tags=["connectors"])
app.include_router(secrets_router, prefix="/api/secrets", tags=["secrets"])
app.include_router(healing_router, prefix="/api/healing", tags=["healing"])
app.include_router(auto_repair_router, prefix="/api/auto-repair", tags=["auto-repair"])
app.include_router(repair_gateway_router, prefix="/api/repair-gateway", tags=["repair-gateway"])
app.include_router(deploy_recovery_router, prefix="/api/deploy-recovery", tags=["deploy-recovery"])
app.include_router(public_status_router, prefix="/api/public", tags=["public-status"])
app.include_router(public_intelligence_router, prefix="/api/public", tags=["public-intelligence"])
app.include_router(brain_router, prefix="/api/brain", tags=["brain"])
app.include_router(executives_router, prefix="/api/executives", tags=["executives"])
app.include_router(intelligence_router, prefix="/api/intelligence", tags=["intelligence"])
app.include_router(engineering_router, prefix="/api/engineering", tags=["engineering"])
app.include_router(git_workers_router, prefix="/api/workforce", tags=["git-workers"])
app.include_router(agents_catalog_router, prefix="/api/agents", tags=["agents"])
app.include_router(cloud_router, prefix="/api/cloud", tags=["jroc-cloud"])
app.include_router(compute_router, prefix="/api/cloud", tags=["jroc-compute"])
