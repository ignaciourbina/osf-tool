# osf-tool

Standalone Python toolkit for two adjacent OSF workflows:

- `osf_workflow/`: parse, edit, version, and regenerate OSF preregistration `.docx` files.
- `osf_api_cli/`: research-grade OSF API client and CLI for projects, files, draft registrations, and registrations.

## Components

### `osf_workflow`

The document workflow preserves the existing OSF preregistration form structure while letting you:

- parse a `.docx` preregistration into structured fields
- edit responses programmatically with type checks
- write an updated `.docx`
- snapshot versions and diff field-level changes

### `osf_api_cli`

The API layer provides:

- authenticated OSF API access with normalized errors
- typed resource models for users, projects, files, drafts, registrations, contributors, and schemas
- nested CLI commands for discovery and export
- draft inspection by draft ID
- project inspection/export across contributors, files, drafts, and registrations
- draft field updates via JSON payloads

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Optional editable install:

```bash
.venv/bin/pip install -e .
```

## Authentication

The CLI resolves credentials in this order:

1. `--token`
2. `OSF_TOKEN`
3. profile token in `~/.config/osf-tool/config.toml`
4. legacy `osf-credentials.txt`

Example config:

```toml
default_profile = "default"

[profiles.default]
token = "your-osf-token"
timeout = 30
```

## CLI Usage

```bash
python -m osf_api_cli auth check
python -m osf_api_cli project list
python -m osf_api_cli project inspect vseu4 --json
python -m osf_api_cli draft inspect 69d02feb810dc0832d7a8507 --dest draft.json --json
python -m osf_api_cli draft update-metadata 69d02feb810dc0832d7a8507 fields.json --json
```

If installed via `pip -e .`, the console scripts are:

```bash
osf auth check
osf-api auth check
```

## Document Workflow Usage

```python
from osf_workflow import parse_osf_form, write_osf_form_to_docx

form = parse_osf_form("OSF Preregistration.docx")
form.edit_field("hypotheses", "Trait aggression predicts far-right vote choice.")
write_osf_form_to_docx(form, "updated_preregistration.docx")
```

## Repo Layout

```text
osf_api_cli/
osf_workflow/
scripts/
tests/
versions/
TECH_SPEC.md
requirements.txt
```
