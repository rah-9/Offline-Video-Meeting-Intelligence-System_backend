from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db_session
from app.db.crud import get_job
from app.models.request_models import AskRequest
from app.models.response_models import AskResponse
from app.services.embedding_service import search_embeddings_sync
from app.services.summarization_service import answer_question_sync
import asyncio

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask_question(
    request: Request,
    body: AskRequest,
    db: AsyncSession = Depends(get_db_session)
):
    job = await get_job(db, body.job_id)
    if not job or job.status != "completed":
        raise HTTPException(status_code=400, detail="Job not found or not completed.")
        
    # Search embeddings
    results = await search_embeddings_sync(request, body.question, body.job_id, top_k=3)
    
    # Check threshold for hybrid RAG mode
    # FAISS L2 distance for BAAI/bge-small-en-v1.5 typically ranges from 0.0 to 2.0.
    # Scores > 1.1 usually indicate poor semantic matching.
    is_general = False
    if not results or all(r["score"] > 1.1 for r in results):
        is_general = True
        
    # Compile context
    context_text = ""
    if results:
        context_chunks = [r["chunk"]["text"] for r in results]
        context_text = " ".join(context_chunks)
    
    # Generate answer
    answer = answer_question_sync(
        request, 
        body.question, 
        context_text, 
        history=body.history, 
        is_general=is_general
    )
    
    return AskResponse(answer=answer)
