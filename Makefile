.PHONY: help
help: # Show help for each of the Makefile recipes
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m: $$(echo $$l | cut -f 2- -d'#')\n"; done

PROJECT_NAME := $(shell echo "$${COMPOSE_PROJECT_NAME:-$$(basename $$(pwd))}")
CONTAINER_ID ?= $(PROJECT_NAME)-api-1
TA ?= -v --ignore=tests/e2e/ tests/

build: # Build the app container
	docker compose -p $(PROJECT_NAME) -f docker-compose.yaml build

up: # Spin up the project
	docker compose -p $(PROJECT_NAME) -f docker-compose.yaml up

up-d: # Spin up the project in the background
	docker compose -p $(PROJECT_NAME) -f docker-compose.yaml up -d

down: # Tear down the project
	docker compose -p $(PROJECT_NAME) -f docker-compose.yaml down

test: # Run tests in project, optionally set CONTAINER_ID for docker name and TA for test arguments
	docker exec -it $(CONTAINER_ID) pytest $(TA)

retest: # Run tests from the last failed test
	docker exec -it $(CONTAINER_ID) pytest --lf -v tests/

bash: # Start an interactive session with the project
	docker exec -it $(CONTAINER_ID) bash

lint: # Run the every linting script and a format script
	pre-commit install --install-hooks
	pre-commit run --all-files
