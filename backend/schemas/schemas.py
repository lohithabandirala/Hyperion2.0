from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = ""

class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

class SourceCreateText(BaseModel):
    project_id: int
    title: str
    content: str

class SourceCreateURL(BaseModel):
    project_id: int
    url: str

class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    type: str
    filename: Optional[str]
    content: Optional[str]
    metadata_json: Optional[Dict[str, Any]]
    created_at: datetime

class FactItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    fact_id: str
    claim: str
    fact_type: str = "CLAIM"
    confidence: float = 1.0
    source_reference: str = ""
    entities: List[str] = []

class FactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    source_id: int
    fact_id: str
    claim: str
    fact_type: str
    confidence: float
    source_reference: str
    entities: List[str]
    created_at: datetime

class TransformRequest(BaseModel):
    source_id: int
    audience: str = "Executive" # General Public, Executive, Government, Technical, Media, Internal Team
    tone: str = "Professional" # Professional, Formal, Neutral, Informative, Urgent, Conversational
    language: str = "English" # English, Hindi, Telugu, Tamil, Kannada, Marathi, Bengali, Gujarati
    detail_level: str = "Medium" # Brief, Medium, Detailed
    objective: str = "Inform" # Inform, Alert, Explain, Educate, Summarize, Persuade
    outputs: List[str] # ["linkedin", "x", "advisory", "summary", "infographic", "presentation", "video"]

class TransformationStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    source_id: int
    status: str
    stage: str
    progress_percent: int
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class OutputVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    output_id: int
    version: int
    content: str
    change_description: str
    created_by: str
    created_at: datetime

class OutputEditRequest(BaseModel):
    content: str
    change_description: Optional[str] = "Human Edited"

class OutputRegenerateRequest(BaseModel):
    instruction: Optional[str] = None # e.g. "make shorter", "emphasize timeline", "change tone to urgent"
    target_language: Optional[str] = None
    target_tone: Optional[str] = None

class OutputResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    transformation_id: int
    type: str
    content: str
    status: str
    quality_status: Optional[str]
    quality_report: Optional[Dict[str, Any]]
    fact_consistency_report: Optional[Dict[str, Any]]
    current_version: int
    created_at: datetime
    updated_at: datetime
