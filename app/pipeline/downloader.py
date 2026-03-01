import yt_dlp
import os
from app.utils.logger import logger
from app.config import settings
import asyncio

def download_video_sync(url: str, job_id: str) -> str:
    logger.info(f"Downloading video for job {job_id}: {url}")
    
    output_dir = os.path.join(settings.DATA_DIR, job_id)
    os.makedirs(output_dir, exist_ok=True)
    
    output_template = os.path.join(output_dir, 'video.%(ext)s')
    
    ydl_opts = {
        'format': 'bestaudio/best', # Download best audio or fall back to best
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        # Find the actual downloaded file name
        filepath = ydl.prepare_filename(info_dict)
        return filepath

async def download_video(url: str, job_id: str) -> str:
    return await asyncio.to_thread(download_video_sync, url, job_id)
