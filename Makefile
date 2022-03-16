INTERPRETER := python

.DEFAULT_GOAL := run

run:
	$(INTERPRETER) -m manx
.PHONY: run

format:
	black manx tests
.PHONY: format

types: format
	mypy manx
.PHONY: types

test: types
	pytest tests
.PHONY: test

setup:
	$(INTERPRETER) -m pip install --upgrade pip
.PHONY: setup

install: setup
	$(INTERPRETER) -m pip install -e ".[dev]"
.PHONY: install
