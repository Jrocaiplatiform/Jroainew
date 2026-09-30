from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), default="OBSERVER")
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class Memory(Base):
    __tablename__ = "memories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    namespace: Mapped[str] = mapped_column(String(50), index=True)
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    key: Mapped[str] = mapped_column(String(200), index=True)
    title: Mapped[str] = mapped_column(String(255), default="")
    content: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    event: Mapped[str] = mapped_column(String(100), index=True)
    resource: Mapped[str] = mapped_column(String(255), default="")
    action: Mapped[str] = mapped_column(String(50), default="")
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class AgentDefinition(Base):
    __tablename__ = "agent_definitions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    department: Mapped[str] = mapped_column(String(100), index=True)
    role: Mapped[str] = mapped_column(String(100), default="SPECIALIST_WORKER")
    capabilities_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    instructions: Mapped[str] = mapped_column(Text, default="")
    model_policy: Mapped[str] = mapped_column(String(100), default="free-tier-failover")
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    lifecycle_status: Mapped[str] = mapped_column(String(30), default="ACTIVE", index=True)
    retired_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Mission(Base):
    __tablename__ = "missions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    chairman_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    objective: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="RECEIVED", index=True)
    decision: Mapped[str | None] = mapped_column(String(40), nullable=True)
    context_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    result_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class MissionTask(Base):
    __tablename__ = "mission_tasks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    mission_id: Mapped[str] = mapped_column(ForeignKey("missions.id"), index=True)
    title: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="READY", index=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    worker_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    result_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class SwarmDefinition(Base):
    __tablename__="swarm_definitions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    mission_id: Mapped[str|None] = mapped_column(String(36), nullable=True, index=True)
    supervisor_agent_id: Mapped[str|None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="READY", index=True)
    config_json: Mapped[dict|None] = mapped_column(JSON, nullable=True)
    owner_id: Mapped[int|None] = mapped_column(Integer, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class SwarmMember(Base):
    __tablename__="swarm_members"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    swarm_id: Mapped[str] = mapped_column(ForeignKey("swarm_definitions.id"), index=True)
    agent_id: Mapped[str] = mapped_column(String(36), index=True)
    role: Mapped[str] = mapped_column(String(50), default="WORKER")
    status: Mapped[str] = mapped_column(String(30), default="READY")

class AgentMessage(Base):
    __tablename__="agent_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    swarm_id: Mapped[str|None] = mapped_column(String(36), nullable=True, index=True)
    sender_agent_id: Mapped[str] = mapped_column(String(36), index=True)
    recipient_agent_id: Mapped[str|None] = mapped_column(String(36), nullable=True, index=True)
    message_type: Mapped[str] = mapped_column(String(40), default="TASK")
    content: Mapped[str] = mapped_column(Text)
    context_json: Mapped[dict|None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class AgentTelemetry(Base):
    __tablename__="agent_telemetry"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(36), index=True)
    mission_id: Mapped[str|None] = mapped_column(String(36), nullable=True, index=True)
    task_id: Mapped[str|None] = mapped_column(String(36), nullable=True, index=True)
    event: Mapped[str] = mapped_column(String(50), index=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    latency_ms: Mapped[int|None] = mapped_column(Integer, nullable=True)
    provider: Mapped[str|None] = mapped_column(String(100), nullable=True)
    model: Mapped[str|None] = mapped_column(String(150), nullable=True)
    metadata_json: Mapped[dict|None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class KnowledgeNode(Base):
    __tablename__="knowledge_nodes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[int|None] = mapped_column(Integer, nullable=True, index=True)
    node_type: Mapped[str] = mapped_column(String(50), index=True)
    key: Mapped[str] = mapped_column(String(200), index=True)
    content: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict|None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class KnowledgeEdge(Base):
    __tablename__="knowledge_edges"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int|None] = mapped_column(Integer, nullable=True, index=True)
    source_id: Mapped[str] = mapped_column(String(36), index=True)
    target_id: Mapped[str] = mapped_column(String(36), index=True)
    relation: Mapped[str] = mapped_column(String(80), index=True)
    metadata_json: Mapped[dict|None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class WorkflowDefinition(Base):
    __tablename__="workflow_definitions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    steps_json: Mapped[list] = mapped_column(JSON, default=list)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class WorkflowRun(Base):
    __tablename__="workflow_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    workflow_id: Mapped[str] = mapped_column(String(36), index=True)
    owner_id: Mapped[int] = mapped_column(Integer, index=True)
    status: Mapped[str] = mapped_column(String(30), default="RUNNING", index=True)
    input_json: Mapped[dict|None] = mapped_column(JSON, nullable=True)
    result_json: Mapped[dict|None] = mapped_column(JSON, nullable=True)
    error_json: Mapped[dict|None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    finished_at: Mapped[datetime|None] = mapped_column(DateTime, nullable=True)

class Organization(Base):
    __tablename__="organizations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    plan: Mapped[str] = mapped_column(String(50), default="free")
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class OrganizationMember(Base):
    __tablename__="organization_members"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(40), default="MEMBER")
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class AppDefinition(Base):
    __tablename__="app_definitions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    slug: Mapped[str] = mapped_column(String(180), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    config_json: Mapped[dict|None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class MarketplaceItem(Base):
    __tablename__="marketplace_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    organization_id: Mapped[str|None] = mapped_column(ForeignKey("organizations.id"), nullable=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    item_type: Mapped[str] = mapped_column(String(40), index=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    payload_json: Mapped[dict|None] = mapped_column(JSON, nullable=True)
    price_cents: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class AppVersion(Base):
    __tablename__="app_versions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    app_id: Mapped[str] = mapped_column(ForeignKey("app_definitions.id"), index=True)
    version: Mapped[str] = mapped_column(String(40))
    config_json: Mapped[dict|None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class AppInstallation(Base):
    __tablename__="app_installations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    app_id: Mapped[str] = mapped_column(ForeignKey("app_definitions.id"), index=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    installed_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="INSTALLED", index=True)
    installed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class MarketplaceInstall(Base):
    __tablename__="marketplace_installs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    item_id: Mapped[str] = mapped_column(ForeignKey("marketplace_items.id"), index=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    installed_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="INSTALLED", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class ConnectorConnection(Base):
    __tablename__ = "connector_connections"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    connector_key: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(30), default="NOT_CONNECTED", index=True)
    permissions_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    last_tested_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class ConnectorEvent(Base):
    __tablename__ = "connector_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    connector_key: Mapped[str] = mapped_column(String(80), index=True)
    event: Mapped[str] = mapped_column(String(50), index=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
