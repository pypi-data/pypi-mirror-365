from typing import Any, Dict, List, Optional

from ..base import BaseAPIClient
from ..exceptions import APIException
from ..models.requests import AgentCreateRequest, AgentUpdateRequest
from ..models.responses import AgentResponse, APIResponse


class AgentsEndpoint:
    def __init__(self, client: BaseAPIClient):
        self.client = client

    def create(self, request: AgentCreateRequest) -> AgentResponse:
        data = request.dict(exclude_none=True)

        response = self.client.post("/agents", data=data)

        if response.success and response.data:
            return AgentResponse(**response.data)
        else:
            raise APIException(response.error or "Failed to create agent")

    def get(self, agent_id: str) -> AgentResponse:
        response = self.client.get(f"/agents/{agent_id}")

        if response.success and response.data:
            return AgentResponse(**response.data)
        else:
            raise APIException(response.error or f"Failed to get agent {agent_id}")

    def update(self, agent_id: str, request: AgentUpdateRequest) -> AgentResponse:
        data = request.dict(exclude_none=True)

        response = self.client.put(f"/agents/{agent_id}", data=data)

        if response.success and response.data:
            return AgentResponse(**response.data)
        else:
            raise APIException(response.error or f"Failed to update agent {agent_id}")

    def delete(self, agent_id: str) -> bool:
        response = self.client.delete(f"/agents/{agent_id}")

        if response.success:
            return True
        else:
            raise APIException(response.error or f"Failed to delete agent {agent_id}")

    def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[AgentResponse]:
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if name:
            params["name"] = name
        if status:
            params["status"] = status

        response = self.client.get("/agents", params=params)

        if response.success and response.data:
            agents_data = response.data.get("agents", [])
            return [AgentResponse(**agent) for agent in agents_data]
        else:
            raise APIException(response.error or "Failed to list agents")

    def get_logs(
        self, agent_id: str, limit: Optional[int] = None, since: Optional[str] = None
    ) -> Dict[str, Any]:
        params = {}
        if limit is not None:
            params["limit"] = limit
        if since:
            params["since"] = since

        response = self.client.get(f"/agents/{agent_id}/logs", params=params)

        if response.success:
            return response.data or {}
        else:
            raise APIException(
                response.error or f"Failed to get logs for agent {agent_id}"
            )

    def get_metrics(self, agent_id: str) -> Dict[str, Any]:
        response = self.client.get(f"/agents/{agent_id}/metrics")

        if response.success:
            return response.data or {}
        else:
            raise APIException(
                response.error or f"Failed to get metrics for agent {agent_id}"
            )
