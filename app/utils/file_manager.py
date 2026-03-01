import os
import aiofiles
from fastapi import UploadFile
from app.config import settings

async def save_upload_file(upload_file: UploadFile, job_id: str) -> str:
    # Ensure a unique directory for the job to store its files
    job_dir = os.path.join(settings.DATA_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    file_path = os.path.join(job_dir, upload_file.filename)
    
    # Async safe file reading
    async with aiofiles.open(file_path, 'wb') as out_file:
        while content := await upload_file.read(1024 * 1024):  # async read chunk
            await out_file.write(content)  # async write chunk
            
    return file_path
    
def get_job_dir(job_id: str) -> str:
    path = os.path.join(settings.DATA_DIR, job_id)
    os.makedirs(path, exist_ok=True)
    return path
    
def get_vector_store_dir(job_id: str) -> str:
    path = os.path.join(settings.VECTOR_STORE_DIR, job_id)
    os.makedirs(path, exist_ok=True)
    return path
