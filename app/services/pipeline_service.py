from fastapi import Request
from app.db.crud import update_job_status, save_result
from app.db.database import AsyncSessionLocal
from app.utils.logger import logger
from app.pipeline.downloader import download_video_sync
from app.pipeline.audio_extractor import extract_audio_sync
from app.pipeline.transcriber import transcribe_audio_sync
from app.pipeline.cleaner import clean_transcript_sync
from app.pipeline.chunker import chunk_transcript_sync
from app.services.embedding_service import create_embeddings_sync
from app.services.topic_service import extract_topics_sync
from app.services.summarization_service import generate_hierarchical_summary_sync
from app.services.action_service import extract_actions_and_decisions_sync
import traceback
import asyncio

def run_pipeline_sync(request: Request, job_id: str, source: str, is_url: bool):
    """
    Runs the full ML pipeline synchronously, intended to be executed in a ThreadPoolExecutor.
    """
    logger.info(f"Starting pipeline for job {job_id}")
    
    async def update_status_async(status, progress):
        async with AsyncSessionLocal() as db:
            await update_job_status(db, job_id, status, progress)

    def sync_update_status(s, p):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        # Avoid running if loop is already running inside thread (rare in this case but safe)
        if loop.is_running():
            asyncio.create_task(update_status_async(s, p))
        else:
            loop.run_until_complete(update_status_async(s, p))

    try:
        # 1. Download / File prep
        if is_url:
            sync_update_status("downloading", 10.0)
            file_path = download_video_sync(source, job_id)
        else:
            file_path = source
            
        # 2. Extract Audio
        sync_update_status("transcribing", 20.0)
        audio_path = extract_audio_sync(file_path, job_id)
        
        # 3. Transcribe
        sync_update_status("transcribing", 30.0)
        transcript_data = transcribe_audio_sync(request, audio_path, job_id)
        
        # 4. Clean
        sync_update_status("summarizing", 50.0)
        cleaned_data = clean_transcript_sync(request, transcript_data, job_id)
        
        # 5. Chunk
        sync_update_status("summarizing", 60.0)
        chunks = chunk_transcript_sync(cleaned_data, job_id)
        
        # 6. Embeddings
        sync_update_status("summarizing", 70.0)
        create_embeddings_sync(request, chunks, job_id)
        
        # 7. Topic Clustering
        sync_update_status("summarizing", 80.0)
        topics = extract_topics_sync(request, chunks, job_id)
        
        # 8. Summarization (Hierarchical)
        sync_update_status("summarizing", 85.0)
        short_summary, detailed_summary = generate_hierarchical_summary_sync(request, chunks, job_id)
        
        # 9. Action Items & Decisions
        sync_update_status("summarizing", 90.0)
        action_items, decisions = extract_actions_and_decisions_sync(request, chunks, job_id)
        
        # Formulate QA pairs (optional)
        qa_pairs = [{"question": "What is the short summary?", "answer": short_summary}]
        
        # Combine actions and decisions for db storage
        final_actions_and_decisions = [{"type": "action", **a} for a in action_items] + [{"type": "decision", **d} for d in decisions]
        
        async def save_final_result():
            async with AsyncSessionLocal() as db:
                await save_result(db, job_id, short_summary, detailed_summary, topics, final_actions_and_decisions, qa_pairs)
                await update_job_status(db, job_id, "completed", 100.0)

        loop = asyncio.new_event_loop()
        loop.run_until_complete(save_final_result())
        
        logger.info(f"Pipeline completed successfully for job {job_id}")
        
    except Exception as e:
        logger.error(f"Pipeline failed for job {job_id}: {str(e)}\n{traceback.format_exc()}")
        sync_update_status("failed", 0.0)
        
        async def save_error():
            async with AsyncSessionLocal() as db:
                await update_job_status(db, job_id, "failed", 0.0, str(e))
                
        loop = asyncio.new_event_loop()
        loop.run_until_complete(save_error())
