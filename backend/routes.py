import os
import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form, Query, Response
from fastapi.responses import StreamingResponse, FileResponse
from typing import Optional, List

from backend.schemas import (
    ResearchRequest,
    TaskStatusResponse,
    MemoryItemResponse,
    PdfChatRequest,
    PdfChatResponse,
    ExportPdfRequest,
    ExportLatexRequest,
    ExportBibtexRequest,
    SettingsUpdateRequest
)
from backend.services.research_service import research_service
from backend.services.memory_service import memory_service
from backend.services.pdf_service import pdf_service
from tools.pdf_generator import convert_markdown_to_pdf_bytes
from tools.latex_generator import convert_markdown_to_latex, generate_bibtex

router = APIRouter()

# -------------------------------------------------------------------
# RESEARCH ENDPOINTS
# -------------------------------------------------------------------

@router.post("/research/start")
async def start_research(req: ResearchRequest, background_tasks: BackgroundTasks):
    if not req.topic or not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    task = research_service.create_task(
        topic=req.topic.strip(),
        workspace=req.workspace,
        self_correction_rounds=req.self_correction_rounds
    )
    background_tasks.add_task(research_service.run_task, task.task_id)

    return {
        "task_id": task.task_id,
        "status": task.status,
        "topic": task.topic,
        "created_at": task.created_at
    }

@router.get("/research/stream/{task_id}")
async def stream_research(task_id: str):
    task = research_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return StreamingResponse(
        research_service.stream_task_events(task_id),
        media_type="text/event-stream"
    )

@router.get("/research/status/{task_id}", response_model=TaskStatusResponse)
async def get_research_status(task_id: str):
    task = research_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    step_status = {}
    if task.orchestrator:
        for t_id, t_obj in task.orchestrator.tasks.items():
            step_status[t_id] = {
                "name": t_obj.name,
                "status": t_obj.status,
                "duration": t_obj.duration,
                "error": t_obj.error
            }

    return TaskStatusResponse(
        task_id=task.task_id,
        status=task.status,
        topic=task.topic,
        tasks=step_status,
        logs=task.logs,
        final_report=task.result.get("final_report"),
        critique=task.result.get("critique"),
        summary=task.result.get("summary"),
        duration=task.duration
    )

# -------------------------------------------------------------------
# MEMORY BANK ENDPOINTS
# -------------------------------------------------------------------

@router.get("/memory", response_model=List[MemoryItemResponse])
def list_memories(query: Optional[str] = Query(None), workspace: str = Query("default")):
    items = memory_service.list_memories(query=query, workspace=workspace)
    return items

@router.get("/memory/{doc_id}", response_model=MemoryItemResponse)
def get_memory(doc_id: str, workspace: str = Query("default")):
    item = memory_service.get_memory(doc_id=doc_id, workspace=workspace)
    if not item:
        raise HTTPException(status_code=404, detail="Memory item not found")
    return item

@router.delete("/memory/{doc_id}")
def delete_memory(doc_id: str, workspace: str = Query("default")):
    success = memory_service.delete_memory(doc_id=doc_id, workspace=workspace)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete memory")
    return {"success": True, "message": f"Memory {doc_id} deleted"}

@router.get("/workspaces")
def get_workspaces():
    return {"workspaces": memory_service.get_workspaces()}

# -------------------------------------------------------------------
# PDF CHAT ENDPOINTS
# -------------------------------------------------------------------

@router.post("/pdf/upload")
async def upload_pdf(file: UploadFile = File(...), workspace: str = Form("default")):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    contents = await file.read()
    record = pdf_service.upload_and_ingest(file_bytes=contents, filename=file.filename, workspace=workspace)
    return record

@router.get("/pdf/files")
def list_pdfs(workspace: str = Query("default")):
    return pdf_service.list_pdfs(workspace=workspace)

@router.post("/pdf/chat", response_model=PdfChatResponse)
def chat_pdf(req: PdfChatRequest, workspace: str = Query("default")):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    res = pdf_service.chat_with_pdf(query=req.query, filename=req.filename, top_k=req.top_k, workspace=workspace)
    return res

# -------------------------------------------------------------------
# EXPORT ENDPOINTS
# -------------------------------------------------------------------

@router.post("/export/pdf")
async def export_pdf(req: ExportPdfRequest):
    if not req.markdown_content:
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    pdf_bytes = convert_markdown_to_pdf_bytes(req.markdown_content, title=req.title)
    filename = f"{req.title.lower().replace(' ', '_')[:30]}_report.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/export/latex")
async def export_latex(req: ExportLatexRequest):
    if not req.markdown_content:
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    latex_code = convert_markdown_to_latex(req.markdown_content, title=req.title)
    filename = f"{req.title.lower().replace(' ', '_')[:30]}_report.tex"

    return Response(
        content=latex_code.encode("utf-8"),
        media_type="application/x-tex",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/export/bibtex")
async def export_bibtex(req: ExportBibtexRequest):
    bibtex_code = generate_bibtex(sources=req.sources, markdown_content=req.markdown_content or "", title=req.title)
    filename = f"{req.title.lower().replace(' ', '_')[:30]}_references.bib"

    return Response(
        content=bibtex_code.encode("utf-8"),
        media_type="application/x-bibtex",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# -------------------------------------------------------------------
# SETTINGS ENDPOINTS
# -------------------------------------------------------------------

@router.get("/settings")
async def get_settings():
    # Count how many keys each provider has configured
    def _count_keys(prefix: str) -> int:
        count = 0
        primary = os.getenv(prefix, "")
        if primary and not primary.startswith("YOUR_"):
            count += 1
        for i in range(2, 10):
            extra = os.getenv(f"{prefix}_{i}", "")
            if extra and not extra.startswith("YOUR_"):
                count += 1
        return count
    
    return {
        "api_keys": {
            "groq": bool(os.getenv("GROQ_API_KEY")),
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "tavily": bool(os.getenv("TAVILY_API_KEY")),
            "serper": bool(os.getenv("SERPER_API_KEY")),
            "xai": bool(os.getenv("XAI_API_KEY")),
            "nvidia": bool(os.getenv("NVIDIA_API_KEY")),
            "deepseek": bool(os.getenv("DEEPSEEK_API_KEY"))
        },
        "key_counts": {
            "groq": _count_keys("GROQ_API_KEY"),
            "gemini": _count_keys("GEMINI_API_KEY"),
        },
        "available_workspaces": memory_service.get_workspaces()
    }

from tools.groq_client import _invalidate_key_cache

def _write_key_to_env(key_name: str, value: str):
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    lines = []
    found = False
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{key_name}="):
            new_lines.append(f"{key_name}={value}\n")
            found = True
        else:
            new_lines.append(line)
            
    if not found:
        new_lines.append(f"{key_name}={value}\n")
        
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

# Map of schema field names to environment variable names
_KEY_FIELD_MAP = {
    "groq_api_key": "GROQ_API_KEY",
    "groq_api_key_2": "GROQ_API_KEY_2",
    "groq_api_key_3": "GROQ_API_KEY_3",
    "gemini_api_key": "GEMINI_API_KEY",
    "gemini_api_key_2": "GEMINI_API_KEY_2",
    "gemini_api_key_3": "GEMINI_API_KEY_3",
    "openai_api_key": "OPENAI_API_KEY",
    "tavily_api_key": "TAVILY_API_KEY",
    "serper_api_key": "SERPER_API_KEY",
    "xai_api_key": "XAI_API_KEY",
    "nvidia_api_key": "NVIDIA_API_KEY",
    "deepseek_api_key": "DEEPSEEK_API_KEY",
}

@router.post("/settings")
async def update_settings(req: SettingsUpdateRequest):
    req_dict = req.model_dump(exclude_none=True)
    req_dict.pop("active_workspace", None)
    
    updated_count = 0
    for field_name, env_var in _KEY_FIELD_MAP.items():
        value = req_dict.get(field_name)
        if value and value.strip():
            os.environ[env_var] = value.strip()
            _write_key_to_env(env_var, value.strip())
            updated_count += 1

    _invalidate_key_cache()
    return {"success": True, "message": f"Settings updated successfully ({updated_count} keys saved)"}
