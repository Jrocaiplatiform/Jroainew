from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from datetime import datetime, timezone
from backend.api.routes.auth import current_user
from backend.database.database import get_db
from backend.database.models import (
    AgentDefinition,
    AgentTelemetry,
    AppDefinition,
    AuditLog,
    KnowledgeNode,
    MarketplaceItem,
    Memory,
    Mission,
    MissionTask,
    Organization,
    SwarmDefinition,
)
from backend.brains.chairman_brain import ChairmanBrain
from backend.workforce.runtime import get_workforce_runtime
from backend.services.chairman_command_service import ChairmanCommandExecutor
from backend.services.github_mission_queue import GitHubMissionQueue
from backend.api.routes.health import health as _system_health

router = APIRouter()
chairman_brain = ChairmanBrain()
CHAIRMAN_ROLES = {"CHAIRMAN", "EXECUTIVE"}


def _require_chairman(user):
    if user.role != "CHAIRMAN":
        raise HTTPException(status_code=403, detail="Chairman authority required")
    return user


def _require_executive(user):
    if user.role not in CHAIRMAN_ROLES:
        raise HTTPException(status_code=403, detail="Chairman or Executive authority required")
    return user


@router.get("/dashboard")
def dashboard(user=Depends(current_user), db=Depends(get_db)):
    _require_executive(user)
    active_agents = db.query(AgentDefinition).filter(
        AgentDefinition.owner_id == user.id,
        AgentDefinition.active.is_(True),
    ).count()
    active_swarms = db.query(SwarmDefinition).filter(
        SwarmDefinition.owner_id == user.id,
        SwarmDefinition.status.notin_(["COMPLETED", "RETIRED"]),
    ).count()
    mission_rows = db.query(Mission).filter(Mission.chairman_id == user.id)
    return {
        "system": "J-ROC AI Chairman Command Center",
        "status": "online",
        "chairman": {"id": user.id, "username": user.username, "role": user.role},
        "counts": {
            "organizations": db.query(Organization).filter(Organization.owner_id == user.id).count(),
            "departments": 8,
            "agents": active_agents,
            "swarms": active_swarms,
            "apps": db.query(AppDefinition).filter(AppDefinition.owner_id == user.id).count(),
            "marketplace_items": db.query(MarketplaceItem).filter(MarketplaceItem.owner_id == user.id).count(),
            "missions": mission_rows.count(),
            "memories": db.query(Memory).filter(Memory.owner_id == user.id).count(),
            "knowledge_nodes": db.query(KnowledgeNode).filter(KnowledgeNode.owner_id == user.id).count(),
        },
        "operations": {
            "active_missions": mission_rows.filter(
                Mission.status.in_(["RECEIVED", "PLANNING", "VALIDATING", "DELEGATING", "RUNNING", "HEALING"])
            ).count(),
            "completed_missions": mission_rows.filter(Mission.status == "COMPLETED").count(),
            "failed_missions": mission_rows.filter(Mission.status.in_(["FAILED", "REJECTED"])).count(),
        },
    }


@router.get("/briefing")
async def briefing(user=Depends(current_user), db=Depends(get_db)):
    _require_chairman(user)
    dashboard_data = dashboard(user, db)
    directive = await chairman_brain.direct(
        "Prepare a Chairman executive briefing for the current J-ROC ecosystem.",
        str(dashboard_data),
    )
    return {"briefing": directive, "dashboard": dashboard_data}


@router.get("/executives")
def executives(user=Depends(current_user)):
    _require_executive(user)
    return {
        "executives": [
            {"key": "CEO_AI", "role": "CEO", "status": "ACTIVE"},
            {"key": "COO_AI", "role": "COO", "status": "ACTIVE"},
            {"key": "CTO_AI", "role": "CTO", "status": "ACTIVE"},
            {"key": "CFO_AI", "role": "CFO", "status": "ACTIVE"},
            {"key": "CMO_AI", "role": "CMO", "status": "ACTIVE"},
            {"key": "CSO_AI", "role": "CSO", "status": "ACTIVE"},
            {"key": "RESEARCH_AI", "role": "RESEARCH", "status": "ACTIVE"},
            {"key": "PRODUCT_AI", "role": "PRODUCT", "status": "ACTIVE"},
        ]
    }


@router.get("/missions")
def missions(user=Depends(current_user), db=Depends(get_db)):
    _require_executive(user)
    rows = db.query(Mission).filter(Mission.chairman_id == user.id).order_by(Mission.created_at.desc()).limit(50).all()
    return {"missions": [
        {"id": m.id, "objective": m.objective, "status": m.status, "decision": m.decision}
        for m in rows
    ]}


@router.get("/workforce")
def workforce(user=Depends(current_user), db=Depends(get_db)):
    _require_executive(user)
    runtime = get_workforce_runtime()
    workers = runtime.registry.list_workers()
    return {
        "workers": [
            {
                "id": w.id,
                "name": w.name,
                "department": w.department,
                "role": w.role,
                "status": w.status,
                "current_task_id": w.current_task_id,
            }
            for w in workers
        ],
        "capacity": len([w for w in workers if w.status == "AVAILABLE"]),
    }


@router.get("/organizations")
def organizations(user=Depends(current_user), db=Depends(get_db)):
    _require_executive(user)
    rows = db.query(Organization).filter(Organization.owner_id == user.id).all()
    return {"organizations": [
        {"id": o.id, "name": o.name, "plan": o.plan, "active": o.active}
        for o in rows
    ]}


@router.get("/apps")
def apps(user=Depends(current_user), db=Depends(get_db)):
    _require_executive(user)
    rows = db.query(AppDefinition).filter(AppDefinition.owner_id == user.id).all()
    return {"apps": [
        {"id": a.id, "organization_id": a.organization_id, "name": a.name, "slug": a.slug, "status": a.status}
        for a in rows
    ]}


@router.get("/marketplace")
def marketplace(user=Depends(current_user), db=Depends(get_db)):
    _require_executive(user)
    rows = db.query(MarketplaceItem).filter(MarketplaceItem.owner_id == user.id).all()
    return {"items": [
        {"id": i.id, "type": i.item_type, "name": i.name, "price_cents": i.price_cents, "active": i.active}
        for i in rows
    ]}


@router.get("/financials")
def financials(user=Depends(current_user), db=Depends(get_db)):
    _require_chairman(user)
    marketplace_revenue = db.query(func.coalesce(func.sum(MarketplaceItem.price_cents), 0)).filter(
        MarketplaceItem.owner_id == user.id,
        MarketplaceItem.active.is_(True),
    ).scalar()
    return {
        "status": "foundation",
        "cash": None,
        "mrr": None,
        "arr": None,
        "revenue": {"catalog_value_cents": int(marketplace_revenue or 0), "realized": None},
        "note": "Treasury, banking, invoices, subscriptions, and realized revenue models are not yet present in the current core schema.",
    }


@router.get("/security")
def security(user=Depends(current_user), db=Depends(get_db)):
    _require_chairman(user)
    failed = db.query(AuditLog).filter(
        AuditLog.user_id == user.id,
        AuditLog.success.is_(False),
    ).count()
    recent = db.query(AuditLog).filter(AuditLog.user_id == user.id).order_by(AuditLog.created_at.desc()).limit(20).all()
    return {
        "risk_level": "UNKNOWN",
        "failed_events": failed,
        "recent_events": [
            {"event": e.event, "action": e.action, "resource": e.resource, "success": e.success}
            for e in recent
        ],
    }


@router.get("/infrastructure")
def infrastructure(user=Depends(current_user), db=Depends(get_db)):
    _require_executive(user)
    telemetry_count = db.query(AgentTelemetry).filter(AgentTelemetry.agent_id.is_not(None)).count()
    return {
        "status": "online",
        "api": {"status": "online"},
        "database": {"status": "connected"},
        "telemetry": {"events": telemetry_count},
        "queues": {"status": "not_configured"},
        "storage": {"status": "not_configured"},
        "networking": {"status": "managed_externally"},
    }


@router.get("/knowledge")
def knowledge(user=Depends(current_user), db=Depends(get_db)):
    _require_executive(user)
    return {
        "memory_count": db.query(Memory).filter(Memory.owner_id == user.id).count(),
        "knowledge_nodes": db.query(KnowledgeNode).filter(KnowledgeNode.owner_id == user.id).count(),
    }



@router.get("/activity")
def activity(user=Depends(current_user), db=Depends(get_db)):
    _require_executive(user)
    rows = db.query(AuditLog).filter(AuditLog.user_id == user.id).order_by(AuditLog.created_at.desc()).limit(50).all()
    return {"events": [
        {"id": e.id, "event": e.event, "resource": e.resource, "action": e.action,
         "success": e.success, "created_at": e.created_at.isoformat() if e.created_at else None,
         "metadata": e.metadata_json or {}}
        for e in rows
    ]}


@router.get("/health")
def chairman_health(user=Depends(current_user), db=Depends(get_db)):
    _require_executive(user)
    system = _system_health()
    telemetry_total = db.query(AgentTelemetry).join(
        AgentDefinition, AgentTelemetry.agent_id == AgentDefinition.id
    ).filter(AgentDefinition.owner_id == user.id).count()
    return {
        "system": "J-ROC Chairman Command Center",
        "status": system["status"],
        "runtime": system["runtime"],
        "database": system["database"],
        "telemetry": {"events": telemetry_total},
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/metrics")
def metrics(user=Depends(current_user), db=Depends(get_db)):
    _require_executive(user)
    mission_query = db.query(Mission).filter(Mission.chairman_id == user.id)
    telemetry_query = db.query(AgentTelemetry).join(
        AgentDefinition, AgentTelemetry.agent_id == AgentDefinition.id
    ).filter(AgentDefinition.owner_id == user.id)
    audit_query = db.query(AuditLog).filter(AuditLog.user_id == user.id)
    total_telemetry = telemetry_query.count()
    successful_telemetry = telemetry_query.filter(AgentTelemetry.success.is_(True)).count()
    return {
        "missions": {
            "total": mission_query.count(),
            "active": mission_query.filter(Mission.status.in_(["RECEIVED", "PLANNING", "VALIDATING", "DELEGATING", "RUNNING", "HEALING"])).count(),
            "completed": mission_query.filter(Mission.status == "COMPLETED").count(),
            "failed": mission_query.filter(Mission.status.in_(["FAILED", "REJECTED"])).count(),
        },
        "workforce": {
            "agents": db.query(AgentDefinition).filter(AgentDefinition.owner_id == user.id).count(),
            "active_agents": db.query(AgentDefinition).filter(AgentDefinition.owner_id == user.id, AgentDefinition.active.is_(True)).count(),
            "swarms": db.query(SwarmDefinition).filter(SwarmDefinition.owner_id == user.id).count(),
        },
        "telemetry": {
            "events": total_telemetry,
            "successes": successful_telemetry,
            "failures": total_telemetry - successful_telemetry,
            "success_rate": (successful_telemetry / total_telemetry) if total_telemetry else 0,
        },
        "audit": {"events": audit_query.count()},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


class ChairmanCommandRequest(BaseModel):
    objective: str = Field(min_length=1, max_length=5000)
    context: dict = Field(default_factory=dict)


@router.get("/mission/{mission_id}/stream")
def mission_stream(mission_id: str, user=Depends(current_user), db=Depends(get_db)):
    _require_chairman(user)
    mission = db.query(Mission).filter(Mission.id == mission_id, Mission.chairman_id == user.id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    events = db.query(AuditLog).filter(
        AuditLog.user_id == user.id,
        AuditLog.resource == "mission:" + mission_id,
    ).order_by(AuditLog.created_at.asc()).all()
    tasks = db.query(MissionTask).filter(MissionTask.mission_id == mission_id).all()
    return {
        "mission_id": mission.id,
        "status": mission.status,
        "decision": mission.decision,
        "tasks": [{"id": t.id, "title": t.title, "status": t.status, "department": t.department, "worker_id": t.worker_id} for t in tasks],
        "events": [
            {"event": e.event, "action": e.action, "success": e.success,
             "created_at": e.created_at.isoformat() if e.created_at else None,
             "metadata": e.metadata_json or {}}
            for e in events
        ],
    }


@router.post("/command")
async def chairman_command(request: ChairmanCommandRequest, background_tasks: BackgroundTasks, user=Depends(current_user), db=Depends(get_db)):
    _require_chairman(user)
    from backend.services.mission_service import MissionService
    from backend.services.audit_service import AuditService
    mission_service = MissionService()
    mission = mission_service.create(db, user.id, request.objective, request.context)
    AuditService().record(
        db,
        "CHAIRMAN_COMMAND_RECEIVED",
        user.id,
        "mission:" + mission.id,
        "COMMAND",
        metadata={"source": request.context.get("source", "chairman")},
    )
    try:
        queued = GitHubMissionQueue().enqueue(mission.id, request.objective, user.id)
        mission.status = "QUEUED"
        db.commit()
        AuditService().record(
            db, "MISSION_QUEUED", user.id, "mission:" + mission.id, "QUEUE",
            metadata={"github_issue": queued.issue_url, "issue_number": str(queued.issue_number)},
        )
        return {
            "authority": "CHAIRMAN",
            "objective": request.objective,
            "mission_id": mission.id,
            "status": "QUEUED",
            "queue": {"provider": "github-actions", "issue_url": queued.issue_url, "issue_number": queued.issue_number},
            "result": {"decision": "EXECUTING", "message": "Mission queued durably. You may leave; GitHub Actions will execute it."},
        }
    except Exception as exc:
        background_tasks.add_task(ChairmanCommandExecutor().run, mission.id, user.id, request.objective)
        return {
            "authority": "CHAIRMAN",
            "objective": request.objective,
            "mission_id": mission.id,
            "status": mission.status,
            "result": {"decision": "EXECUTING", "message": "GitHub queue unavailable; local background execution started.", "queue_error": str(exc)},
        }
