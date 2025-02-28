#!/bin/bash

# Get IP address (for Mac)
export HOST_IP=$(ipconfig getifaddr en0)
# Uncomment and set manually if needed:
# export HOST_IP="192.168.1.100"

# Proxy settings (if you're behind a proxy)
# export http_proxy="http://proxy.example.com:8080"
# export https_proxy="http://proxy.example.com:8080"
export no_proxy="localhost,127.0.0.1,${HOST_IP}"

# ChatQnA Service Settings
export CHATQNA_REDIS_VECTOR_PORT=6379
export CHATQNA_REDIS_VECTOR_INSIGHT_PORT=8001
export CHATQNA_REDIS_DATAPREP_PORT=6007
export CHATQNA_REDIS_URL="redis://redis:6379"
export CHATQNA_INDEX_NAME="chatqna"

# Service Ports (using new ports to avoid conflicts)
export EMBEDDING_SERVER_PORT=6001
export RETRIEVER_SERVICE_PORT=7001
export MEGA_SERVICE_PORT=8889

# Ollama Settings
export LLM_SERVER_HOST_IP="host.docker.internal"
export LLM_SERVER_PORT=11434
export LLM_MODEL="mistral"

# Print the settings
echo "Environment variables set:"
echo "HOST_IP: ${HOST_IP}"
echo "EMBEDDING_SERVER_PORT: ${EMBEDDING_SERVER_PORT}"
echo "RETRIEVER_SERVICE_PORT: ${RETRIEVER_SERVICE_PORT}"
echo "MEGA_SERVICE_PORT: ${MEGA_SERVICE_PORT}"
echo "LLM_SERVER_HOST_IP: ${LLM_SERVER_HOST_IP}"
echo "LLM_MODEL: ${LLM_MODEL}" 