from fastapi import Request
from app.utils.logger import logger
import gc
import torch
import time

def transcribe_audio_sync(request: Request, audio_path: str, job_id: str) -> list:
    """
    Transcribes audio using the app-level Whisper model singleton.
    Returns a list of dicts with text and timestamps.
    """
    logger.info(f"Transcribing audio for job {job_id}")
    
    whisper_model = request.app.state.whisper
    
    start_time = time.time()
    segments, info = whisper_model.transcribe(audio_path, beam_size=5, word_timestamps=False)
    
    transcript_data = []
    
    for segment in segments:
        transcript_data.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip(),
            "id": segment.id
        })
        
    logger.info(f"Transcription for job {job_id} finished in {time.time() - start_time:.2f}s")
    
    # If on GPU, clear VRAM cache explicitly
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()
        
    return transcript_data
