PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python

.PHONY: venv format format-check lint typecheck test coverage shell-test package package-check verify clean

venv: $(VENV)/.deps

$(VENV)/bin/python:
	$(PYTHON) -m venv $(VENV)

$(VENV)/.deps: requirements-dev.txt pyproject.toml | $(VENV)/bin/python
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements-dev.txt
	$(VENV_PYTHON) -m pip install --no-build-isolation --no-deps -e .
	touch $(VENV)/.deps

test: venv
	$(VENV_PYTHON) -m pytest

format: venv
	$(VENV_PYTHON) -m isort src tests
	$(VENV_PYTHON) -m black src tests

format-check: venv
	$(VENV_PYTHON) -m isort --check-only --diff src tests
	$(VENV_PYTHON) -m black --check src tests

lint: venv format-check
	$(VENV_PYTHON) -m pylint src tests

typecheck: venv
	$(VENV_PYTHON) -m mypy

coverage: venv
	$(VENV_PYTHON) -m pytest --cov --cov-report=term-missing

shell-test:
	bash tests/install_test.sh

package: venv
	rm -rf dist build src/*.egg-info
	$(VENV_PYTHON) -m build

package-check: package
	$(VENV_PYTHON) -m twine check dist/*

verify: venv lint typecheck coverage package-check
	bash -n install.sh
	bash -n tests/install_test.sh
	PYTHONPYCACHEPREFIX=/tmp/llm-wiki-pycache $(VENV_PYTHON) -m compileall -q src
	$(VENV_PYTHON) -m pytest
	bash tests/install_test.sh

clean:
	rm -rf .coverage .mypy_cache .pytest_cache .ruff_cache .venv build dist htmlcov src/*.egg-info /private/tmp/llm-wiki-pycache
	find src tests -name __pycache__ -type d -prune -exec rm -rf {} +
