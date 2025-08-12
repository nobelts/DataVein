from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
from datetime import datetime, timedelta


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    uploads = relationship("Upload", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    pipelines = relationship("Pipeline", back_populates="user")


class Upload(Base):
    __tablename__ = "uploads"
    
    upload_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=True)
    status = Column(String(50), nullable=False, default="INITIATED")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="uploads")
    file_parts = relationship("FilePart", back_populates="upload")
    pipelines = relationship("Pipeline", back_populates="upload")


class FilePart(Base):
    __tablename__ = "file_parts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    upload_id = Column(UUID(as_uuid=True), ForeignKey("uploads.upload_id"), nullable=False)
    part_number = Column(Integer, nullable=False)
    etag = Column(String(255), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    upload = relationship("Upload", back_populates="file_parts")


class Pipeline(Base):
    __tablename__ = "pipelines"
    
    pipeline_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    upload_id = Column(UUID(as_uuid=True), ForeignKey("uploads.upload_id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(String(50), nullable=False, default="QUEUED")  # QUEUED, RUNNING, COMPLETED, FAILED
    config = Column(JSON, nullable=True)  # Pipeline configuration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="pipelines")
    upload = relationship("Upload", back_populates="pipelines")
    events = relationship("PipelineEvent", back_populates="pipeline")


class PipelineEvent(Base):
    __tablename__ = "pipeline_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipelines.pipeline_id"), nullable=False)
    stage = Column(String(50), nullable=False)  # VALIDATE, PROFILE, AUGMENT, PARQUETIZE, FINALIZE
    status = Column(String(50), nullable=False)  # STARTED, COMPLETED, FAILED
    message = Column(Text, nullable=True)  # Progress message or error details
    data = Column(JSON, nullable=True)  # Stage output data
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    pipeline = relationship("Pipeline", back_populates="events")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
