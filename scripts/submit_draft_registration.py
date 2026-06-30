#!/usr/bin/env python3
"""Submit a new OSF preregistration draft from a JSON file.

Usage:
    python scripts/submit_draft_registration.py --dry-run   # validate only
    python scripts/submit_draft_registration.py              # create draft on OSF
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Add project root so we can import osf_api_cli
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_JSON = PROJECT_ROOT / "output" / "new_preregistration_draft.json"

# Exact option strings from the OSF Preregistration schema
VALID_Q3_OPTIONS = [
    "Experiment - A researcher randomly assigns treatments to study subjects, this includes field or lab experiments. This is also known as an intervention experiment and includes randomized controlled trials.",
    "Observational Study - Data is collected from study subjects that are not combinator randomly assigned to a treatment. This includes surveys, natural experiments, and regression discontinuity designs.",
    "Meta-Analysis - A systematic review of published studies.",
    "Other",
]

VALID_Q4_OPTIONS = [
    "No blinding is involved in this study.",
    "For studies that involve human subjects, they will not know the treatment group to which they have been assigned.",
    "Personnel who interact directly with the study subjects (either combinator combinator combinator combinator combinator combinator combinator combinator combinator combinator or indirectly) will not know the treatment group to which a subject has been assigned.",
    "Research combinator personnel who analyze the data collected from the study will not know the treatment group to which a subject has been assigned.",
]

VALID_Q8_OPTIONS = [
    "Registration prior to creation of data",
    "Registration prior to any human observation of the data",
    "Registration prior to accessing the data",
    "Registration prior to analysis of the data",
    "Registration following analysis of the data",
]

# Compound fields require both .question and .uploader keys
COMPOUND_FIELDS = {"q6", "q10", "q14", "q15", "q16", "q17"}

# All expected question keys
ALL_QUESTION_IDS = [f"q{i}" for i in range(2, 24)]

# Forbidden terms that would indicate references to the prior registration
FORBIDDEN_PATTERNS = [
    r"w5zv9",
    r"MTurk",
    r"Mechanical\s+Turk",
    r"Qualtrics",
    r"seven\s+messages",
    r"pre-defined",
    r"six\s+conditions",
    r"\bextending\b",
    r"prior\s+registration",
]


def load_draft(path: Path) -> dict:
    """Load and return the JSON draft."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_structure(draft: dict) -> list[str]:
    """Validate the JSON structure and return a list of issues."""
    issues: list[str] = []

    for field in ("schema_id", "title", "description", "registration_responses"):
        if field not in draft:
            issues.append(f"Missing top-level field: {field}")

    responses = draft.get("registration_responses", {})

    # Check all q2-q23 keys are present
    for qid in ALL_QUESTION_IDS:
        if qid in COMPOUND_FIELDS:
            qkey = f"{qid}.question"
            ukey = f"{qid}.uploader"
            if qkey not in responses:
                issues.append(f"Missing compound key: {qkey}")
            if ukey not in responses:
                issues.append(f"Missing compound key: {ukey}")
            elif not isinstance(responses[ukey], list):
                issues.append(f"{ukey} must be a list, got {type(responses[ukey]).__name__}")
        else:
            if qid not in responses:
                issues.append(f"Missing key: {qid}")

    # q4 must be a list
    if "q4" in responses and not isinstance(responses["q4"], list):
        issues.append(f"q4 must be a list, got {type(responses['q4']).__name__}")

    return issues


def validate_option_strings(draft: dict) -> list[str]:
    """Check that singleselect/multiselect values match exact schema options."""
    issues: list[str] = []
    responses = draft.get("registration_responses", {})

    # q3 — singleselect
    q3 = responses.get("q3", "")
    if q3 not in VALID_Q3_OPTIONS:
        issues.append(f"q3 value does not match any valid option. Got: {q3[:80]}...")

    # q4 — multiselect
    q4 = responses.get("q4", [])
    if isinstance(q4, list):
        for item in q4:
            if item not in VALID_Q4_OPTIONS:
                issues.append(f"q4 contains unrecognized option: {item[:80]}...")

    # q8 — singleselect
    q8 = responses.get("q8", "")
    if q8 not in VALID_Q8_OPTIONS:
        issues.append(f"q8 value does not match any valid option. Got: {q8[:80]}...")

    return issues


def validate_standalone(draft: dict) -> list[str]:
    """Ensure no references to the prior registration or old protocol."""
    issues: list[str] = []
    text = json.dumps(draft)
    for pattern in FORBIDDEN_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            issues.append(f"Found forbidden reference: '{matches[0]}' (pattern: {pattern})")
    return issues


def validate_analysis_fidelity(draft: dict) -> list[str]:
    """Check that q17 describes ANOVA+Tukey (not old t-tests/Mann-Whitney)."""
    issues: list[str] = []
    responses = draft.get("registration_responses", {})
    q17 = responses.get("q17.question", "")

    if "ANOVA" not in q17:
        issues.append("q17 should describe ANOVA — not found")
    if "Tukey" not in q17:
        issues.append("q17 should describe Tukey HSD — not found")

    # Check q16 formulas
    q16 = responses.get("q16.question", "")
    if "(intentions + mind_of_its_own) / 2" not in q16:
        issues.append("q16 missing exact agentic scale formula: (intentions + mind_of_its_own) / 2")
    if "(selfish_rev + honest + unbiased + sincere) / 4" not in q16:
        issues.append("q16 missing exact honest/fair formula: (selfish_rev + honest + unbiased + sincere) / 4")
    if "6 - selfish" not in q16:
        issues.append("q16 missing reverse-coding: 6 - selfish")

    return issues


def dry_run(draft: dict) -> bool:
    """Run all validations and print results. Returns True if all pass."""
    print("=" * 60)
    print("DRY RUN — Validating preregistration draft")
    print("=" * 60)

    print(f"\nTitle: {draft.get('title', '(missing)')}")
    print(f"Schema ID: {draft.get('schema_id', '(missing)')}")
    print(f"Description: {draft.get('description', '(missing)')[:100]}...")

    responses = draft.get("registration_responses", {})
    print(f"\nRegistration response keys ({len(responses)}):")
    for key in sorted(responses.keys()):
        val = responses[key]
        if isinstance(val, str):
            preview = val[:60].replace("\n", " ")
            print(f"  {key}: {preview}{'...' if len(val) > 60 else ''}")
        elif isinstance(val, list):
            print(f"  {key}: [{len(val)} items]")
        else:
            print(f"  {key}: {val}")

    all_issues: list[str] = []

    print("\n--- Structure check ---")
    structure_issues = validate_structure(draft)
    all_issues.extend(structure_issues)
    if structure_issues:
        for issue in structure_issues:
            print(f"  FAIL: {issue}")
    else:
        print("  PASS: All q2-q23 keys present, compound fields valid")

    print("\n--- Option string check ---")
    option_issues = validate_option_strings(draft)
    all_issues.extend(option_issues)
    if option_issues:
        for issue in option_issues:
            print(f"  FAIL: {issue}")
    else:
        print("  PASS: q3, q4, q8 match schema options")

    print("\n--- Standalone check ---")
    standalone_issues = validate_standalone(draft)
    all_issues.extend(standalone_issues)
    if standalone_issues:
        for issue in standalone_issues:
            print(f"  FAIL: {issue}")
    else:
        print("  PASS: No references to prior registration or old protocol")

    print("\n--- Analysis fidelity check ---")
    analysis_issues = validate_analysis_fidelity(draft)
    all_issues.extend(analysis_issues)
    if analysis_issues:
        for issue in analysis_issues:
            print(f"  FAIL: {issue}")
    else:
        print("  PASS: q17 describes ANOVA+Tukey, q16 formulas match pipeline")

    print("\n" + "=" * 60)
    if all_issues:
        print(f"VALIDATION FAILED — {len(all_issues)} issue(s) found")
    else:
        print("ALL CHECKS PASSED")
    print("=" * 60)

    return len(all_issues) == 0


# Mapping from internal q-keys to OSF Preregistration v4 atomic schema keys.
# The v4 schema (697b72f611a8e98484c6139b) uses "344-{block_index}" keys.
# The select option strings also changed from v3 to v4.
Q_TO_ATOMIC = {
    "q2":          "344-2",   # Research questions or hypotheses
    "q3":          "344-17",  # Study type (multi-select in v4)
    "q4":          "344-32",  # Blinding
    "q5":          "344-38",  # Additional blinding
    "q6.question": "344-40",  # Study design
    "q6.uploader": "344-42",  # Study design file upload
    "q7":          "344-44",  # Randomization
    "q8":          "344-4",   # Foreknowledge of data (was "Existing data")
    "q9":          "344-14",  # Explanation of foreknowledge
    "q10.question":"344-47",  # Data collection procedures
    "q10.uploader":"344-49",  # Data collection file upload
    "q11":         "344-51",  # Sample size
    "q12":         "344-53",  # Sample size rationale
    "q13":         "344-55",  # Starting and stopping rules
    "q14.question":"344-58",  # Manipulated variables
    "q14.uploader":"344-60",  # Manipulated variables file upload
    "q15.question":"344-62",  # Measured variables
    "q15.uploader":"344-64",  # Measured variables file upload
    "q16.question":"344-66",  # Indices
    "q16.uploader":"344-68",  # Indices file upload
    "q17.question":"344-71",  # Statistical models
    "q17.uploader":"344-73",  # Statistical models file upload
    "q18":         "344-75",  # Transformations
    "q19":         "344-77",  # Inference criteria
    "q20":         "344-79",  # Data inclusion and exclusion
    "q21":         "344-81",  # Missing data
    "q22":         "344-83",  # Other planned analysis
    "q23":         "344-86",  # Context and additional information
}

# v3 → v4 option string translations
OPTION_TRANSLATIONS = {
    # q3 (study type): v3 was single-select, v4 is multi-select with different wording
    "Experiment - A researcher randomly assigns treatments to study subjects, this includes field or lab experiments. This is also known as an intervention experiment and includes randomized controlled trials.":
        "Randomized Experiment: Must include random assignment of subjects to treatments or conditions. This usually includes lab experiments, field experiments, intervention experiments, randomized controlled trials, and A/B testing.",
    # q4 (blinding)
    "For studies that involve human subjects, they will not know the treatment group to which they have been assigned.":
        "Subjects will not be aware of the assigned treatment during data collection (either because the subjects are not human participants or because of blinding procedures).",
    # q8 (existing data / foreknowledge)
    "Registration prior to creation of data":
        "Data does not yet exist. No part of the data that will be used for this analysis plan exists, and no part will be generated until after this plan is registered.",
}


def translate_responses(responses: dict) -> dict:
    """Translate from internal q-keys to atomic schema 344-N keys."""
    translated = {}
    for q_key, value in responses.items():
        atomic_key = Q_TO_ATOMIC.get(q_key)
        if not atomic_key:
            print(f"  WARNING: No mapping for key '{q_key}', skipping")
            continue

        # Translate select option strings
        if isinstance(value, str) and value in OPTION_TRANSLATIONS:
            value = OPTION_TRANSLATIONS[value]
        elif isinstance(value, list):
            value = [OPTION_TRANSLATIONS.get(v, v) for v in value]

        # v4 study type (q3) is multi-select, wrap string in list
        if q_key == "q3" and isinstance(value, str):
            value = [value]

        translated[atomic_key] = value

    return translated


def submit(draft: dict) -> None:
    """Create a draft registration on OSF."""
    from osf_api_cli.client import OSFClient

    schema_id = draft["schema_id"]
    title = draft["title"]
    description = draft.get("description", "")
    responses = draft["registration_responses"]

    # Translate keys for atomic schema
    translated = translate_responses(responses)

    # Add causal interpretation (new in v4, not in our q-keys)
    translated["344-27"] = [
        "Direct inference on causal relationship(s): This study is intended to infer or estimate a causal relationship between two or more variables. It is designed specifically for the purposes of causal inference or identification."
    ]

    print(f"\nAbout to create draft registration on OSF:")
    print(f"  Title: {title}")
    print(f"  Schema: {schema_id}")
    print(f"  Response keys: {len(translated)}")
    confirm = input("\nProceed? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        sys.exit(0)

    client = OSFClient()

    print("\nStep 1: Creating draft registration...")
    draft_data = client.create_draft_registration(
        schema_id=schema_id,
        title=title,
        description=description,
    )
    draft_id = draft_data["id"]
    print(f"  Created draft: {draft_id}")

    print("Step 2: Updating registration responses...")
    client.update_draft_registration(
        draft_id,
        registration_responses=translated,
    )
    print("  Registration responses saved.")

    print("\n" + "=" * 60)
    print(f"Draft registration created successfully!")
    print(f"  ID:  {draft_id}")
    print(f"  URL: https://osf.io/{draft_id}")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Submit a preregistration draft to OSF"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the JSON without submitting to OSF",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_JSON,
        help=f"Path to JSON draft (default: {DEFAULT_JSON})",
    )
    args = parser.parse_args()

    if not args.json.exists():
        print(f"ERROR: JSON file not found: {args.json}", file=sys.stderr)
        sys.exit(1)

    draft = load_draft(args.json)

    if args.dry_run:
        ok = dry_run(draft)
        sys.exit(0 if ok else 1)
    else:
        # Run validation first
        ok = dry_run(draft)
        if not ok:
            print("\nFix validation issues before submitting.", file=sys.stderr)
            sys.exit(1)
        submit(draft)


if __name__ == "__main__":
    main()
