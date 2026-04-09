"""Tests for the service-oriented OSF client."""

from __future__ import annotations

from pathlib import Path

from osf_api_cli.client import OSFClient


class DummyResponse:
    def __init__(self, payload=None):
        self.payload = payload or {}

    def iter_content(self, chunk_size: int = 8192):
        yield b"payload"


def test_list_all_draft_registrations_aggregates_project_context():
    client = OSFClient(token="token")

    client.projects.list = lambda: [  # type: ignore[method-assign]
        type("Project", (), {"id": "node1", "title": "Project One", "url": "https://osf.io/node1/"})(),
        type("Project", (), {"id": "node2", "title": "Project Two", "url": "https://osf.io/node2/"})(),
    ]

    def fake_paginate(path: str, **params):
        if path == "nodes/node1/draft_registrations/":
            yield {"id": "69b8bc267e5ab73ed2147e56", "attributes": {}, "links": {}}
        else:
            yield from []

    client.transport.paginate = fake_paginate  # type: ignore[method-assign]

    summaries = client.drafts.list_all()
    assert len(summaries) == 1
    assert summaries[0].project_id == "node1"
    assert summaries[0].project_title == "Project One"


def test_file_upload_returns_typed_result(tmp_path):
    source = tmp_path / "local.txt"
    source.write_text("payload")
    client = OSFClient(token="token")
    captured: dict[str, object] = {}

    def fake_request_json(method: str, path_or_url: str, **kwargs):
        captured["method"] = method
        captured["url"] = path_or_url
        return {"ok": True}

    client.transport.request_json = fake_request_json  # type: ignore[method-assign]

    result = client.files.upload(
        "abcde",
        source,
        remote_path="nested folder/custom name.txt",
    )

    assert result.name == "custom name.txt"
    assert result.remote_path == "/nested folder/custom name.txt"
    assert captured["method"] == "PUT"
    assert captured["url"] == (
        "https://files.osf.io/v1/resources/abcde/providers/osfstorage/"
        "nested%20folder/?kind=file&name=custom+name.txt"
    )


def test_recursive_file_listing_walks_nested_folders():
    client = OSFClient(token="token")

    def fake_paginate(path: str, **params):
        if path == "nodes/node123/files/osfstorage/":
            yield {
                "id": "folder1",
                "attributes": {
                    "name": "folder",
                    "kind": "folder",
                    "materialized_path": "/folder",
                },
                "links": {},
            }
            yield {
                "id": "file1",
                "attributes": {
                    "name": "root.txt",
                    "kind": "file",
                    "materialized_path": "/root.txt",
                    "size": 7,
                },
                "links": {},
            }
            return
        if path == "nodes/node123/files/osfstorage/folder":
            yield {
                "id": "file2",
                "attributes": {
                    "name": "nested.txt",
                    "kind": "file",
                    "materialized_path": "/folder/nested.txt",
                    "size": 9,
                },
                "links": {},
            }

    client.transport.paginate = fake_paginate  # type: ignore[method-assign]

    files = client.files.list("node123", recursive=True)

    assert [item.materialized_path for item in files] == [
        "/folder",
        "/root.txt",
        "/folder/nested.txt",
    ]
    assert all(item.provider == "osfstorage" for item in files)


def test_list_all_providers_aggregates_provider_entries():
    client = OSFClient(token="token")
    client.files.list_provider_names = lambda node_id: ["osfstorage", "dropbox"]  # type: ignore[method-assign]
    client.files.list = lambda node_id, provider="osfstorage", path="/", recursive=False: [  # type: ignore[method-assign]
        type(
            "Entry",
            (),
            {
                "provider": provider,
                "materialized_path": f"/{provider}/report.txt",
                "name": "report.txt",
                "kind": "file",
                "id": provider,
            },
        )()
    ]

    files = client.files.list_all_providers("node123")

    assert len(files) == 2
    assert {item.provider for item in files} == {"osfstorage", "dropbox"}


def test_create_draft_registration_supports_unattached_legacy_flow():
    client = OSFClient(token="token")
    captured: dict[str, object] = {}

    def fake_request_json(method: str, path_or_url: str, **kwargs):
        captured["method"] = method
        captured["url"] = path_or_url
        captured["json"] = kwargs["json"]
        return {
            "data": {
                "id": "draft123",
                "attributes": {"title": "Draft Title"},
                "links": {"self": "https://api.osf.io/v2/draft_registrations/draft123/"},
            }
        }

    client.transport.request_json = fake_request_json  # type: ignore[method-assign]

    draft = client.create_draft_registration(
        schema_id="schema1",
        title="Draft Title",
        description="Draft description",
    )

    assert draft.id == "draft123"
    assert captured["method"] == "POST"
    assert captured["url"] == "draft_registrations/"
    payload = captured["json"]
    assert payload["data"]["attributes"]["title"] == "Draft Title"
    assert payload["data"]["attributes"]["description"] == "Draft description"


def test_update_draft_registration_supports_response_payloads():
    client = OSFClient(token="token")
    captured: dict[str, object] = {}

    def fake_update_metadata(draft_id: str, *, registration_metadata=None, registration_responses=None):
        captured["draft_id"] = draft_id
        captured["registration_metadata"] = registration_metadata
        captured["registration_responses"] = registration_responses
        return type("Draft", (), {"id": draft_id, "title_display": "Draft"})()

    client.drafts.update_metadata = fake_update_metadata  # type: ignore[method-assign]

    draft = client.update_draft_registration("draft123", registration_responses={"344-66": "value"})

    assert draft.id == "draft123"
    assert captured["draft_id"] == "draft123"
    assert captured["registration_metadata"] is None
    assert captured["registration_responses"] == {"344-66": "value"}
