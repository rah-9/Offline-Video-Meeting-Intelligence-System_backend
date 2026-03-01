# Speech Intelligence System - Backend

The core processing engine of the Intelligence System. This backend handles heavy AI processing, running entirely offline models to extract transcriptions, summaries, topics, and action items from multimedia, and provides an API for the frontend.

## API Architecture
- **FastAPI**: Provides a high-performance REST API.
- **aiosqlite**: Asynchronous database interactions for managing job queues and results.
- **Uvicorn**: ASGI web server.

## AI Pipeline Technologies
The backend leverages multiple models sequentially (pipeline structure):
1. **faster-whisper**: High-performance audio transcription.
2. **BAAI/bge-small-en-v1.5 (sentence-transformers)**: Embeddings for semantic search and topic clustering.
3. **facebook/bart-large-cnn**: Abstractive text summarization.
4. **google/flan-t5-base**: Used for the Retrieval-Augmented Generation (RAG) Q&A system.
5. **spaCy (en_core_web_sm)**: NLP parser for extracting actionable verbs and tasks.

## Storage
- **Local DB (`db.sqlite3`)**: Stores job statuses (`pending`, `processing`, `completed`, `failed`) and final structured results.
- **Vector Store**: Uses **FAISS** to maintain localized vector embeddings of transcripts, required for the semantic RAG question-answering workflow.
- **Media Processing**: `ffmpeg-python` handles audio extraction from video files, and `yt-dlp` resolves and downloads YouTube media.

## Prerequisites
- **Python 3.10+**
- **FFmpeg**: You *must* have `ffmpeg` installed and accessible in your system's PATH.
  - Windows: Download from gyan.dev or use `winget install ffmpeg`.
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

## Local Setup

1. **Create and Activate a Virtual Environment**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download spaCy Model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Run the Server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

**Hardware Warning:** On your first run, the system will download the AI models to your local cache. Running all models simultaneously requires a minimum of **4GB - 8GB of RAM**. If available, install PyTorch with CUDA support for significantly faster processing.

## Deploying on Hugging Face Spaces
This backend supports deployment as a **Docker Space**. The existing `Dockerfile` is already configured to expose port **7860** and install all dependencies.

### Steps to publish
1. **Authenticate with the Hugging Face CLI**:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://hf.co/cli/install.ps1 | iex"
   hf login    # paste your access token (write permissions)
   ```

2. **Create a new Space or use an existing one** on the website.
3. **Add the Space remote** to this repository (replace `<username>`/`<repo>`):
   ```bash
   git remote add hf https://huggingface.co/spaces/<username>/<repo>
   ```

4. **Push the code** to the Space:
   ```bash
   git push hf main
   ```
   When prompted for a password, use your access token.

5. Once the build completes, the Space will be live and listening on port **7860**.

> **Tip:** Customize the `README.md` on the Space to set emoji, colors, or description; the file here will be copied when you push.

### Notes
* The `requirements.txt` already contains all necessary packages (FastAPI, Uvicorn, AI libraries, etc.).
* The `Dockerfile` in this repo uses a slim Python image, installs `ffmpeg`, and sets cache directories appropriately for Spaces.
* You can test the build locally with `docker build -t sis-backend . && docker run -p 7860:7860 sis-backend` before pushing.

After pushing, allow a few minutes for HF to build and start your Space. Monitor logs via the Hugging Face web UI.

