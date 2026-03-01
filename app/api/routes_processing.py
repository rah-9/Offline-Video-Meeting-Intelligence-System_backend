from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.dependencies import get_db_session
from app.db.crud import create_job, get_job, get_result
from app.utils.file_manager import save_upload_file
from app.models.response_models import JobResponse, JobStatusResponse, ProcessResultResponse
from app.services.pipeline_service import run_pipeline_sync

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=2) # 2 workers max for GPU safety/memory

@router.post("/process", response_model=JobResponse)
async def process_media(
    request: Request,
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db_session)
):
    if not url and not file:
        raise HTTPException(status_code=400, detail="Must provide either URL or file")
        
    job = await create_job(db)
    
    if url:
        is_url = True
        source = url
        await db.refresh(job) # ensure we have job
        
        # Submit to threadpool
        loop = asyncio.get_event_loop()
        loop.run_in_executor(executor, run_pipeline_sync, request, job.id, source, is_url)
    else:
        is_url = False
        source = await save_upload_file(file, job.id)
        
        loop = asyncio.get_event_loop()
        loop.run_in_executor(executor, run_pipeline_sync, request, job.id, source, is_url)
        
    return JobResponse(job_id=job.id, status="queued", message="Processing started")

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str, db: AsyncSession = Depends(get_db_session)):
    job = await get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        error_message=job.error_message
    )

@router.get("/result/{job_id}", response_model=ProcessResultResponse)
async def get_process_result(job_id: str, db: AsyncSession = Depends(get_db_session)):
    job = await get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job.status != "completed":
        raise HTTPException(status_code=400, detail=f"Job not completed. Current status: {job.status}")
        
    result = await get_result(db, job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
        
    import json
    
    actions_decisions = json.loads(result.action_items_json) if result.action_items_json else []
    actions = [d for d in actions_decisions if d.get("type", "action") == "action"]
    decisions = [d.get("text", "") for d in actions_decisions if d.get("type") == "decision"]
    
    return ProcessResultResponse(
        job_id=job.id,
        summary_short=result.summary_short,
        summary_detailed=result.summary_detailed,
        topics=json.loads(result.topics_json) if result.topics_json else [],
        action_items=actions,
        decisions=decisions,
        qa_pairs=json.loads(result.qa_json) if result.qa_json else []
    )
