# Makefile for {{ cookiecutter.__target }}
{% if cookiecutter.include_frontend == "yes" %}
# Delegates to backend/ and frontend/ Makefiles
{% else %}
# Delegates to backend/ Makefile
{% endif %}

.DEFAULT_GOAL := help

IMAGE ?= {{ cookiecutter.__container_registry }}/{{ cookiecutter.__target }}
IMAGE_TAG ?= latest

##############################################################################
# Backend
##############################################################################

.PHONY: backend-install
backend-install: ## Install backend (Python venv + packages)
	$(MAKE) -C backend install

.PHONY: backend-start
backend-start: ## Start backend dev server
	$(MAKE) -C backend run

.PHONY: backend-test
backend-test: ## Run backend tests
	$(MAKE) -C backend test

.PHONY: backend-check
backend-check: ## Check backend code (ruff + zpretty)
	$(MAKE) -C backend check

.PHONY: backend-format
backend-format: ## Format backend code
	$(MAKE) -C backend format

.PHONY: backend-clean
backend-clean: ## Clean backend installation
	$(MAKE) -C backend clean
{% if cookiecutter.include_frontend == "yes" %}

##############################################################################
# Frontend
##############################################################################

.PHONY: frontend-install
frontend-install: ## Install frontend (pnpm + mrs-developer)
	$(MAKE) -C frontend install

.PHONY: frontend-start
frontend-start: ## Start frontend dev server
	$(MAKE) -C frontend run

.PHONY: frontend-build
frontend-build: ## Build frontend for production
	$(MAKE) -C frontend volto-build

.PHONY: frontend-test
frontend-test: ## Run frontend tests (Jest)
	$(MAKE) -C frontend test

.PHONY: frontend-check
frontend-check: ## Check frontend code (eslint + prettier + stylelint)
	$(MAKE) -C frontend check

.PHONY: frontend-format
frontend-format: ## Format frontend code
	$(MAKE) -C frontend format

.PHONY: frontend-i18n
frontend-i18n: ## Sync frontend translations
	$(MAKE) -C frontend i18n

.PHONY: frontend-storybook-start
frontend-storybook-start: ## Start Storybook dev server
	$(MAKE) -C frontend volto-storybook-start

.PHONY: frontend-storybook-build
frontend-storybook-build: ## Build Storybook
	$(MAKE) -C frontend volto-storybook-build

.PHONY: frontend-clean
frontend-clean: ## Clean frontend installation
	$(MAKE) -C frontend clean
{% endif %}

##############################################################################
# Orchestration
##############################################################################

.PHONY: install
{% if cookiecutter.include_frontend == "yes" %}
install: backend-install frontend-install ## Install backend and frontend
{% else %}
install: backend-install ## Install backend
{% endif %}

.PHONY: check
{% if cookiecutter.include_frontend == "yes" %}
check: backend-check frontend-check ## Run all code checks
{% else %}
check: backend-check ## Run all code checks
{% endif %}

.PHONY: format
{% if cookiecutter.include_frontend == "yes" %}
format: backend-format frontend-format ## Format all code
{% else %}
format: backend-format ## Format all code
{% endif %}

.PHONY: test
{% if cookiecutter.include_frontend == "yes" %}
test: backend-test frontend-test ## Run all tests
{% else %}
test: backend-test ## Run all tests
{% endif %}
{% if cookiecutter.include_frontend == "yes" %}

.PHONY: i18n
i18n: frontend-i18n ## Sync translations
{% endif %}

.PHONY: clean
{% if cookiecutter.include_frontend == "yes" %}
clean: backend-clean frontend-clean ## Clean all installations
{% else %}
clean: backend-clean ## Clean all installations
{% endif %}

##############################################################################
# Docker
##############################################################################

.PHONY: build-image
build-image: ## Build Docker image
	docker build . -t $(IMAGE):$(IMAGE_TAG)

##############################################################################
# Help
##############################################################################

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'
