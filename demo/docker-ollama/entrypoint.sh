#!/bin/bash

# Start Ollama in the background
ollama serve &

# Wait for the server to be ready
echo "Waiting for Ollama server to start..."
while ! curl -s http://localhost:11434/api/tags > /dev/null; do
    sleep 1
done

# Pull the requested models
echo "Pulling llama3.2:latest..."
ollama run llama3.2:latest

echo "Pulling mxbai-embed-large..."
ollama run mxbai-embed-large

# Keep the container running by bringing the server back to the foreground
wait