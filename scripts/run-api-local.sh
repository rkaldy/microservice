#!/usr/bin/bash
set -e

exec uvicorn \
    --reload \
    --host 0.0.0.0 \
    --port 80 \
    --log-level "${LOG_LEVEL}" \
    --factory \
    src.app:create_api_app
