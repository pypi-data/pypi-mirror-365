import json
from pathlib import Path
from typing import Any, Dict, Optional

from ..base import BaseAPIClient
from ..exceptions import APIException
from ..models.requests import UploadRequest
from ..models.responses import UploadResponse


class UploadsEndpoint:
    def __init__(self, client: BaseAPIClient):
        self.client = client

    def upload_package(
        self, package_path: str, request: Optional[UploadRequest] = None, **kwargs
    ) -> UploadResponse:
        package_file = Path(package_path)

        if not package_file.exists():
            raise APIException(f"Package file not found: {package_path}")

        request = request or UploadRequest()

        # Prepare files with 'file' field name to match API requirements
        files = {
            "file": (
                package_file.name,
                open(package_file, "rb"),
                "application/zip",
            )
        }

        # Build metadata object containing all upload parameters
        metadata = {}
        if request.agent_name:
            metadata["agent_name"] = request.agent_name
        if request.version:
            metadata["version"] = request.version
        if request.description:
            metadata["description"] = request.description
        if request.environment:
            metadata["environment"] = request.environment
        if request.tags:
            metadata["tags"] = request.tags

        # Add any additional kwargs to metadata
        for key, value in kwargs.items():
            if value is not None:
                metadata[key] = value

        # Create form data with metadata as JSON string
        data = {
            "metadata": json.dumps(metadata)
        }

        try:
            response = self.client.post("/upload", data=data, files=files, timeout=300)

            files["file"][1].close()

            if response.success and response.data:
                return UploadResponse(**response.data)
            else:
                raise APIException(response.error or "Upload failed")

        except Exception as e:
            try:
                files["file"][1].close()
            except Exception:
                pass
            raise e

    def get_upload_status(self, upload_id: str) -> Dict[str, Any]:
        response = self.client.get(f"/upload/{upload_id}/status")

        if response.success:
            return response.data or {}
        else:
            raise APIException(response.error or "Failed to get upload status")

    def list_uploads(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        agent_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if agent_name:
            params["agent_name"] = agent_name

        response = self.client.get("/uploads", params=params)

        if response.success:
            return response.data or {}
        else:
            raise APIException(response.error or "Failed to list uploads")
