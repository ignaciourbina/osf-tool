# osf-tool - Technical Specification

## 1. Purpose

Structured Python API for parsing, inspecting, editing, versioning, and regenerating OSF Preregistration documents stored as `.docx` files. This package borrows the `irb-tool` workflow pattern, but the OSF template uses a different form structure.

## 2. Source Document Analysis

**File:** `OSF Preregistration.docx`

| Metric | Value |
|--------|-------|
| Total paragraphs | 217 |
| Heading 1 sections | 7 |
| Heading 3 headings | 29 |
| Parsed fields | 28 |
| Tables | 24 |
| Response tables (1x1) | 22 |
| Structural/instruction tables | 2 |
| Checkboxes (`w14:checkbox`) | 0 |
| Structured Doc Tags (`w:sdt`) | 0 |

### 2.1 Document Structure

The OSF form uses a `Heading 1 -> Heading 3` hierarchy. The parser skips the instruction preamble and ignores the blank `Heading 3` that appears after `License`.

```text
Heading 2: Instructions              (preamble - skip)
Heading 1: Metadata                  (major section)
  Heading 3: Title*                  (field)
    [normal paragraphs: prompt/help text]
    [1x1 table: response entry area]
  Heading 3: Description*
    ...
Heading 1: Study Information
  Heading 3: Hypotheses*
    ...
Heading 1: Design Plan
  Heading 3: Study type*
    [normal paragraphs: option text + prompt/help]
    [1x1 table: response entry area]
```

### 2.2 Response Entry Mechanism

Unlike the IRB protocol, the OSF form uses 1x1 tables as text entry areas. The parser and writer operate on table cells, not checkbox XML or content controls.

### 2.3 Response Types

The current model has three canonical response types:

| ResponseType | Count | Mechanism | Notes |
|---|---:|---|---|
| `FREE_TEXT` | 24 | 1x1 table cell | Includes `title`, `description`, `contributors`, `subject`, `tags`, and the other free-text fields |
| `RADIO` | 3 | Plain-text label written to the response cell | `license`, `study_type`, `existing_data` |
| `MULTI_SELECT` | 1 | Newline-separated labels written to the response cell | `blinding` |

`subject`, `tags`, and `contributors` are treated as plain free-text fields in this implementation. There are no dedicated `TAG_LIST` or `CONTRIBUTOR_LIST` response classes.

## 3. Data Model

### 3.1 Section Hierarchy

```text
OSFSection (major section) -> keyed by slug: "metadata", "study_information", ...
  OSFField (question)      -> keyed by slug: "title", "hypotheses", "study_type", ...
```

Slugs are derived from heading text with `_slugify()`, plus a small set of parser overrides for awkward headings such as `Inference criteria ` and `Existing data*`.

### 3.2 Core Classes

```python
class ResponseType(Enum):
    FREE_TEXT = "free_text"
    RADIO = "radio"
    MULTI_SELECT = "multi_select"

@dataclass
class FreeTextResponse:
    text: str

@dataclass
class RadioResponse:
    selected: str | None
    options: list[str]

@dataclass
class MultiSelectResponse:
    selections: dict[str, bool]

Response = FreeTextResponse | RadioResponse | MultiSelectResponse

@dataclass
class OSFField:
    slug: str
    title: str
    required: bool
    section_slug: str
    prompt_text: str
    response_type: ResponseType
    response: Response
    table_index: int | None
    para_indices: list[int]
    dirty: bool = False

@dataclass
class OSFSection:
    slug: str
    title: str
    fields: OrderedDict[str, OSFField]
    para_index: int

@dataclass
class OSFFormMetadata:
    template_name: str = "OSF Preregistration"
    source_path: str | None = None

class OSFPreregistration:
    metadata: OSFFormMetadata
    sections: OrderedDict[str, OSFSection]
    source_path: str | None

    # Query
    get_field(slug: str) -> OSFField
    all_fields() -> list[OSFField]
    required_fields() -> list[OSFField]
    section_names() -> list[str]
    summary() -> dict

    # Edit
    edit_field(slug: str, value) -> None

    # Compare
    diff(other: OSFPreregistration) -> list[FieldDiff]

    # Serialize
    to_dict() -> dict
    to_markdown() -> str
    @classmethod
    from_dict(d) -> OSFPreregistration
```

### 3.3 Type Protection

| Field response type | Accepted input to `edit_field()` | Rejected |
|---|---|---|
| `FREE_TEXT` | `str` | dict, list, int |
| `RADIO` | `str` that matches one of the known options | dict, unknown option |
| `MULTI_SELECT` | `dict[str, bool]` using known option labels | str, list, unknown label |

## 4. Module Architecture

```text
osf-tool/
├── doc/
│   └── TECH_SPEC.md
├── osf_workflow/
│   ├── __init__.py          # Public API re-exports
│   ├── schema.py            # Data model (OSFPreregistration, OSFField, ResponseType, ...)
│   ├── parser.py            # DOCX -> OSFPreregistration
│   ├── writer.py            # OSFPreregistration -> DOCX
│   └── versioning.py        # JSON snapshot save/load/diff
├── output/
├── scripts/
│   └── fill_pap_draft.py
├── tests/
│   ├── conftest.py
│   ├── test_parser.py
│   ├── test_schema.py
│   ├── test_writer.py
│   └── test_versioning.py
├── versions/
├── Makefile
└── requirements.txt
```

## 5. Parser Pipeline

### Step 1: Walk body XML elements

The parser walks `doc.element.body` so it can see paragraphs and tables in document order.

### Step 2: Identify section boundaries

- `Heading 1` starts a new `OSFSection`
- `Heading 3` starts a new `OSFField`
- `Heading 2` is the instruction preamble and is skipped

### Step 3: Collect prompt text

Normal paragraphs between the field heading and the response table are concatenated into `prompt_text`.

### Step 4: Classify response type

`FIELD_TYPE_OVERRIDES` currently hard-codes four non-default fields:

```python
FIELD_TYPE_OVERRIDES = {
    "license": ResponseType.RADIO,
    "study_type": ResponseType.RADIO,
    "existing_data": ResponseType.RADIO,
    "blinding": ResponseType.MULTI_SELECT,
}
```

Everything else defaults to `FREE_TEXT`.

### Step 5: Populate canonical option sets

Radio and multi-select fields do not infer options from nearby paragraphs. A second pass assigns the canonical option lists from hard-coded slug-specific tables in `parser.py`.

### Step 6: Link tables to fields

When the parser encounters a 1x1 table, it stores the corresponding `table_index` on the current field.

### Step 7: Read existing responses

If a 1x1 table already contains text, the parser loads it into `FreeTextResponse.text`. Radio and multi-select fields are initialized empty and remain unselected in the parsed model.

## 6. Writer Pipeline

### Preservation-First Strategy

1. Open the original DOCX with `python-docx`
2. For each field where `dirty=True`:
   - `FREE_TEXT`: write the string into the linked response cell
   - `RADIO`: write the selected label into the linked response cell
   - `MULTI_SELECT`: write the selected labels joined by newlines into the linked response cell
3. Save to a new file

The implementation preserves document structure and unchanged content semantically, but it does not guarantee byte-identical output because `python-docx` rewrites the package on save.

### Table Cell Write-Back

```python
def _set_table_cell_text(table, text: str) -> None:
    cell = table.rows[0].cells[0]
    # Replace cell text while preserving the first paragraph's formatting
```

## 7. Versioning

The versioning layer is a thin JSON snapshot wrapper:

- `VersionManager(versions_dir)`
- `.save(form, label, notes="") -> VersionRecord`
- `.load(label) -> OSFPreregistration`
- `.list_versions() -> list[VersionRecord]`
- `.diff(label_a, label_b) -> list[FieldDiff]`

Snapshots are stored as `<label>.json` files under `versions/`.

## 8. Field Inventory

### Metadata (6 fields)

| # | Field | Slug | Required | Type |
|---|-------|------|----------|------|
| 1 | Title | `title` | yes | FREE_TEXT |
| 2 | Description | `description` | yes | FREE_TEXT |
| 3 | Contributors | `contributors` | yes | FREE_TEXT |
| 4 | License | `license` | yes | RADIO (17 options) |
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
| 10 | Is there any additional blinding in this study? | `additional_blinding` | no | FREE_TEXT |
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

```text
python-docx >= 1.2.0
lxml >= 5.3.0
pytest >= 8.0.0    # dev
```

No `docxtpl` is needed because the implementation performs surgical edits rather than template rendering.

## 10. Key Differences from irb-tool

| Aspect | irb-tool | osf-tool |
|--------|----------|----------|
| Section addressing | Numbered (`3.1`, `14.5`) | Slug-based (`hypotheses`, `study_type`) |
| Response areas | "Block Text" paragraphs | 1x1 tables |
| Checkbox mechanism | `w14:checkbox` XML elements | None |
| Parsed fields | 105 | 28 |
| Preamble extraction | Title, Version, PI from markers | Template name only |
| Section type overrides | 17 hardcoded | 4 hardcoded |
| Write-back target | Paragraph runs | Table cells |
