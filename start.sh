#!/bin/bash

echo "Starting Concstar Backend with Poetry and Uvicorn..."
poetry run uvicorn app.main:app --reload
