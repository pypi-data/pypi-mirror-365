import os
import requests
from typing import Optional, Dict, Any, Union
from .exceptions import APIException, APIConnectionError, APIAuthenticationError, APITimeoutError
from .models.responses import APIResponse


class BaseAPIClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv('DEFINABLE_API_KEY')
        self.timeout = timeout
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'User-Agent': 'definable-cli/0.1.5'
            })
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> APIResponse:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_timeout = timeout or self.timeout
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                data=data,
                files=files,
                params=params,
                timeout=request_timeout
            )
            
            return self._handle_response(response)
            
        except requests.exceptions.ConnectionError as e:
            raise APIConnectionError(f"Connection failed: {str(e)}")
        except requests.exceptions.Timeout as e:
            raise APITimeoutError(f"Request timeout: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise APIException(f"Request failed: {str(e)}")
    
    def _handle_response(self, response: requests.Response) -> APIResponse:
        try:
            response_data = response.json() if response.content else {}
        except ValueError:
            response_data = {'message': response.text} if response.text else {}
        
        if response.status_code == 200:
            return APIResponse(
                success=True,
                data=response_data,
                status_code=response.status_code
            )
        elif response.status_code == 401:
            raise APIAuthenticationError("Authentication failed. Check your API key.")
        elif response.status_code == 403:
            raise APIAuthenticationError("Access forbidden. Check your permissions.")
        elif response.status_code == 404:
            raise APIException("Resource not found.", status_code=404)
        elif 400 <= response.status_code < 500:
            error_msg = self._extract_error_message(response_data)
            raise APIException(error_msg, status_code=response.status_code)
        elif response.status_code >= 500:
            error_msg = self._extract_error_message(response_data) or "Server error"
            raise APIException(error_msg, status_code=response.status_code)
        else:
            return APIResponse(
                success=False,
                error=f"Unexpected status code: {response.status_code}",
                status_code=response.status_code,
                data=response_data
            )
    
    def _extract_error_message(self, response_data: Dict[str, Any]) -> str:
        if isinstance(response_data, dict):
            return (
                response_data.get('error') or 
                response_data.get('message') or 
                response_data.get('detail') or
                "Request failed"
            )
        return "Request failed"
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> APIResponse:
        return self._make_request('GET', endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
             files: Optional[Dict[str, Any]] = None, **kwargs) -> APIResponse:
        return self._make_request('POST', endpoint, data=data, files=files, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> APIResponse:
        return self._make_request('PUT', endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> APIResponse:
        return self._make_request('DELETE', endpoint, **kwargs)