"""J-ROC Cloud control-plane API (Stage 31)."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.cloud.core import CloudResource, ResourceType, ResourceStatus, registry

router=APIRouter()

class ResourceRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    resource_type: ResourceType
    owner_id: str = Field(min_length=1, max_length=120)
    provider: str = "jroc"
    region: str = "default"
    metadata: dict = Field(default_factory=dict)

@router.get("/status")
def cloud_status():
    resources=registry.list()
    return {"cloud":"J-ROC Cloud","stage":31,"status":"ONLINE","resource_count":len(resources),"resource_types":[t.value for t in ResourceType],"governance":{"chairman_authority":True,"audit_required":True,"provider_neutral":True}}

@router.post("/resources")
def create_resource(request: ResourceRequest):
    resource=registry.register(CloudResource(**request.model_dump()))
    resource.status=ResourceStatus.ACTIVE
    return resource

@router.get("/resources")
def list_resources(resource_type: ResourceType | None = None):
    return {"resources":registry.list(resource_type)}

@router.get("/resources/{resource_id}")
def get_resource(resource_id: str):
    resource=registry.get(resource_id)
    if not resource: raise HTTPException(status_code=404, detail="cloud_resource_not_found")
    return resource

@router.post("/resources/{resource_id}/status/{status}")
def set_resource_status(resource_id: str, status: ResourceStatus):
    if not registry.get(resource_id): raise HTTPException(status_code=404, detail="cloud_resource_not_found")
    return registry.set_status(resource_id,status)
