# Microservice Template

## Prerequisities

* [gcloud CLI](https://cloud.google.com/sdk/docs/install)
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
* [helm](https://helm.sh/docs/intro/install)

## Preparation

### Create a new project

Create a new [project](https://console.cloud.google.com/projectcreate) in GCP

Create a new [cluster](https://console.cloud.google.com/kubernetes/list/overview), in Autopilot mode

Log in from console to your Google account:
```bash
gcloud auth login
```
Set the default project configuration
```bash
gcloud config set project <your-project-id>`
```
Set kubernetes context
```bash
gcloud services enable container.googleapis.com
gcloud container clusters get-credentials <your-cluster-name>
```

## Customizing the template
Use this template as a skeleton for you new project. You need to rewrite following things:

### Project name
* rename `src` package to your project name
* rename appropriately the `src` package in `Dockerfile`, `run-api-*.sh` scripts and `enable_all_loggers()` fixture
* add project name to `pyproject.toml`
* add project name and description to `run_api_app()` function
* add project name and description to `Chart.yaml`

### Python version
Set desired python version in `Dockerfile` and in `pyproject.yaml`, sections `[tool.poetry.dependencies]` and `[tool.mypy]`

### Database engine
The template allows you to use either mysql or postgresql as database engine.
* set appropriate db protocol, host and port in `docker-compose.yaml`, `values.yaml` and `values-*.yaml`
* in `pyproject.toml` remove lines with either `asyncpg` or `aiomysql` and `cryptography` (the `cryptography` library is used for mysql connection only)

## Docker registry
Set your cloud docker registry (where your app images will be stored) in Makefile if you want to build and push images directly from local computer.

* Run `pre-commit install` in the command line
