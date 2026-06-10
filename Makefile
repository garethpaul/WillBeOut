PYTHON ?= python3
PYTHON2 ?= python2
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
CHECK_SCRIPT := $(ROOT)/scripts/check_willbeout_contracts.py
PYTHON_FILES := $(addprefix $(ROOT)/,__init__.py attendees.py auth.py base.py cal.py events.py facebook.py ismobile.py messages.py mobile.py prettydate.py votes.py)

.PHONY: clean lint test build verify check

clean:
	find "$(ROOT)" -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	find "$(ROOT)" -type d -name '__pycache__' -prune -exec rm -rf {} +

lint:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m py_compile "$(CHECK_SCRIPT)"

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(CHECK_SCRIPT)"
	@if command -v $(PYTHON2) >/dev/null 2>&1; then \
		$(PYTHON2) -m py_compile $(PYTHON_FILES); \
	else \
		echo "Skipping legacy Python 2 syntax checks: python2 is not installed."; \
	fi

build: lint

verify: lint test build

check: clean verify
	$(MAKE) -f "$(ROOT)/Makefile" clean
