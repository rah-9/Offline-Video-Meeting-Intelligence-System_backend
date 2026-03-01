import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Offline Video & Meeting Intelligence System"
    API_V1_STR: str = "/api/v1"
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    VECTOR_STORE_DIR: str = os.path.join(BASE_DIR, "vector_store")
    OUTPUTS_DIR: str = os.path.join(BASE_DIR, "outputs")
    
    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{os.path.join(BASE_DIR, 'db.sqlite3')}"
    
    # Models Config
    WHISPER_MODEL: str = "medium"
    WHISPER_DEVICE: str = "cuda"
    WHISPER_COMPUTE_TYPE: str = "float16"
    
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    SUMMARIZATION_MODEL: str = "facebook/bart-large-cnn"
    QA_MODEL: str = "google/flan-t5-base"
    SPACY_MODEL: str = "en_core_web_sm"

    class Config:
        case_sensitive = True

settings = Settings()

# Ensure directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)
os.makedirs(settings.OUTPUTS_DIR, exist_ok=True)
