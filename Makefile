PYTHON ?= python3
override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
CHECK_SCRIPT := $(ROOT)/scripts/check_willbeout_contracts.py
WORKFLOW_CONTRACT_SCRIPT := $(ROOT)/scripts/test_workflow_contract.py
PYTHON_FILES := $(addprefix $(ROOT)/,__init__.py attendees.py auth.py base.py cal.py database.py events.py facebook.py facebook_client.py messages.py mobile.py prettydate.py session.py votes.py)

.PHONY: clean lint test contract-test build verify check

clean:
	find "$(ROOT)" -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	find "$(ROOT)" -type d -name '__pycache__' -prune -exec rm -rf {} +

lint:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m py_compile "$(CHECK_SCRIPT)" $(PYTHON_FILES)

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(CHECK_SCRIPT)"
	cd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v test_modern_runtime.py

contract-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(WORKFLOW_CONTRACT_SCRIPT)"

build: lint

verify: lint test contract-test build

check: clean verify
	$(MAKE) -f "$(ROOT)/Makefile" clean
