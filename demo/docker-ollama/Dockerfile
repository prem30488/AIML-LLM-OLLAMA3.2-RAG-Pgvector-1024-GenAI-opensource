FROM ollama/ollama:latest

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create the script directly inside the Dockerfile
RUN printf "#!/bin/bash\n\
ollama serve &\n\
sleep 5\n\
echo \"Pulling models...\"\n\
ollama pull llama3.2:latest\n\
ollama pull mxbai-embed-large\n\
ollama pull nomic-embed-text\n\
wait" > entrypoint.sh

RUN chmod +x entrypoint.sh

EXPOSE 11434

ENTRYPOINT ["/bin/bash", "entrypoint.sh"]