from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import spacy
from faster_whisper import WhisperModel
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import torch

from app.config import settings
from app.db.database import init_db
from app.api import routes_health, routes_processing, routes_query
from app.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    await init_db()
    logger.info("Database initialized.")
    
    # Load Models as State Singletons
    logger.info("Loading AI Models... This may take a minute.")
    
    app.state.whisper = WhisperModel(
        settings.WHISPER_MODEL,
        device=settings.WHISPER_DEVICE,
        compute_type=settings.WHISPER_COMPUTE_TYPE
    )
    logger.info("Whisper loaded.")
    
    app.state.embedder = SentenceTransformer(
        settings.EMBEDDING_MODEL,
        device="cpu"
    )
    logger.info("Embedder loaded.")
    
    app.state.summarizer = pipeline(
        "summarization",
        model=settings.SUMMARIZATION_MODEL,
        device=-1 # CPU
    )
    logger.info("Summarizer loaded.")
    
    app.state.nlp = spacy.load(settings.SPACY_MODEL)
    logger.info("spaCy loaded.")

    app.state.qa_pipeline = pipeline(
        "text2text-generation",
        model=settings.QA_MODEL,
        device=0 if torch.cuda.is_available() else -1,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    logger.info("QA pipeline loaded.")
    
    logger.info("All models loaded successfully.")
    
    yield
    
    # Cleanup
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(routes_health.router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(routes_processing.router, prefix=settings.API_V1_STR, tags=["Processing"])
app.include_router(routes_query.router, prefix=settings.API_V1_STR, tags=["Query"])
