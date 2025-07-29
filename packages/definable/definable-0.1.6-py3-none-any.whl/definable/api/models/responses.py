from typing import Optional, Dict, Any, Union
from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    message: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: Optional[str] = None
    timestamp: Optional[str] = None
    uptime: Optional[float] = None


class UploadResponse(BaseModel):
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    version: Optional[str] = None
    deployment_url: Optional[str] = None
    package_size: Optional[int] = None
    upload_time: Optional[str] = None


class AgentResponse(BaseModel):
    id: str
    name: str
    status: str
    version: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deployment_url: Optional[str] = None


class DeploymentResponse(BaseModel):
    id: str
    agent_id: str
    status: str
    version: Optional[str] = None
    url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    logs_url: Optional[str] = None