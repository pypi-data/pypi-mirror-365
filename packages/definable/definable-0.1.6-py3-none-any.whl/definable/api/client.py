from typing import Optional, Dict, Any
from .base import BaseAPIClient
from .endpoints.uploads import UploadsEndpoint
from .endpoints.health import HealthEndpoint
from .endpoints.agents import AgentsEndpoint
from .endpoints.deployments import DeploymentsEndpoint
from .models.requests import UploadRequest
from .models.responses import UploadResponse, HealthResponse
from .exceptions import APIException


class APIClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        self._base_client = BaseAPIClient(base_url, api_key, timeout)
        
        self.uploads = UploadsEndpoint(self._base_client)
        self.health = HealthEndpoint(self._base_client)
        self.agents = AgentsEndpoint(self._base_client)
        self.deployments = DeploymentsEndpoint(self._base_client)
    
    def upload_package(
        self, 
        package_path: str, 
        agent_name: Optional[str] = None,
        **kwargs
    ) -> UploadResponse:
        request = UploadRequest(agent_name=agent_name)
        
        for key, value in kwargs.items():
            if hasattr(request, key):
                setattr(request, key, value)
        
        return self.uploads.upload_package(package_path, request, **kwargs)
    
    def check_connection(self) -> Dict[str, Any]:
        try:
            health_response = self.health.check()
            return {
                'success': True,
                'message': 'Connection successful',
                'data': health_response.dict()
            }
        except APIException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e, 'status_code', None)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }