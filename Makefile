ROOT     := ../../..
VENV     := $(ROOT)/venv
REQS     := $(ROOT)/requirements.txt
PYTHON   := $(VENV)/bin/python
PIP      := $(VENV)/bin/pip
PYTEST   := $(VENV)/bin/pytest
OSF_DOCX := ../OSF\ Preregistration.docx

.PHONY: venv install test parse fill clean

venv:
	python3 -m venv $(VENV)

install: venv
	$(PIP) install -r $(REQS)

test: install
	$(PYTEST) tests/ -v

parse: install
	$(PYTHON) -c "from osf_workflow import parse_osf_form; f = parse_osf_form('$(OSF_DOCX)'); print(f.summary()); print(f.to_markdown()[:2000])"

fill: install
	$(PYTHON) scripts/fill_pap_draft.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null; true
