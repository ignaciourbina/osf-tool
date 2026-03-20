"""osf_workflow — Structured API for OSF Preregistration .docx documents."""

from .schema import (
    ResponseType,
    FreeTextResponse,
    RadioResponse,
    MultiSelectResponse,
    OSFField,
    OSFSection,
    OSFFormMetadata,
    OSFPreregistration,
    FieldDiff,
    response_from_dict,
)
from .parser import parse_osf_form
from .writer import write_osf_form_to_docx
from .versioning import VersionManager

__all__ = [
    "ResponseType",
    "FreeTextResponse",
    "RadioResponse",
    "MultiSelectResponse",
    "OSFField",
    "OSFSection",
    "OSFFormMetadata",
    "OSFPreregistration",
    "FieldDiff",
    "response_from_dict",
    "parse_osf_form",
    "write_osf_form_to_docx",
    "VersionManager",
]
