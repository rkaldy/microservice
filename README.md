# Microservice Template

## Customizing the template

Use this template as a skeleton for you new project. You need to rewrite following things:

### Project name
* rename `src` package to your project name
* rename appropriately the `src` package in `Dockerfile`, `run-api-*.sh` scripts and `enable_all_loggers()` fixture
* add project name to `pyproject.toml`
* add project name and description to `run_api_app()` function

### Python version
Set desired python version in `Dockerfile` and in `pyproject.yaml`, sections `[tool.poetry.dependencies]` and `[tool.mypy]`

### Database engine
The template allows you to use either mysql or postgresql as database engine.
* set appropriate db protocol, host and port in `docker-compose.yaml`
* in `pyproject.toml` remove lines with either `asyncpg` or `aiomysql` and `cryptography` (the `cryptography` library is used for mysql connection only)

## Docker registry
Set your cloud docker registry (where your app images will be stored) in Makefile if you want to build and push images directly from local computer.

* Run `pre-commit install` in the command line
