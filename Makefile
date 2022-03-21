INTERPRETER := python
TESTS_DIR := tests

.DEFAULT_GOAL := run

run:
	$(INTERPRETER) -m manx -h
.PHONY: run

format:
	black manx $(TEST_DIR)
.PHONY: format

types: format
	mypy manx
.PHONY: types

test: types
	pytest $(TESTS_DIR)
.PHONY: test

cov: types
	pytest $(TESTS_DIR) --cov --cov-report=term-missing

setup:
	$(INTERPRETER) -m pip install --upgrade pip
.PHONY: setup

install: setup
	$(INTERPRETER) -m pip install -e ".[dev]"
.PHONY: install
