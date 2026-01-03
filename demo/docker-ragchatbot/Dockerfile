# STEP 1: Use a standard Python base image (CPU-Only)
FROM python:3.10-bullseye

WORKDIR /app

# STEP 2: Install core system dependencies (Crucial for source build)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        curl \
        build-essential \
        python3-dev \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# STEP 3: Install Python Dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel

# --- CRITICAL STEP 1: Install only the core Torch library ---
# We use torch 1.13.0/1.13.1, which is the version required for DeepFloyd.
# We skip torchvision/torchaudio here, as the requirements.txt will handle them.
#RUN pip install \
#    torch \
#    --index-url https://download.pytorch.org/whl/cpu

	# Source - https://stackoverflow.com/a
	# Posted by trsvchn, modified by community. See post 'Timeline' for change history
	# Retrieved 2025-12-10, License - CC BY-SA 4.0
#RUN pip install torchaudio \
#	  --index-url https://download.pytorch.org/whl/cpu

#RUN pip install torchvision \
#	  	  --index-url https://download.pytorch.org/whl/cpu


# --- CRITICAL STEP 2: Install the rest from requirements.txt ---
# If torchvision==0.14.1 and torchaudio==0.13.1 wheels are not found, 
# pip will use the build tools installed in STEP 2 to compile them from source.
RUN pip install --no-cache-dir -r requirements.txt

# STEP 4: Application Files
COPY . .

# STEP 5: Container Execution
EXPOSE 8007
CMD ["python", "-u" , "app.py"]