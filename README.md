# osf-tool

Python toolkit for parsing, editing, versioning, and regenerating OSF Pre-registration forms stored as `.docx` files.

## What it does

- Parses OSF pre-registration `.docx` files into structured data (questions, response types, current answers).
- Edits responses programmatically with type-safe write-back that preserves the original document formatting.
- Versions completed forms with digest-based snapshots for audit trails.
- Supports three response types: free text, radio (single select), and multi-select checkboxes.

## Structure

```
osf_workflow/
  parser.py       # Reads .docx, extracts questions and responses
  writer.py       # Surgical write-back into .docx (preservation-first)
  schema.py       # ResponseType enum, field inventory, type contracts
  versioning.py   # Digest-based versioning (cloned from irb-tool pattern)
```

## Usage

```python
from osf_workflow.parser import parse_preregistration
from osf_workflow.writer import update_response

questions = parse_preregistration("my_prereg.docx")
update_response("my_prereg.docx", field_id="study_design", value="Between-subjects experiment")
```

The toolkit maps all 28 fields of the OSF Preregistration template to their response types and section locations.

## Used in

- Pre-analysis plan for "Trait Aggression and Voting for the Far-Right" (Sgorlon and Urbina)
- Registration packet for "Communication and Cooperation with Human and Artificial Agents" (Urbina, Kline, and Ponda)

## Requirements

- Python 3.11+
- python-docx
