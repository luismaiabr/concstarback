#!/bin/bash

PORT=8000

echo "Killing any process running on port $PORT..."
fuser -k $PORT/tcp 2>/dev/null || true

echo "Starting Concstar Backend with Poetry and Uvicorn..."
poetry run uvicorn app.main:app --reload --port $PORT
