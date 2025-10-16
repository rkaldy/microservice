# Microservice Template

## Customizing the template

Use this template as a skeleton for you new project. You need to rewrite following things:

### Project name
* rename `src` folder to your project name
* rename appropriately the `src` folder in `Dockerfile` and `run-api-*.sh` scripts
* add project name to `pyproject.toml`
* add project name and description to `run_api_app()` function

### Database engine
The template allows you to use either mysql or postgresql as database engine. 
* choose `mysql` or `postgres` as database instance in `docker-compose.yaml`
* in `pyproject.toml` remove lines with either `asyncpg` or `aiomysql` and `cryptography` (the `cryptography` library is used for mysql connection only)
* in class `Settings` set `DB_PROTOCOL` to `postgres+asyncpg` or `mysql+aiomysql`
