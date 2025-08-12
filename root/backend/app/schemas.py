from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


# Auth schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    id: uuid.UUID
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Upload schemas
class UploadInitRequest(BaseModel):
    filename: str
    file_size: int
    
    @validator('file_size')
    def validate_file_size(cls, v):
        max_size = 500 * 1024 * 1024  # 500MB
        if v > max_size:
            raise ValueError(f'File size must not exceed 500MB')
        return v
    
    @validator('filename')
    def validate_filename(cls, v):
        allowed_extensions = ['.csv', '.json', '.ndjson']
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(f'File must be CSV, JSON, or NDJSON')
        return v


class PresignedUrlPart(BaseModel):
    part_number: int
    upload_url: str


class UploadInitResponse(BaseModel):
    upload_id: uuid.UUID
    upload_urls: List[PresignedUrlPart]
    s3_key: str


class UploadPartComplete(BaseModel):
    part_number: int
    etag: str


class UploadCompleteRequest(BaseModel):
    upload_id: uuid.UUID
    parts: List[UploadPartComplete]


class UploadStatus(BaseModel):
    upload_id: uuid.UUID
    filename: str
    status: str
    file_size_bytes: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Pipeline schemas
class PipelineConfig(BaseModel):
    synthetic_multiplier: int = 2
    include_nulls: bool = True
    
    @validator('synthetic_multiplier')
    def validate_multiplier(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Synthetic multiplier must be between 1 and 10')
        return v


class PipelineCreateRequest(BaseModel):
    upload_id: uuid.UUID
    config: Optional[PipelineConfig] = None


class PipelineEvent(BaseModel):
    stage: str
    status: str
    message: Optional[str]
    data: Optional[Dict[str, Any]]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class PipelineStatus(BaseModel):
    pipeline_id: uuid.UUID
    upload_id: uuid.UUID
    status: str
    config: Optional[Dict[str, Any]]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PipelineDetails(PipelineStatus):
    events: List[PipelineEvent]
    upload_filename: Optional[str] = None
