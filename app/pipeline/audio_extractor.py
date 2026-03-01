import ffmpeg
import os
import imageio_ffmpeg
from app.utils.logger import logger
import asyncio

def extract_audio_sync(input_path: str, job_id: str) -> str:
    """Extracts 16kHz mono wav audio from the input file."""
    logger.info(f"Extracting audio for job {job_id}: {input_path}")
    
    output_path = os.path.join(os.path.dirname(input_path), 'audio.wav')
    
    try:
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(stream, output_path, acodec='pcm_s16le', ac=1, ar='16k')
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg.run(stream, cmd=ffmpeg_exe, overwrite_output=True, quiet=True)
        return output_path
    except ffmpeg.Error as e:
        logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
        raise Exception("Failed to extract audio")

async def extract_audio(input_path: str, job_id: str) -> str:
    return await asyncio.to_thread(extract_audio_sync, input_path, job_id)
