FROM python:3.11-bullseye

WORKDIR /app

# Install system dependencies for WhisperSpeech + audio
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        libavformat-dev \
        libavcodec-dev \
        libavutil-dev \
        libsndfile1 \
        git \
        curl \
        build-essential \
        libffi-dev \
        libssl-dev \
        python3-dev \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python deps
RUN pip install --upgrade pip setuptools wheel

# --- IMPORTANT: Install pytorch CPU wheels first ---
RUN pip install torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu

# 1. Install torchaudio explicitly (if it's in your requirements, this is a clean re-install)
RUN pip install torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cpu

# Now install WhisperSpeech + Flask + other libs
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .
#ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/:/usr/local/lib/:$LD_LIBRARY_PATH
EXPOSE 8000
# Run Flask app
CMD ["python", "tts_server.py"]
