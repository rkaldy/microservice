.PHONY: help
help: # Show help for each of the Makefile recipes
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m: $$(echo $$l | cut -f 2- -d'#')\n"; done

PROJECT_NAME := $(shell grep "name:" chart/Chart.yaml | head -n 1 | cut -d " " -f 2)
# rename to your cloud docker registry
DOCKER_REGISTRY := europe-central2-docker.pkg.dev/microservice-template-475915/docker
IMAGE = $(DOCKER_REGISTRY)/$(PROJECT_NAME)
TAG = $(shell git rev-parse --short=8 HEAD)
BUILD_TARGET ?= dev
CONTAINER_ID ?= $(PROJECT_NAME)-api-1
TA ?= -v --ignore=tests/e2e/ tests/

build: # Build the app container
	poetry lock
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

migration: # Create alembic migration script from the current state, set MSG for migration comment message
	docker exec -it $(CONTAINER_ID) alembic upgrade head
	docker exec -it $(CONTAINER_ID) alembic revision --autogenerate -m "$(MSG)"
	docker exec -it $(CONTAINER_ID) alembic upgrade head

push: # Build image and push it to the registry. You can specify the build target (default: dev)
	docker build -t $(IMAGE):$(TAG) --target $(BUILD_TARGET) .
	docker push $(IMAGE):$(TAG)

TPL_FLAG := $(if $(strip $(TPL)),--show-only templates/$(TPL),)
helm-template: # Render helm templates for BUILD_TARGET (default: dev). If TPL is set, it renders only only template.
	@helm template -n $(PROJECT_NAME)-$(BUILD_TARGET) \
		--set image.repository="$(IMAGE)" \
		--set image.tag="$(TAG)" \
		--values chart/values.yaml \
		--values chart/values.$(BUILD_TARGET).yaml \
		$(TPL_FLAG) $(PROJECT_NAME) chart/

install: # Deploy the application to the dev cluster. The current revision must be pushed to docker registry first. Intentionally allows only development deploy to prevent accidentally rewriting production cluster.
	helm upgrade --install \
		--namespace $(PROJECT_NAME)-dev \
		--set env="dev" \
		--set image.repository="$(IMAGE)" \
		--set image.tag="$(TAG)" \
		--values chart/values.yaml \
		--values chart/values.dev.yaml \
		$(PROJECT_NAME) chart/

uninstall: # Uninstall the application from the dev cluster. Intentionally allows only development deploy to prevent accidentally production cluster deletion.
	helm uninstall --namespace $(PROJECT_NAME)-dev $(PROJECT_NAME)
