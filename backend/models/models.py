from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON, Boolean
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="OPERATOR") # ADMIN, OPERATOR, AUDITOR
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    sources = relationship("Source", back_populates="project", cascade="all, delete-orphan")

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    type = Column(String) # txt, pdf, docx, image, video, url, demo
    filename = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    source_hash = Column(String, nullable=True) # SHA-256 of raw source
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="sources")
    facts = relationship("Fact", back_populates="source", cascade="all, delete-orphan")
    transformations = relationship("Transformation", back_populates="source", cascade="all, delete-orphan")

class Fact(Base):
    __tablename__ = "facts"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    fact_id = Column(String, index=True) # F001, F002...
    claim = Column(Text)
    fact_type = Column(String, default="CLAIM") # DATE, NUMBER, PERCENTAGE, ENTITY, LOCATION, EVENT, STATISTIC, CLAIM
    confidence = Column(Float, default=1.0)
    source_reference = Column(String, default="")
    entities = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    source = relationship("Source", back_populates="facts")

class Transformation(Base):
    __tablename__ = "transformations"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    configuration = Column(JSON)
    status = Column(String, default="QUEUED")
    stage = Column(String, default="QUEUED")
    progress_percent = Column(Integer, default=0)
    fact_registry_hash = Column(String, nullable=True) # SHA-256 of canonical facts JSON
    semantic_model_hash = Column(String, nullable=True) # SHA-256 of semantic representation
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    source = relationship("Source", back_populates="transformations")
    outputs = relationship("Output", back_populates="transformation", cascade="all, delete-orphan")

class Output(Base):
    __tablename__ = "outputs"
    id = Column(Integer, primary_key=True, index=True)
    transformation_id = Column(Integer, ForeignKey("transformations.id"))
    type = Column(String) # linkedin, x, advisory, summary, infographic, presentation, video
    content = Column(Text)
    status = Column(String, default="DRAFT") # DRAFT, UNDER_REVIEW, APPROVED, REJECTED
    quality_status = Column(String, default="READY FOR HUMAN REVIEW")
    quality_report = Column(JSON, nullable=True)
    fact_consistency_report = Column(JSON, nullable=True)
    provenance_id = Column(String, index=True, nullable=True) # e.g. NTRO-26154-OUT-20261001-A1B2C3
    artifact_hash = Column(String, nullable=True) # SHA-256 of output content bytes
    current_version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    transformation = relationship("Transformation", back_populates="outputs")
    versions = relationship("OutputVersion", back_populates="output", cascade="all, delete-orphan")
    provenance_records = relationship("ProvenanceRecord", back_populates="output", cascade="all, delete-orphan")

class OutputVersion(Base):
    __tablename__ = "output_versions"
    id = Column(Integer, primary_key=True, index=True)
    output_id = Column(Integer, ForeignKey("outputs.id"))
    version = Column(Integer)
    content = Column(Text)
    artifact_hash = Column(String, nullable=True)
    change_description = Column(String, default="AI Generated")
    created_by = Column(String, default="AI Engine")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    output = relationship("Output", back_populates="versions")

class ProvenanceRecord(Base):
    __tablename__ = "provenance_records"
    id = Column(Integer, primary_key=True, index=True)
    provenance_id = Column(String, unique=True, index=True) # NTRO-26154-OUT-...
    transformation_id = Column(Integer, ForeignKey("transformations.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    output_id = Column(Integer, ForeignKey("outputs.id"))
    output_version = Column(Integer, default=1)
    
    # Cryptographic Hashes
    source_hash = Column(String, nullable=False)
    fact_registry_hash = Column(String, nullable=False)
    semantic_model_hash = Column(String, nullable=False)
    artifact_hash = Column(String, nullable=False, index=True)
    hash_algorithm = Column(String, default="SHA-256")
    
    # Metadata & Signing
    output_type = Column(String)
    model_provider = Column(String, default="Google / NTRO AI Hub")
    model_name = Column(String, default="gemini-2.5-flash")
    signature_algorithm = Column(String, default="Ed25519")
    signature = Column(Text, nullable=False)
    public_key_hex = Column(Text, nullable=False)
    
    # Manifest & Approval
    manifest_json = Column(JSON, nullable=False)
    approval_status = Column(String, default="DRAFT")
    verification_status = Column(String, default="AUTHENTIC")
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

    output = relationship("Output", back_populates="provenance_records")
