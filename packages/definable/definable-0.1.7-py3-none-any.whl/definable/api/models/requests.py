from typing import Optional, Dict, Any
from pydantic import BaseModel


class UploadRequest(BaseModel):
    agent_name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    environment: Optional[str] = None


class AgentCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


class AgentUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


class DeploymentCreateRequest(BaseModel):
    agent_id: str
    version: Optional[str] = None
    environment: Optional[str] = None
    scaling: Optional[Dict[str, Any]] = None