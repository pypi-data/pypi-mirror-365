from typing import Dict, Any
from ..base import BaseAPIClient
from ..models.responses import APIResponse, HealthResponse
from ..exceptions import APIException


class HealthEndpoint:
    def __init__(self, client: BaseAPIClient):
        self.client = client
    
    def check(self) -> HealthResponse:
        response = self.client.get('/health', timeout=10)
        
        if response.success and response.data:
            return HealthResponse(**response.data)
        elif response.success:
            return HealthResponse(status="ok")
        else:
            raise APIException(response.error or "Health check failed")
    
    def get_status(self) -> Dict[str, Any]:
        response = self.client.get('/status', timeout=10)
        
        if response.success:
            return response.data or {}
        else:
            raise APIException(response.error or "Failed to get status")
    
    def get_version(self) -> Dict[str, Any]:
        response = self.client.get('/version', timeout=10)
        
        if response.success:
            return response.data or {}
        else:
            raise APIException(response.error or "Failed to get version")