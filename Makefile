.PHONY: help validate check-shell validate-compose validate-compose-root test-backend test-agents type-check-frontend lint-i18n build local-dev local-test-up local-test-down local-test-status

help:
	@echo "Available targets: validate, check-shell, validate-compose, validate-compose-root, test-backend, test-agents, type-check-frontend, lint-i18n, build, local-dev"
	@echo "                 local-test-up, local-test-down, local-test-status"

validate: check-shell test-backend type-check-frontend lint-i18n

check-shell:
	bash -n backend/entrypoint.sh
	bash -n setup.sh

validate-compose:
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "Docker CLI is not available." >&2; \
		exit 1; \
	fi
	@if docker compose version >/dev/null 2>&1; then \
		docker compose -f infrastructure/docker-compose.yml config --quiet; \
	elif command -v docker-compose >/dev/null 2>&1; then \
		docker-compose -f infrastructure/docker-compose.yml config --quiet; \
	else \
		echo "Neither 'docker compose' nor 'docker-compose' is available." >&2; \
		exit 1; \
	fi

validate-compose-root:
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "Docker CLI is not available." >&2; \
		exit 1; \
	fi
	@if docker compose version >/dev/null 2>&1; then \
		docker compose -f docker-compose.yml config --quiet; \
	elif command -v docker-compose >/dev/null 2>&1; then \
		docker-compose -f docker-compose.yml config --quiet; \
	else \
		echo "Neither 'docker compose' nor 'docker-compose' is available." >&2; \
		exit 1; \
	fi

test-backend:
	@PYTEST=""; \
	if [ -f "$(CURDIR)/.venv/bin/pytest" ]; then PYTEST="$(CURDIR)/.venv/bin/pytest"; \
	elif [ -f "$(CURDIR)/backend/.venv/bin/pytest" ]; then PYTEST="$(CURDIR)/backend/.venv/bin/pytest"; \
	elif command -v pytest >/dev/null 2>&1; then PYTEST="pytest"; \
	else echo "pytest not found. Activate a virtualenv or install pytest." >&2; exit 1; fi; \
	cd backend && $$PYTEST

test-agents:
	@PYTEST=""; \
	if [ -f "$(CURDIR)/.venv/bin/pytest" ]; then PYTEST="$(CURDIR)/.venv/bin/pytest"; \
	elif [ -f "$(CURDIR)/backend/.venv/bin/pytest" ]; then PYTEST="$(CURDIR)/backend/.venv/bin/pytest"; \
	elif command -v pytest >/dev/null 2>&1; then PYTEST="pytest"; \
	else echo "pytest not found. Activate a virtualenv or install pytest." >&2; exit 1; fi; \
	cd backend && $$PYTEST tests/test_memory_service.py tests/test_dream_motor.py tests/test_model_router.py tests/test_agent_orchestrator.py -v

type-check-frontend:
	cd frontend && npx tsc --noEmit

lint-i18n:
	python3 scripts/check_i18n.py

build: validate-compose
	@if docker compose version >/dev/null 2>&1; then \
		docker compose -f infrastructure/docker-compose.yml build; \
	elif command -v docker-compose >/dev/null 2>&1; then \
		docker-compose -f infrastructure/docker-compose.yml build; \
	else \
		echo "Neither 'docker compose' nor 'docker-compose' is available." >&2; \
		exit 1; \
	fi

local-dev: validate validate-compose
	@if docker compose version >/dev/null 2>&1; then \
		docker compose -f infrastructure/docker-compose.yml up --build; \
	elif command -v docker-compose >/dev/null 2>&1; then \
		docker-compose -f infrastructure/docker-compose.yml up --build; \
	else \
		echo "Neither 'docker compose' nor 'docker-compose' is available." >&2; \
		exit 1; \
	fi

local-test-up:
	./scripts/local_test_up.sh

local-test-down:
	./scripts/local_test_down.sh

local-test-status:
	./scripts/local_test_status.sh