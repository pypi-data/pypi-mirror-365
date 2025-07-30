from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class FileResponse(BaseModel):
    path: str
    content: Optional[str] = None
    version: int = 1
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_record(cls, record):
        """Create FileResponse from database record"""
        return cls(
            path=record["path"],
            content=record.get("content"),
            version=record["version"],
            created_at=record["created_at"],
            updated_at=record["updated_at"]
        )


class FileListResponse(BaseModel):
    files: list[FileResponse]


class CreateFileRequest(BaseModel):
    path: str = Field(..., description="File path starting with /")
    content: str
    
    @validator("path")
    def validate_path(cls, v):
        if not v.startswith("/"):
            raise ValueError("Path must start with /")
        if ".." in v:
            raise ValueError("Path cannot contain ..")
        return v


class UpdateFileRequest(BaseModel):
    content: str
    version: int = Field(..., description="Current version for optimistic locking")


class MoveFileRequest(BaseModel):
    new_path: str = Field(..., description="New file path starting with /")
    
    @validator("new_path")
    def validate_path(cls, v):
        if not v.startswith("/"):
            raise ValueError("Path must start with /")
        if ".." in v:
            raise ValueError("Path cannot contain ..")
        return v


class AppendFileRequest(BaseModel):
    content: str = Field(..., description="Content to append to the file")


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict = {}