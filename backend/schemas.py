from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ResearchRequest(BaseModel):
    topic: str
    target_word_count: int = Field(default=2500, ge=500, le=10000)
    self_correction_rounds: int = Field(default=1, ge=0, le=3)
    search_provider: str = "tavily"
    workspace: str = "default"

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    topic: str
    tasks: Dict[str, Any]
    logs: List[str]
    final_report: Optional[str] = None
    critique: Optional[Any] = None
    summary: Optional[str] = None
    duration: float = 0.0

class MemoryItemResponse(BaseModel):
    id: str
    topic: str
    summary: str
    critique: Any
    full_research: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

class PdfChatRequest(BaseModel):
    query: str
    filename: Optional[str] = None
    top_k: int = 4

class PdfChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]] = []

class ExportPdfRequest(BaseModel):
    title: str
    markdown_content: str

class ExportLatexRequest(BaseModel):
    title: str
    markdown_content: str
    sources: Optional[List[Dict[str, Any]]] = None

class ExportBibtexRequest(BaseModel):
    title: str
    sources: Optional[List[Dict[str, Any]]] = None
    markdown_content: Optional[str] = None

class SettingsUpdateRequest(BaseModel):
    groq_api_key: Optional[str] = None
    groq_api_key_2: Optional[str] = None
    groq_api_key_3: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_api_key_2: Optional[str] = None
    gemini_api_key_3: Optional[str] = None
    openai_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    xai_api_key: Optional[str] = None
    nvidia_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    active_workspace: Optional[str] = None
