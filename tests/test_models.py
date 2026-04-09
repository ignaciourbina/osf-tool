"""Tests for typed resource parsing."""

from __future__ import annotations

from osf_api_cli.models import DraftRegistration, Project, infer_object_id_timestamp


def test_infer_object_id_timestamp_returns_utc_iso8601():
    assert infer_object_id_timestamp("69b8bc267e5ab73ed2147e56") == "2026-03-17T02:27:50Z"


def test_draft_registration_uses_api_timestamp_fallback_fields():
    project = Project(
        id="vseu4",
        title="Trait Aggression",
        description=None,
        category="project",
        public=False,
        tags=[],
        date_created=None,
        date_modified=None,
        url="https://osf.io/vseu4/",
        api_url="https://api.osf.io/v2/nodes/vseu4/",
        raw={},
    )
    draft = DraftRegistration.from_api(
        {
            "id": "69b8bc267e5ab73ed2147e56",
            "attributes": {
                "title": None,
                "datetime_initiated": "2026-03-17T02:27:50.059135",
                "datetime_updated": "2026-04-03T22:40:38.758590",
            },
            "links": {
                "html": "https://osf.io/registries/drafts/example/review",
                "self": "https://api.osf.io/v2/draft_registrations/example/",
            },
        },
        project=project,
    )
    assert draft.title_display == "(untitled)"
    assert draft.date_created == "2026-03-17T02:27:50.059135"
    assert draft.date_modified == "2026-04-03T22:40:38.758590"
    assert draft.date_source == "api"
    assert draft.project_title == "Trait Aggression"
