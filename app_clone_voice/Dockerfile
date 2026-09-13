FROM python:3.11-slim

LABEL maintainer="app_clone_voice"
LABEL description="Standalone CLI for voice cloning from audio samples"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY voice_clone.py .
COPY bark/ bark/
COPY hubert/ hubert/
COPY source_voice_input/ source_voice_input/

# Create directories for models and prompts
RUN mkdir -p data/models/hubert bark/assets/prompts

# Set Python path
ENV PYTHONPATH=/app

# Entry point
ENTRYPOINT ["python", "voice_clone.py"]
CMD ["--help"]
