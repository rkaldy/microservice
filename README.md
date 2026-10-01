# Microservice Template

## Project Overview
This repository provides a FastAPI-based microservice starter kit that already connects the application layer, database
access, observability, testing, and deployment tooling. Clone it, rename the packages, and focus on business logic
instead of repeating boilerplate.

- **Application**: `src/app.py` boots the FastAPI server with simple Bearer authentication, health checks
  (`/-/liveness`, `/-/readiness`), a metrics endpoint (`/-/metrics`), and an example versioned router at
  `src/api/v1/router.py`.
- **Data layer**: `src/db/engine.py` wraps the SQLAlchemy engine, `src/db/connection.py` wraps the SQLAlchemy connection
  with optional retry/backoff logic. Alembic migrations live in `/alembic`, and `src/settings/base.py` centralizes the
  environment-specific configuration for PostgreSQL or MySQL.
- **Observability and resilience**: Logging (`src/utils/log.py`), Prometheus counters (`src/metrics.py` and
  `PrometheusMetricsMiddleware`), and optional Sentry integration (`src/utils/sentry.py`) are wired in at startup so the
  service emits useful telemetry out of the box.
- **Tooling and operations**: Poetry manages dependencies, the multi-stage `Dockerfile` targets dev and prod images,
  `docker-compose.yaml` orchestrates local services, Helm manifests live under `chart/`, Terraform modules under
  `terraform/`, and GitHub Actions workflows under `.github/workflows/`.
- **Testing**: `tests/` ships with pytest suites that bootstrap an test database engine (`tests/engine.py`)
- **Local run**: Use `docker-compose.yaml` for local containers, and lean on the `Makefile` targets for build, lint, and
  test workflows.

## Prerequisites

- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
- [helm](https://helm.sh/docs/intro/install)
- [terragrunt](https://terragrunt.gruntwork.io/docs/getting-started/install/)
- [docker](https://docs.docker.com/engine/install/)
- [poetry](https://python-poetry.org/)
- [pre-commit](https://pre-commit.com/#install) (optional but recommended for local linting)

## Preparation

### Create Google project and configure tooling

Create a new [Google Cloud project](https://console.cloud.google.com/projectcreate).

Log in with the Google Cloud CLI:

```bash
gcloud auth login
```

Set the default project configuration:

```bash
gcloud config set project <your-project-id>
```

### Prepare Github authentication

- In your Github repository, create a fine grained personal access token (PAT).
- Add permissions Actions (read-only), Administration (read and write) and Environments (read and write) for it.
- Store the token value in Google Secret Manager with name `github-token`.

## Project Configuration

Use this template as a skeleton for your new project and update the following areas before the first deployment.

### Project name

- Rename the `src` package to the new project name.
- Update `Dockerfile`, `run-api-*.sh` scripts, and the `enable_all_loggers()` fixture to reflect the renamed package.
- Set the project name in `pyproject.toml`.
- Adjust the metadata in `create_api_app()` and `chart/Chart.yaml` (name, title, description, version, etc.).

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

Copy `terraform/config.hcl.example` to `terraform/config.hcl` and populate the variables to match
your environment (project IDs, regions, secrets, etc.).

### Helm charts

Copy `chart/values.yaml.example` to `chart/values.yaml` and customize image tags, credentials, endpoint URLs,
and any other runtime configuration.

## External Service Credentials

### GitHub

GitHub Actions deployments are designed to use Workload Identity Federation. Create the shared identity pool and provider
before applying an application environment; do not use a long-lived Google service-account key.

### Grafana

1. In Grafana Cloud or Enterprise, navigate to **Get Started → Logs → Kubernetes** to generate the deployment wizard.
2. Reuse the usernames for Loki and Prometheus targets inside `terraform/config.hcl`; do **not** deploy using
   Grafana’s generated manifests.
3. Click **Create token** and store the token in Google Secret Manager under the key `grafana-password`.

### Sentry

In Sentry, open **Settings → Projects → _<project>_ → SDK Setup → Client Keys (DSN)**, copy the DSN, and place it in
`chart/values.yaml` (or the relevant environment values file). Leave the setting blank if you do not plan to use Sentry.

## Installing

### Platform

The `terraform/platform` stack provisions shared infrastructure such as:

- Container registry
- GitHub Actions Workload Identity Federation
- GKE cluster
- Grafana monitoring
- DNS
- Certificate management
- Secret storage

The platform is split into Terragrunt units with an explicit dependency graph:

```text
services ─┬─> cluster ─> crds ─┐
          └─> cloud ───────────┴─> kubernetes
```

For the initial bootstrap, copy `terraform/config.hcl.example` to `terraform/config.hcl` and fill all variable values.
Then run in the `terraform/platform` directory:

```bash
gcloud auth application-default login
terragrunt backend bootstrap
terragrunt run --all init
terragrunt run --all apply
```

### Application environment

For each environment under `terraform/env`, run from the corresponding directory:

```bash
terragrunt init && terragrunt plan && terragrunt apply
```

You can add, rename, or remove environment directories as needed, but keep the GitHub Actions environments and workflows
in sync with the desired environments.

## Local development

Build the local Docker image:

```bash
poetry update
make build
```

Install the pre-commit hooks:

```bash
pre-commit install
```

Initialize the local database (run the last command inside the container shell):

```bash
make up-d
make bash
alembic upgrade head
```

### Pushh docker images

To allow pushing docker images to Google Artifact Registry, run once:

```bash
gcloud auth configure-docker <cluster-location>-docker.pkg.dev
```

Push docker image to the artifact registry:

```bash
make push
```

### Deployment to the Google Cluster

Rename `charts/values.yaml.example` to `charts/values.yaml` and fill all variable values. Then run:

```bash
make install
```

## CI/CD

### Pull requests

Opening a pull request against `master`, reopening it, or pushing another commit to it starts the branch workflow. GitHub checks
out the pull request merge commit, so the pipeline validates the result of merging the branch with the current `master`, rather
than testing the branch in isolation.

The branch workflow:

1. builds the development image;
2. runs pre-commit checks and tests;
3. builds and pushes an image tagged with the short Git commit SHA;
4. deploys the image to the `dev` environment.

Only one development pipeline runs at a time. A newer pull request run cancels the previous one because all pull requests share
the same development cluster.

### Merge to master

Closing a pull request without merging it does not publish or deploy anything. After a pull request is merged into `master`, the
master workflow runs the common pipeline with `ENVIRONMENT=stage`. It runs the checks and pushes a stage image, but does not
automatically run `make install`.

`ENVIRONMENT` determines both the Helm configuration and Docker build target:

| `ENVIRONMENT` | Docker target | Helm values | Kubernetes namespace |
|---|---|---|---|
| `dev` | `dev` | `chart/values.dev.yaml` | `microservice-dev` |
| `stage` | `prod` | `chart/values.stage.yaml` | `microservice-stage` |
| `prod` | `prod` | `chart/values.prod.yaml` | `microservice-prod` |

### Manual deployment

To deploy stage or production:

1. open **Actions** in the GitHub repository;
2. select **CI (master)**;
3. click **Run workflow**;
4. select `stage` or `prod` in **Environment to deploy**;
5. click **Run workflow** to confirm.

The manual run repeats the build, checks, and image push before executing `make install` for the selected environment. The
**Run workflow** button is available only after `master.yaml` exists on the repository's default branch.

For additional production protection, configure required reviewers for the `prod` GitHub environment. GitHub will then pause
the publish/deployment job until an authorized reviewer approves it.
