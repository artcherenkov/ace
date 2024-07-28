VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PIP_COMPILE := $(VENV)/bin/pip-compile
UVICORN := $(VENV)/bin/uvicorn

.PHONY: venv install update-requirements run

venv:
	python3 -m venv $(VENV)

install: venv
	$(PIP) install -r requirements.txt

update-requirements: install
	$(PIP) freeze > requirements.txt

run:
	$(UVICORN) src.main:app --reload
