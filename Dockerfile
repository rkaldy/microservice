ARG PYTHON_VERSION=3.13


FROM python:${PYTHON_VERSION}-slim AS deps-base
ENV PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=2.2 \
    POETRY_VIRTUALENVS_IN_PROJECT=true
WORKDIR /app

RUN pip install --upgrade pip && pip install "poetry==$POETRY_VERSION"


FROM deps-base AS deps-dev
COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --with dev --no-root


FROM deps-base AS deps-prod
COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --only main --no-root


FROM python:${PYTHON_VERSION}-slim AS base
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends vim curl iputils-ping && \
    apt-get clean
RUN useradd --uid 1000 --user-group --no-create-home app

COPY src src

EXPOSE 5000
#CMD ["scripts/run-api.sh"]


FROM base AS dev
ENV APP_ENV=development
COPY --from=deps-dev /app/.venv /app/.venv
COPY tests tests
#COPY scripts/run-api-dev.sh scripts/run-api.sh
RUN chown app:app /app
USER app


FROM base AS prod
ENV APP_ENV=production
COPY --from=deps-prod /app/.venv /app/.venv
#COPY scripts/run-api-prod.sh scripts/run-api.sh
RUN chown -R app:app /app
USER app
