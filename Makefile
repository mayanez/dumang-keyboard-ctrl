.PHONY: setup
setup: ## Install the poetry environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using pyenv and poetry"
	@poetry install
	@poetry run pre-commit install

.PHONY: shell
shell: ## Activate the poetry environment
	@echo "🚀 Activating virtual environment using pyenv and poetry"
	@poetry shell

.PHONY: check
check: ## Run pre-commit checks.
	@echo "🚀 Checking Poetry lock file consistency with 'pyproject.toml': Running poetry lock --check"
	@poetry check --lock
	@echo "🚀 Running pre-commit"
	@poetry run pre-commit run -a

.PHONY: check-strict
check-strict: ## Run code quality tools
	@echo "🚀 Static type checking: Running mypy"
	@poetry run mypy
	@echo "🚀 Linting code: unning ruff"
	@poetry run ruff dumang_ctrl

.PHONY: build
build: clean-build ## Build wheel file using poetry
	@echo "🚀 Creating wheel file"
	@poetry version $(shell git describe --tags --abbrev=0)
	@poetry build

.PHONY: clean-build
clean-build: ## clean build artifacts
	@rm -rf dist

.PHONY: publish
publish: ## publish a release to pypi.
	@echo "🚀 Publishing: Dry run."
	@poetry config pypi-token.pypi $(PYPI_TOKEN)
	@poetry publish --dry-run
	@echo "🚀 Publishing."
	@poetry publish

.PHONY: publish-test
publish-test: ## publish a release to pypi.
	@echo "🚀 Publishing: Dry run."
	@poetry publish -r test-pypi --dry-run
	@echo "🚀 Publishing."
	@poetry publish -r test-pypi

.PHONY: build-and-publish
build-and-publish: build publish ## Build and publish.

.PHONY: docs
docs: ## Build and serve the documentation
	@poetry run mkdocs serve

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
