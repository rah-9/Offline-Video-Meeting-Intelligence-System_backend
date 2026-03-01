from fastapi import Request
from app.utils.logger import logger
import re

def clean_transcript_sync(request: Request, transcript_data: list, job_id: str) -> list:
    """
    Cleans transcript text using spaCy (e.g. basic normalization).
    """
    logger.info(f"Cleaning transcript for job {job_id}")
    
    nlp = request.app.state.nlp
    cleaned_data = []
    
    for segment in transcript_data:
        text = segment["text"]
        
        # Remove multiple spaces/newlines
        text = re.sub(r'\s+', ' ', text).strip()
        
        if text:
            cleaned_data.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": text,
                "id": segment["id"]
            })
            
    return cleaned_data
