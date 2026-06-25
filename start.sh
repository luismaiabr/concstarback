#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

PORT=$(grep -E "^BACK_END_PORT=" .env | cut -d'=' -f2 | tr -d '\r' | tr -d ' ' | tr -d '"' | tr -d "'")
PORT=${PORT:-8000}

echo "Killing any process running on port $PORT..."
fuser -k $PORT/tcp 2>/dev/null || true

echo "Starting Concstar Backend with Poetry and Uvicorn..."
poetry run uvicorn app.main:app --host 100.101.78.95 --reload --port $PORT
