import httpx
from typing import List, Optional
from .exceptions import (
    FilesystemError,
    FileNotFoundError,
    FileAlreadyExistsError,
    VersionConflictError,
    AuthenticationError,
)
from .models import FileData
    
class FilesystemClient:    
    def __init__(self, api_url: str, auth_token: str):
        self.api_url = api_url.rstrip('/')
        self.auth_token = auth_token
        self.headers = {"Authorization": f"Bearer {auth_token}"}
    
    def list_files(self, path: Optional[str] = None) -> List[FileData]:
        params = {"path": path} if path else {}
        response = httpx.get(
            f"{self.api_url}/v1/files",
            headers=self.headers,
            params=params
        )
        self._handle_response(response)
        return [FileData(**f) for f in response.json()["files"]]
    
    def read_file(self, path: str) -> FileData:
        # Remove leading slash for API call
        clean_path = path.lstrip('/')
        response = httpx.get(
            f"{self.api_url}/v1/files/{clean_path}",
            headers=self.headers
        )
        self._handle_response(response)
        return FileData(**response.json())
    
    def create_file(self, path: str, content: str) -> FileData:
        response = httpx.post(
            f"{self.api_url}/v1/files",
            headers=self.headers,
            json={"path": path, "content": content}
        )
        self._handle_response(response)
        return FileData(**response.json())
    
    def update_file(self, path: str, content: str, version: int) -> FileData:
        clean_path = path.lstrip('/')
        response = httpx.put(
            f"{self.api_url}/v1/files/{clean_path}",
            headers=self.headers,
            json={"content": content, "version": version}
        )
        self._handle_response(response)
        return FileData(**response.json())
    
    def append_to_file(self, path: str, content: str) -> FileData:
        clean_path = path.lstrip('/')
        response = httpx.post(
            f"{self.api_url}/v1/files/{clean_path}/append",
            headers=self.headers,
            json={"content": content}
        )
        self._handle_response(response)
        return FileData(**response.json())
    
    def _handle_response(self, response: httpx.Response):
        if response.status_code == 200 or response.status_code == 201:
            return
        
        if response.status_code == 401:
            raise AuthenticationError("Invalid or expired token")
        elif response.status_code == 404:
            raise FileNotFoundError("File not found")
        elif response.status_code == 409:
            error_detail = response.json().get("detail", "")
            if "already exists" in error_detail:
                raise FileAlreadyExistsError(error_detail)
            else:
                raise VersionConflictError(error_detail)
        else:
            try:
                error_data = response.json() if response.text else {}
            except Exception:
                error_data = {}
            raise FilesystemError(
                error_data.get("detail", f"API error: {response.status_code}")
            )