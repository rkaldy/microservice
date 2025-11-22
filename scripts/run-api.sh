#!/usr/bin/bash
set -e

exec gunicorn \
    --bind 0.0.0.0:80 \
    --log-level "${LOG_LEVEL}" \
    --workers ${API_SERVER_WORKERS} \
    --error-logfile - \
    --worker-class uvicorn.workers.UvicornWorker \
    src.app:create_api_app
