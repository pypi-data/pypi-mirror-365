from typing import List, Optional, Dict, Any
from ..base import BaseAPIClient
from ..models.requests import DeploymentCreateRequest
from ..models.responses import APIResponse, DeploymentResponse
from ..exceptions import APIException


class DeploymentsEndpoint:
    def __init__(self, client: BaseAPIClient):
        self.client = client
    
    def create(self, request: DeploymentCreateRequest) -> DeploymentResponse:
        data = request.dict(exclude_none=True)
        
        response = self.client.post('/deployments', data=data)
        
        if response.success and response.data:
            return DeploymentResponse(**response.data)
        else:
            raise APIException(response.error or "Failed to create deployment")
    
    def get(self, deployment_id: str) -> DeploymentResponse:
        response = self.client.get(f'/deployments/{deployment_id}')
        
        if response.success and response.data:
            return DeploymentResponse(**response.data)
        else:
            raise APIException(response.error or f"Failed to get deployment {deployment_id}")
    
    def delete(self, deployment_id: str) -> bool:
        response = self.client.delete(f'/deployments/{deployment_id}')
        
        if response.success:
            return True
        else:
            raise APIException(response.error or f"Failed to delete deployment {deployment_id}")
    
    def list(
        self, 
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        agent_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[DeploymentResponse]:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        if agent_id:
            params['agent_id'] = agent_id
        if status:
            params['status'] = status
        
        response = self.client.get('/deployments', params=params)
        
        if response.success and response.data:
            deployments_data = response.data.get('deployments', [])
            return [DeploymentResponse(**deployment) for deployment in deployments_data]
        else:
            raise APIException(response.error or "Failed to list deployments")
    
    def start(self, deployment_id: str) -> DeploymentResponse:
        response = self.client.post(f'/deployments/{deployment_id}/start')
        
        if response.success and response.data:
            return DeploymentResponse(**response.data)
        else:
            raise APIException(response.error or f"Failed to start deployment {deployment_id}")
    
    def stop(self, deployment_id: str) -> DeploymentResponse:
        response = self.client.post(f'/deployments/{deployment_id}/stop')
        
        if response.success and response.data:
            return DeploymentResponse(**response.data)
        else:
            raise APIException(response.error or f"Failed to stop deployment {deployment_id}")
    
    def restart(self, deployment_id: str) -> DeploymentResponse:
        response = self.client.post(f'/deployments/{deployment_id}/restart')
        
        if response.success and response.data:
            return DeploymentResponse(**response.data)
        else:
            raise APIException(response.error or f"Failed to restart deployment {deployment_id}")
    
    def scale(self, deployment_id: str, replicas: int) -> DeploymentResponse:
        data = {'replicas': replicas}
        
        response = self.client.post(f'/deployments/{deployment_id}/scale', data=data)
        
        if response.success and response.data:
            return DeploymentResponse(**response.data)
        else:
            raise APIException(response.error or f"Failed to scale deployment {deployment_id}")
    
    def get_logs(
        self, 
        deployment_id: str, 
        limit: Optional[int] = None,
        since: Optional[str] = None,
        follow: bool = False
    ) -> Dict[str, Any]:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if since:
            params['since'] = since
        if follow:
            params['follow'] = 'true'
        
        response = self.client.get(f'/deployments/{deployment_id}/logs', params=params)
        
        if response.success:
            return response.data or {}
        else:
            raise APIException(response.error or f"Failed to get logs for deployment {deployment_id}")
    
    def get_metrics(self, deployment_id: str) -> Dict[str, Any]:
        response = self.client.get(f'/deployments/{deployment_id}/metrics')
        
        if response.success:
            return response.data or {}
        else:
            raise APIException(response.error or f"Failed to get metrics for deployment {deployment_id}")