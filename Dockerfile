# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (ffmpeg is required)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy the application code
COPY . .

# Hugging Face Spaces runs as user 1000.
# We need to give write permissions to cache and data directories.
# Set cache directories to /app/.cache
ENV TRANSFORMERS_CACHE=/app/.cache
ENV HF_HOME=/app/.cache
ENV TORCH_HOME=/app/.cache/torch

# Create cache and data directories with open permissions
RUN mkdir -p /app/.cache \
    && mkdir -p /app/data \
    && mkdir -p /app/outputs \
    && mkdir -p /app/vector_store \
    && chmod -R 777 /app

# Expose port (HF Spaces defaults to 7860)
EXPOSE 7860

# Command to run the FastAPI app using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
