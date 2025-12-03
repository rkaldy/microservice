# Microservice Template

## Project Overview
This repository provides a FastAPI-based microservice starter kit that already connects the application layer, database
access, observability, testing, and deployment tooling. Clone it, rename the packages, and focus on business logic
instead of repeating boilerplate.

- **Application**: `src/app.py` assembles the API server with shared middleware, authentication, metrics, and versioned
  routers (for example `src/api/v1/router.py`) plus system endpoints living under `/-/liveness`, `/-/readiness`, and
  `/-/metrics`.
- **Data layer**: `src/db/engine.py` and `src/db/connection.py` expose an async SQLAlchemy engine with retry/backoff
  logic, Alembic migrations live in `/alembic`, and `src/settings/base.py` wires environment-specific configuration for
  PostgreSQL or MySQL.
- **Observability and resilience**: Structured logging (`src/utils/log.py`), Prometheus counters (`src/metrics.py` and
  `PrometheusMetricsMiddleware`), and optional Sentry integration (`src/utils/sentry.py`) are enabled at startup so the
  service emits actionable telemetry by default.
- **Tooling and operations**: Poetry manages dependencies, the multi-stage `Dockerfile` targets both dev and prod,
  `docker-compose.yaml` runs the API with local Postgres/MySQL, Helm manifests under `/chart`, Terraform modules under
  `/terraform`, GitLab CI definitions under `/gitlab-ci`, and helper scripts/Make targets keep builds and deployments
  consistent.
- **Testing**: `tests/` contains pytest suites that bootstrap an isolated async engine (`tests/engine.py`) and validate
  API authentication, metrics emission, and database retry behavior.

## Prerequisites

- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
- [helm](https://helm.sh/docs/intro/install)
- [terragrunt](https://terragrunt.gruntwork.io/docs/getting-started/install/)
- [pre-commit](https://pre-commit.com/#install) (optional but recommended for local linting)

## Preparation

### Create Google Cloud resources

1. Create a new [Google Cloud project](https://console.cloud.google.com/projectcreate).
2. Provision a new [GKE Autopilot cluster](https://console.cloud.google.com/kubernetes/list/overview) for deployments.

### Authenticate and configure tooling

Log in with the Google Cloud CLI:

```bash
gcloud auth login
```

Set the default project configuration:

```bash
gcloud config set project <your-project-id>
```

Configure the Kubernetes context:

```bash
gcloud services enable container.googleapis.com
gcloud container clusters get-credentials <your-cluster-name>
```

Install the pre-commit hooks:

```bash
pre-commit install
```

## Project Configuration

Use this template as a skeleton for your new project and update the following areas before the first deployment.

### Project name

- Rename the `src` package to the new project name.
- Update `Dockerfile`, `run-api-*.sh` scripts, and the `enable_all_loggers()` fixture to reflect the renamed package.
- Set the project name in `pyproject.toml`.
- Adjust the metadata in `run_api_app()` and `chart/Chart.yaml` (name, title, description, version, etc.).

### Python version

Select the target Python version in both the `Dockerfile` (`PYTHON_VERSION` build argument) and
`pyproject.toml` (sections `[tool.poetry.dependencies]` and `[tool.mypy]`).

### Database engine

The template is prepared for either PostgreSQL or MySQL:

- Configure the correct protocol, host, and port in `docker-compose.yaml`, `chart/values.yaml`, and
  any environment-specific values files.
- Remove unused drivers from `pyproject.toml` (`asyncpg` for PostgreSQL or `aiomysql` plus `cryptography`
  for MySQL).

### Terraform

Copy `terragrunt/terragrunt.hcl.example` to `terragrunt/terragrunt.hcl` and populate the variables to match
your environment (project IDs, regions, secrets, etc.).

### Helm charts

Copy `chart/values.yaml.example` to `chart/values.yaml` and customize image tags, credentials, endpoint URLs,
and any other runtime configuration.

## External Service Credentials

### GitLab

1. Create a project access token under **Settings → Access tokens**.
2. Name the token `gitlab-runner`, grant the `Maintainer` role, and enable the `api` and `create_runner` scopes.
3. Store the token in Google Secret Manager under the key `grafana-pat`

### Grafana

1. In Grafana Cloud or Enterprise, navigate to **Get Started → Logs → Kubernetes** to generate the deployment wizard.
2. Reuse the usernames for Loki and Prometheus targets inside `terraform/terragrunt.hcl`; do **not** deploy using
   Grafana’s generated manifests.
3. Click **Create token** and store the token in Google Secret Manager under the key `grafana-password`.

### Sentry

In Sentry, open **Settings → Projects → _<project>_ → SDK Setup → Client Keys (DSN)**, copy the DSN, and place it in
`chart/values.yaml` (or the relevant environment values file). Leave the setting blank if you do not plan to use Sentry.

## Installing

### Platform

The `terraform/platform` stack provisions shared infrastructure such as:

- Container registry
- GitLab CI/CD runners
- Grafana monitoring
- DNS
- Certificate management
- Secret storage

Run the following commands in `terraform/platform/helm_releases` first, because it installs Kubernetes CRDs required by
the rest of the platform modules:

```bash
terragrunt init && terragrunt plan && terragrunt apply
```

After the CRDs are in place, repeat the same commands inside `terraform/platform`.

### Microservice

For each environment under `terraform/env`, run:

```bash
terragrunt init && terragrunt plan && terragrunt apply
```

You can add, rename, or remove environment directories as needed, but remember to keep the GitLab CI pipelines under
`gitlab-ci/` in sync with the desired environments.

### CI/CD

Pipeline automation is under active development. Review the files in `gitlab-ci/` and adapt them to your project before
enabling deployments in production.
