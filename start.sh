#!/bin/bash
set -e

# Create storage directories
mkdir -p storage/uploads storage/outputs storage/temp

# Start the API with port from environment or default to 8000
exec uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
