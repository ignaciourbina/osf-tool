# osf-tool — Technical Specification

## 1. Purpose

Structured, type-safe Python API for parsing, inspecting, editing, versioning, and
regenerating OSF Preregistration documents stored as `.docx` files. Templated from
the `irb-tool` architecture, adapted to the OSF Preregistration form structure.

## 2. Source Document Analysis

**File:** `OSF Preregistration.docx` (canonical OSF template)

| Metric | Value |
|--------|-------|
| Total paragraphs | 217 |
| Heading 1 (major sections) | 7 |
| Heading 3 (question fields) | 29 |
| Tables (1x1 response areas) | 22 |
| Tables (structural/instruction) | 2 |
| Checkboxes (w14:checkbox) | 0 |
| Structured Doc Tags (w:sdt) | 0 |

### 2.1 Document Structure

The OSF form uses a **Heading 1 → Heading 3** hierarchy (no numbered sections):

```
Heading 2: Instructions              (preamble — skip)
Heading 1: Metadata                  (major section)
  Heading 3: Title*                  (question)
    [normal paragraphs: prompt/help text]
    [1x1 table: response entry area]
  Heading 3: Description*
    ...
Heading 1: Study Information
  Heading 3: Hypotheses*
    ...
Heading 1: Design Plan
  Heading 3: Study type*
    [normal paragraphs: radio options listed inline]
  Heading 3: Blinding*
    [normal paragraphs: multi-select options listed inline]
  ...
```

### 2.2 Response Entry Mechanism

Unlike the IRB protocol (which uses "Block Text" paragraphs and `w14:checkbox` XML),
the OSF form uses **1x1 tables** as text entry areas. Researchers type their
responses inside the single cell of a 1x1 table.

### 2.3 Response Types

| Type | Count | Mechanism | Examples |
|------|-------|-----------|----------|
| `FREE_TEXT` | 22 | 1x1 table cell | Title, Description, Hypotheses, Study design, ... |
| `RADIO` | 3 | Options listed as normal paragraphs before table | License (15 options), Study type (4 options), Existing data (5 options) |
| `MULTI_SELECT` | 1 | Options listed as normal paragraphs | Blinding (4 options) |
| `TAG_LIST` | 2 | Free-text comma-separated | Subject, Tags |
| `CONTRIBUTOR_LIST` | 1 | Free-text structured | Contributors |

For the programmatic model, RADIO and MULTI_SELECT selections are stored as
metadata alongside the response. The docx itself has no checkbox XML — selections
are tracked in the JSON serialization and written back as bold/marked text.

**Simplified to 3 canonical types for v1:**

| ResponseType | Input | Description |
|---|---|---|
| `FREE_TEXT` | `str` | Open text entry (covers TAG_LIST, CONTRIBUTOR_LIST) |
| `RADIO` | `str` | One selected option from a known set |
| `MULTI_SELECT` | `dict[str, bool]` | Multiple options, each on/off |

## 3. Data Model

### 3.1 Section Hierarchy

```
OSFSection (major)          → keyed by slug: "metadata", "study_information", ...
  OSFField (question)       → keyed by slug: "title", "hypotheses", "study_type", ...
```

Slugs are derived from Heading text: `"Study design*"` → `"study_design"`.

### 3.2 Core Classes

```python
class ResponseType(Enum):
    FREE_TEXT     = "free_text"
    RADIO         = "radio"
    MULTI_SELECT  = "multi_select"

@dataclass
class FreeTextResponse:
    text: str

@dataclass
class RadioResponse:
    selected: str | None          # label of selected option, or None
    options: list[str]            # all available options

@dataclass
class MultiSelectResponse:
    selections: dict[str, bool]   # label → checked

Response = FreeTextResponse | RadioResponse | MultiSelectResponse

@dataclass
class OSFField:
    slug: str                     # "hypotheses", "study_type"
    title: str                    # "Hypotheses*"
    required: bool                # True if title ends with *
    section_slug: str             # parent section slug
    prompt_text: str              # concatenated help/example text
    response_type: ResponseType
    response: Response
    table_index: int | None       # index into doc.tables for write-back
    para_indices: list[int]       # paragraph indices (heading + prompt paras)
    dirty: bool = False

@dataclass
class OSFSection:
    slug: str                     # "design_plan"
    title: str                    # "Design Plan"
    fields: OrderedDict[str, OSFField]
    para_index: int               # paragraph index of Heading 1

@dataclass
class OSFFormMetadata:
    template_name: str            # "OSF Preregistration"
    source_path: str | None

class OSFPreregistration:
    metadata: OSFFormMetadata
    sections: OrderedDict[str, OSFSection]
    source_path: str | None

    # Query
    get_field(slug: str) -> OSFField
    get_field(section_slug: str, field_slug: str) -> OSFField
    all_fields() -> list[OSFField]
    required_fields() -> list[OSFField]
    summary() -> dict

    # Edit (type-checked)
    edit_field(slug: str, value) -> None

    # Compare
    diff(other: OSFPreregistration) -> list[FieldDiff]

    # Serialize
    to_dict() -> dict
    to_markdown() -> str
    @classmethod from_dict(d) -> OSFPreregistration
```

### 3.3 Type Protection

| Field's ResponseType | Accepted input to `edit_field()` | Rejected |
|---|---|---|
| `FREE_TEXT` | `str` | dict, list, int |
| `RADIO` | `str` (must be in options list) | dict, unknown option |
| `MULTI_SELECT` | `dict[str, bool]` (keys must be known) | str, list |

## 4. Module Architecture

```
osf-tool/
├── osf_workflow/
│   ├── __init__.py          # Public API re-exports
│   ├── schema.py            # Data model (OSFPreregistration, OSFField, ResponseType, ...)
│   ├── parser.py            # DOCX → OSFPreregistration
│   ├── writer.py            # OSFPreregistration → DOCX (surgical write-back)
│   └── versioning.py        # JSON snapshot save/load/diff
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures (parsed form, tmp dirs)
│   ├── test_parser.py       # Parsing correctness
│   ├── test_schema.py       # Type protection, edit validation
│   ├── test_writer.py       # Write-back round-trip
│   └── test_versioning.py   # Snapshot save/load/diff
├── TECH_SPEC.md             # This file
├── requirements.txt
└── Makefile
```

## 5. Parser Pipeline

### Step 1: Walk body XML elements (not just paragraphs)

Unlike `doc.paragraphs` (which skips tables), walk `doc.element.body` children
to track both `w:p` (paragraph) and `w:tbl` (table) elements in document order.

### Step 2: Identify section boundaries

- `Heading 1` → new `OSFSection`
- `Heading 3` → new `OSFField` under current section
- Skip `Heading 2` (instructions preamble)

### Step 3: Collect prompt text

All `normal`-style paragraphs between a `Heading 3` and the next heading/table
form the field's `prompt_text`.

### Step 4: Classify response type

Use `FIELD_TYPE_OVERRIDES` dict for known radio/multi-select fields:

```python
FIELD_TYPE_OVERRIDES = {
    "license":       ResponseType.RADIO,
    "study_type":    ResponseType.RADIO,
    "existing_data": ResponseType.RADIO,
    "blinding":      ResponseType.MULTI_SELECT,
}
```

Everything else defaults to `FREE_TEXT`.

### Step 5: Extract radio/multi-select options

For RADIO and MULTI_SELECT fields, options are the normal-style paragraphs
between the descriptive prompt and the next heading/table. These are identified
by their position and content pattern (short, no "Example:" prefix).

### Step 6: Link tables to fields

Walk the body elements. When a `w:tbl` (1x1) is encountered, link it to the
most recent `OSFField`. Store `table_index` for write-back.

### Step 7: Read existing responses

If table cell is non-empty, populate `FreeTextResponse.text`.
For RADIO/MULTI_SELECT, responses remain `None`/all-false in the blank template.

## 6. Writer Pipeline

### Preservation-First Strategy (same as irb-tool)

1. Open original DOCX with `python-docx`
2. For each field where `dirty=True`:
   - **FREE_TEXT**: locate `doc.tables[table_index]`, set cell text
   - **RADIO**: write selected option label into the table cell (and optionally
     bold the matching option paragraph)
   - **MULTI_SELECT**: write comma-separated selected labels into table cell
3. Save to new file — all non-modified content is byte-identical

### Table Cell Write-Back

```python
def _set_table_cell_text(table, text: str) -> None:
    cell = table.rows[0].cells[0]
    # Clear existing paragraphs, set text on first paragraph
    # Preserve cell formatting (borders, shading)
```

## 7. Versioning (cloned from irb-tool)

Identical pattern:
- `VersionManager(versions_dir)`
- `.save(form, label, notes)` → JSON snapshot
- `.load(label)` → `OSFPreregistration`
- `.diff(label_a, label_b)` → `list[FieldDiff]`

## 8. Field Inventory

### Metadata (5 fields)
| # | Field | Slug | Required | Type |
|---|-------|------|----------|------|
| 1 | Title | `title` | yes | FREE_TEXT |
| 2 | Description | `description` | yes | FREE_TEXT |
| 3 | Contributors | `contributors` | yes | FREE_TEXT |
| 4 | License | `license` | yes | RADIO (15 options) |
| 5 | Subject | `subject` | yes | FREE_TEXT |
| 6 | Tags | `tags` | no | FREE_TEXT |

### Study Information (1 field)
| # | Field | Slug | Required | Type |
|---|-------|------|----------|------|
| 7 | Hypotheses | `hypotheses` | yes | FREE_TEXT |

### Design Plan (5 fields)
| # | Field | Slug | Required | Type |
|---|-------|------|----------|------|
| 8 | Study type | `study_type` | yes | RADIO (4 options) |
| 9 | Blinding | `blinding` | yes | MULTI_SELECT (4 options) |
| 10 | Is there any additional blinding... | `additional_blinding` | no | FREE_TEXT |
| 11 | Study design | `study_design` | yes | FREE_TEXT |
| 12 | Randomization | `randomization` | no | FREE_TEXT |

### Sampling Plan (6 fields)
| # | Field | Slug | Required | Type |
|---|-------|------|----------|------|
| 13 | Existing data | `existing_data` | yes | RADIO (5 options) |
| 14 | Explanation of existing data | `explanation_existing_data` | no | FREE_TEXT |
| 15 | Data collection procedures | `data_collection_procedures` | yes | FREE_TEXT |
| 16 | Sample size | `sample_size` | yes | FREE_TEXT |
| 17 | Sample size rationale | `sample_size_rationale` | no | FREE_TEXT |
| 18 | Stopping rule | `stopping_rule` | no | FREE_TEXT |

### Variables (3 fields)
| # | Field | Slug | Required | Type |
|---|-------|------|----------|------|
| 19 | Manipulated variables | `manipulated_variables` | no | FREE_TEXT |
| 20 | Measured variables | `measured_variables` | yes | FREE_TEXT |
| 21 | Indices | `indices` | no | FREE_TEXT |

### Analysis Plan (6 fields)
| # | Field | Slug | Required | Type |
|---|-------|------|----------|------|
| 22 | Statistical models | `statistical_models` | yes | FREE_TEXT |
| 23 | Transformations | `transformations` | no | FREE_TEXT |
| 24 | Inference criteria | `inference_criteria` | no | FREE_TEXT |
| 25 | Data exclusion | `data_exclusion` | no | FREE_TEXT |
| 26 | Missing data | `missing_data` | no | FREE_TEXT |
| 27 | Exploratory analysis | `exploratory_analysis` | no | FREE_TEXT |

### Other (1 field)
| # | Field | Slug | Required | Type |
|---|-------|------|----------|------|
| 28 | Other | `other` | no | FREE_TEXT |

**Total: 28 fields** (14 required, 14 optional)

## 9. Dependencies

```
python-docx >= 1.2.0
lxml >= 5.3.0
pytest >= 8.0.0    # dev
```

No `docxtpl` needed (no template rendering — surgical edits only).

## 10. Key Differences from irb-tool

| Aspect | irb-tool | osf-tool |
|--------|----------|----------|
| Section addressing | Numbered (`3.1`, `14.5`) | Slug-based (`hypotheses`, `study_type`) |
| Response areas | "Block Text" paragraphs | 1x1 tables |
| Checkbox mechanism | `w14:checkbox` XML elements | None (radio/multi-select as text) |
| Nodes | 105 | 28 |
| Preamble extraction | Title, Version, PI from markers | Template name only |
| Section type overrides | 17 hardcoded | 4 hardcoded |
| Write-back target | Paragraph runs | Table cells |
