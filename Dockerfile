# Use a stable Python base image (Python 3.11-slim has precompiled wheels for PyTorch and TTS)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5050 \
    TTS_HOME=/data/tts

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsndfile1 \
    espeak-ng \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install CPU-only PyTorch and Torchaudio first to prevent CUDA bloating
RUN pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Create outputs, voices, and cache folders
RUN mkdir -p outputs voices /data/tts

# Expose port (Railway will map the internal PORT to external port)
EXPOSE 5050

# Run the Flask app
CMD ["python", "App.py"]
