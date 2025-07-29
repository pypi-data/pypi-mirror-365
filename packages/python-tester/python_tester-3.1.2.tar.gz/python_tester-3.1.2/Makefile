#!/usr/bin/env make -f
#
# Makefile for recipe static site generator
#

# ---------------------------------------------------------------------------
#
# General setup
#

# Set default target
.DEFAULT_GOAL := test

# Decide if use python3 or python
ifeq (, $(@shell which python3))
	py = "uv run python3"
else
	py = python
endif
# Decide if use pip3 or pip
ifeq (, $(@shell which pip3))
	pip = pip3
else
	pip = pip
endif
# Decide if use firefox or firefox.exe
ifeq (, $(@shell which firefox.exe))
	browser = firefox.exe
else
	browser = firefox
endif


# Detect OS
OS = $(shell uname -s)

# Defaults
ECHO = echo

# Make adjustments based on OS
ifneq (, $(findstring CYGWIN, $(OS)))
	ECHO = /bin/echo -e
endif

# Colors and helptext
NO_COLOR	= \033[0m
ACTION		= \033[32;01m
OK_COLOR	= \033[32;01m
ERROR_COLOR	= \033[31;01m
WARN_COLOR	= \033[33;01m

# Which makefile am I in?
WHERE-AM-I = $(CURDIR)/$(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))
THIS_MAKEFILE := $(call WHERE-AM-I)

# Echo some nice helptext based on the target comment
HELPTEXT = $(ECHO) "$(ACTION)--->" `egrep "^\# target: $(1) " $(THIS_MAKEFILE) | sed "s/\# target: $(1)[ ]*-[ ]* / /g"` "$(NO_COLOR)"



# ----------------------------------------------------------------------------
#
# Highlevel targets
#
# target: help                         - Displays help with targets available.
.PHONY:  help
help:
	@$(call HELPTEXT,$@)
	@echo "Usage:"
	@echo " make [target] ..."
	@echo "target:"
	@egrep "^# target:" Makefile | sed 's/# target: / /g'



# target: build                     - Build and package code. Result in build/ folder.
.PHONY: build
build: clean
	uv build



# target: info                         - Displays versions.
.PHONY: info
info:
	uv run python3 --version
	uv run python3 -m pip --version
#@virtualenv --version



# target: validate                     - Validate code with pylint
.PHONY: validate
validate:
	uv run pylint --rcfile=.pylintrc src/tester



# target: test-unit                    - Run tests in tests/unit with coverage.py
.PHONY: test-unit
test-unit: clean
	@$(ECHO) "$(ACTION)---> Running all tests in tests/" "$(NO_COLOR)"
	uv run python3 -m coverage run --rcfile=.coveragerc -m unittest discover -b test

	$(MAKE) clean-py



# target: test                         - Run code validation, tests and display code coverage
.PHONY: test
test: validate test-unit
	uv run python3 -m coverage report  --rcfile=.coveragerc
	$(MAKE) clean-cov



# target: tox                         - Run "test" command for python version >=3.5
.PHONY: tox
tox:
	uv run tox

# target: publish                     - Run "uv publish" with .env file
.PHONY: publish
publish:
	uvx --env-file .env uv publish dist/*

## target: clean-py                     - Remove generated python files
.PHONY: clean-py
clean-py:
	-find . -name '*.pyc' -exec rm -f {} +
	-find . -name '*.pyo' -exec rm -f {} +
	-find . -name '__pycache__' -exec rm -fr {} +
	-find . -name '.pytest_cache' -exec rm -fr {} +
	-find dist/ -name '*.whl' -exec rm -fr {} + 2>/dev/null
	-find dist/ -name '*.tar.gz' -exec rm -fr {} + 2>/dev/null



## target: clean-cov                    - Remove generated coverage files
.PHONY: clean-cov
clean-cov:
	rm -f .coverage
	rm -rf tests/coverage_html



# target: clean                        - Remove all generated files
.PHONY: clean
clean: clean-py clean-cov
	find . -name '*~' -exec rm -f {} +
	find . -name '*.log*' -exec rm -fr {} +



# target: install                      - Install all Python packages specified in requirement.txt
.PHONY: install
install:
	${pip} install -r requirements.txt



# target: install-dev                      - Install all Python packages specified in devrequirement.txt
.PHONY: install-dev
install-dev:
	${pip} install -r devrequirements.txt
