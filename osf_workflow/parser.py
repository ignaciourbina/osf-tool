"""Parser: DOCX → OSFPreregistration.

Walks the document body XML to track both paragraphs and tables in document
order, building a structured OSFPreregistration from the heading hierarchy
and 1x1 response tables.
"""

from __future__ import annotations

import re
from collections import OrderedDict
from pathlib import Path
from typing import Union

from docx import Document

from .schema import (
    FreeTextResponse,
    MultiSelectResponse,
    OSFField,
    OSFFormMetadata,
    OSFPreregistration,
    OSFSection,
    RadioResponse,
    ResponseType,
    _slugify,
)

# ── Constants ───────────────────────────────────────────────────────────

NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

FIELD_TYPE_OVERRIDES: dict[str, ResponseType] = {
    "license": ResponseType.RADIO,
    "study_type": ResponseType.RADIO,
    "existing_data": ResponseType.RADIO,
    "blinding": ResponseType.MULTI_SELECT,
}

# Slug overrides for headings whose auto-slug would be ambiguous or ugly.
SLUG_OVERRIDES: dict[str, str] = {
    "Is there any additional blinding in this study?": "additional_blinding",
    "Explanation of existing data": "explanation_existing_data",
    "Data collection procedures*": "data_collection_procedures",
    "Sample size rationale": "sample_size_rationale",
    "Manipulated variables": "manipulated_variables",
    "Measured variables *": "measured_variables",
    "Statistical models *": "statistical_models",
    "Inference criteria": "inference_criteria",  # trailing space in docx
    "Inference criteria ": "inference_criteria",
    "Data exclusion": "data_exclusion",
    "Missing data": "missing_data",
    "Exploratory analysis": "exploratory_analysis",
    "Existing data*": "existing_data",
}

# Paragraphs whose text starts with these are radio/multi-select OPTIONS
# (not prompt text). Used to separate options from prompt paragraphs.
_OPTION_STOP_PREFIXES = ("Example:", "More info:", "More information:")


# ── Helpers ─────────────────────────────────────────────────────────────


def _get_para_style(para_elem) -> str:
    """Extract the style name from a w:p element."""
    pPr = para_elem.find(f"{{{NS_W}}}pPr")
    if pPr is not None:
        pStyle = pPr.find(f"{{{NS_W}}}pStyle")
        if pStyle is not None:
            return pStyle.get(f"{{{NS_W}}}val", "")
    return ""


def _get_para_text(para_elem) -> str:
    """Extract full text from a w:p element."""
    texts = []
    for t in para_elem.iter(f"{{{NS_W}}}t"):
        if t.text:
            texts.append(t.text)
    return "".join(texts)


def _tag_local(elem) -> str:
    tag = elem.tag
    return tag.split("}")[-1] if "}" in tag else tag


def _heading_level(style_val: str) -> int | None:
    """Return heading level (1, 2, 3) or None."""
    m = re.match(r"Heading(\d+)", style_val) or re.match(r"heading(\d+)", style_val)
    if m:
        return int(m.group(1))
    return None


def _is_option_paragraph(text: str) -> bool:
    """Heuristic: short paragraphs that are selectable options (not prompt/help)."""
    stripped = text.strip()
    if not stripped:
        return False
    for pfx in _OPTION_STOP_PREFIXES:
        if stripped.startswith(pfx):
            return False
    return True


# ── Main parser ─────────────────────────────────────────────────────────


def parse_osf_form(docx_path: Union[str, Path]) -> OSFPreregistration:
    """Parse an OSF Preregistration .docx into a structured OSFPreregistration."""
    docx_path = Path(docx_path)
    doc = Document(str(docx_path))
    body = doc.element.body

    sections: OrderedDict[str, OSFSection] = OrderedDict()
    current_section: OSFSection | None = None
    current_field: OSFField | None = None

    # Collect paragraphs and tables interleaved as (type, index, element)
    para_idx = 0
    table_idx = 0

    # Accumulator for option paragraphs (radio/multi-select)
    option_texts: list[str] = []
    prompt_parts: list[str] = []

    # Track whether we've passed the Instructions preamble
    past_preamble = False

    for child in body:
        local_tag = _tag_local(child)

        if local_tag == "p":
            style = _get_para_style(child)
            text = _get_para_text(child)
            hlevel = _heading_level(style)

            if hlevel == 2:
                # Instructions preamble heading — skip
                para_idx += 1
                continue

            if hlevel == 1:
                # New major section
                past_preamble = True
                _finalize_field(current_field, prompt_parts, option_texts)
                prompt_parts = []
                option_texts = []

                slug = _slugify(text)
                current_section = OSFSection(
                    slug=slug, title=text.strip(), para_index=para_idx
                )
                sections[slug] = current_section
                current_field = None
                para_idx += 1
                continue

            if hlevel == 3 and past_preamble and current_section is not None and text.strip():
                # New field (question) — skip empty headings
                _finalize_field(current_field, prompt_parts, option_texts)
                prompt_parts = []
                option_texts = []

                title = text.strip()
                required = title.endswith("*")
                raw_slug = SLUG_OVERRIDES.get(title, _slugify(title))
                rtype = FIELD_TYPE_OVERRIDES.get(raw_slug, ResponseType.FREE_TEXT)

                current_field = OSFField(
                    slug=raw_slug,
                    title=title,
                    required=required,
                    section_slug=current_section.slug,
                    prompt_text="",
                    response_type=rtype,
                    response=_make_empty_response(rtype),
                    table_index=None,
                    para_indices=[para_idx],
                )
                current_section.fields[raw_slug] = current_field
                para_idx += 1
                continue

            # Normal paragraph — belongs to current field
            if current_field is not None and text.strip():
                current_field.para_indices.append(para_idx)

                if current_field.response_type in (
                    ResponseType.RADIO,
                    ResponseType.MULTI_SELECT,
                ):
                    # Separate prompt from options:
                    # Prompt lines come first (contain "Example:", "More info:", etc.)
                    # Option lines are typically shorter and come between the
                    # description and the examples/more-info.
                    # We use a state machine: once we see example/more-info text,
                    # remaining paragraphs are prompt, not options.
                    prompt_parts.append(text.strip())
                else:
                    prompt_parts.append(text.strip())

            para_idx += 1

        elif local_tag == "tbl":
            # Table element
            rows = child.findall(f"{{{NS_W}}}tr")
            n_rows = len(rows)
            n_cols = 0
            if rows:
                n_cols = len(rows[0].findall(f"{{{NS_W}}}tc"))

            # Only 1x1 tables are response areas (skip the instruction tables)
            if n_rows == 1 and n_cols <= 1 and current_field is not None:
                current_field.table_index = table_idx
                # Read existing cell text
                cell_text = _get_table_cell_text(doc.tables[table_idx])
                if cell_text and current_field.response_type == ResponseType.FREE_TEXT:
                    current_field.response = FreeTextResponse(text=cell_text)

            table_idx += 1

        # Other element types (bookmarkStart, etc.) — skip

    # Finalize last field
    _finalize_field(current_field, prompt_parts, option_texts)

    # Second pass: extract radio/multi-select options from prompt text
    _extract_options_from_prompts(sections)

    metadata = OSFFormMetadata(
        template_name="OSF Preregistration",
        source_path=str(docx_path),
    )

    return OSFPreregistration(
        metadata=metadata,
        sections=sections,
        source_path=str(docx_path),
    )


def _finalize_field(
    field: OSFField | None,
    prompt_parts: list[str],
    option_texts: list[str],
) -> None:
    """Set prompt_text on field from accumulated parts."""
    if field is None:
        return
    field.prompt_text = "\n".join(prompt_parts)


def _make_empty_response(rtype: ResponseType) -> FreeTextResponse | RadioResponse | MultiSelectResponse:
    if rtype == ResponseType.FREE_TEXT:
        return FreeTextResponse(text="")
    if rtype == ResponseType.RADIO:
        return RadioResponse(selected=None, options=[])
    if rtype == ResponseType.MULTI_SELECT:
        return MultiSelectResponse(selections={})
    return FreeTextResponse(text="")


def _get_table_cell_text(table) -> str:
    """Read text from first cell of a table."""
    if not table.rows:
        return ""
    cell = table.rows[0].cells[0]
    return cell.text.strip()


# ── Option extraction (second pass) ────────────────────────────────────

# Known option sets for each radio/multi-select field.
# We define these explicitly because the DOCX mixes options with
# descriptions, examples, and "More info:" blocks in the same paragraph
# sequence, making heuristic extraction fragile.

_RADIO_OPTIONS: dict[str, list[str]] = {
    "license": [
        "No license",
        "GNU Lesser General Public License (LGPL) 3.0",
        'BSD 3-Clause "New"/"Revised" License',
        'BSD 2-Clause "Simplified" License',
        "GNU Lesser General Public License (LGPL) 2.1",
        "CC-By Attribution 4.0 International",
        "Artistic License 2.0",
        "CC0 1.0 Universal",
        "Apache License 2.0",
        "Mozilla Public License 2.0",
        "Academic Free License (AFL) 3.0",
        "Eclipse Public License 1.0",
        "MIT License",
        "GNU General Public License (GPL) 3.0",
        "GNU General Public License (GPL) 2.0",
        "CC-By Attribution-ShareAlike 4.0 International",
        "CC-By Attribution-NonCommercial-NoDerivatives 4.0 International",
    ],
    "study_type": [
        "Experiment - A researcher randomly assigns treatments to study subjects, this includes field or lab experiments. This is also known as an intervention experiment and includes randomized controlled trials.",
        'Observational Study - Data is collected from study subjects that are not randomly assigned to a treatment. This includes surveys, "natural experiments," and regression discontinuity designs.',
        "Meta-Analysis - A systematic review of published studies.",
        "Other",
    ],
    "existing_data": [
        "Registration prior to creation of data: As of the date of submission of this research plan for preregistration, the data have not yet been collected, created, or realized.",
        "Registration prior to any human observation of the data: As of the date of submission, the data exist but have not yet been quantified, constructed, observed, or reported by anyone - including individuals that are not associated with the proposed study. Examples include museum specimens that have not been measured and data that have been collected by non-human collectors and are inaccessible.",
        "Registration prior to accessing the data: As of the date of submission, the data exist, but have not been accessed by you or your collaborators. Commonly, this includes data that has been collected by another researcher or institution.",
        "Registration prior to analysis of the data: As of the date of submission, the data exist and you have accessed it, though no analysis has been conducted related to the research plan (including calculation of summary statistics). A common situation for this scenario when a large dataset exists that is used for many different studies over time, or when a data set is randomly split into a sample for exploratory analyses, and the other section of data is reserved for later confirmatory data analysis.",
        "Registration following analysis of the data: As of the date of submission, you have accessed and analyzed some of the data relevant to the research plan. This includes preliminary analysis of variables, calculation of descriptive statistics, and observation of data distributions. Please see cos.io/prereg for more information.",
    ],
}

_MULTI_SELECT_OPTIONS: dict[str, list[str]] = {
    "blinding": [
        "No blinding is involved in this study.",
        "For studies that involve human subjects, they will not know the treatment group to which they have been assigned.",
        'Personnel who interact directly with the study subjects (either human or non-human subjects) will not be aware of the assigned treatments. (Commonly known as "double blind")',
        "Personnel who analyze the data collected from the study are not aware of the treatment applied to any given group.",
    ],
}


def _extract_options_from_prompts(sections: OrderedDict[str, OSFSection]) -> None:
    """Populate radio/multi-select option lists from the known option sets."""
    for sec in sections.values():
        for fld in sec.fields.values():
            if fld.response_type == ResponseType.RADIO:
                if fld.slug in _RADIO_OPTIONS:
                    fld.response = RadioResponse(
                        selected=None, options=_RADIO_OPTIONS[fld.slug]
                    )

            elif fld.response_type == ResponseType.MULTI_SELECT:
                if fld.slug in _MULTI_SELECT_OPTIONS:
                    fld.response = MultiSelectResponse(
                        selections={
                            opt: False for opt in _MULTI_SELECT_OPTIONS[fld.slug]
                        }
                    )
