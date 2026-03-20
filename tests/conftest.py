"""Shared test fixtures."""

import sys
from pathlib import Path

import pytest

# Ensure osf_workflow is importable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from osf_workflow import parse_osf_form

# Path to the canonical OSF Preregistration .docx
OSF_DOCX = ROOT.parent / "OSF Preregistration.docx"


@pytest.fixture
def osf_docx_path() -> Path:
    if not OSF_DOCX.exists():
        pytest.skip(f"OSF docx not found at {OSF_DOCX}")
    return OSF_DOCX


@pytest.fixture
def parsed_form(osf_docx_path):
    return parse_osf_form(osf_docx_path)
