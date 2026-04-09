"""Tests for the nested CLI parser."""

from __future__ import annotations

from types import SimpleNamespace

from osf_api_cli.cli import (
    _collect_draft_inspect_bundle,
    build_parser,
    cmd_draft_inspect,
    cmd_draft_list,
    cmd_draft_update_metadata,
    cmd_project_inspect,
)


def test_parser_supports_nested_registration_list():
    parser = build_parser()
    args = parser.parse_args(["registration", "list", "--all-projects"])
    assert args.resource == "registration"
    assert args.action == "list"
    assert args.all_projects is True


def test_parser_supports_auth_check():
    parser = build_parser()
    args = parser.parse_args(["auth", "check"])
    assert args.resource == "auth"
    assert args.action == "check"


def test_parser_accepts_output_after_terminal_subcommand():
    parser = build_parser()
    args = parser.parse_args(["registration", "list", "--all-projects", "--output", "json"])
    assert args.resource == "registration"
    assert args.action == "list"
    assert args.output == "json"


def test_parser_supports_plural_aliases_and_ls():
    parser = build_parser()
    args = parser.parse_args(["drafts", "ls", "--all-projects"])
    assert args.handler is cmd_draft_list
    assert args.all_projects is True


def test_parser_supports_project_inspect_export_alias():
    parser = build_parser()
    args = parser.parse_args(["projects", "export", "node123", "--dest", "out.json"])
    assert args.handler is cmd_project_inspect
    assert args.node_id == "node123"
    assert args.dest == "out.json"


def test_parser_supports_my_drafts_shortcut():
    parser = build_parser()
    args = parser.parse_args(["my-drafts", "--json"])
    assert args.handler is cmd_draft_list
    assert args.all_projects is True


def test_parser_supports_draft_inspect_export_alias():
    parser = build_parser()
    args = parser.parse_args(["drafts", "export", "draft123", "--dest", "draft.json"])
    assert args.handler is cmd_draft_inspect
    assert args.draft_id == "draft123"
    assert args.dest == "draft.json"


def test_collect_draft_inspect_bundle_exposes_registration_metadata():
    draft = SimpleNamespace(
        id="draft123",
        title_display="Draft Title",
        date_created="2026-04-03T21:23:55.183723",
        date_modified="2026-04-06T20:11:30.208964",
        date_created_inferred=None,
        raw={
            "attributes": {
                "description": "Draft description",
                "registration_metadata": {"344-66": {"value": "Indices text"}},
                "registration_responses": {"344-66": "Indices text"},
                "tags": ["trait aggression"],
                "has_project": False,
            },
            "relationships": {
                "registration_schema": {"data": {"id": "schema1"}},
                "provider": {"data": {"id": "osf"}},
                "branched_from": {"data": {"id": "xevr3", "type": "draft_nodes"}},
            },
        },
    )
    client = SimpleNamespace(drafts=SimpleNamespace(get=lambda draft_id: draft))
    args = SimpleNamespace(draft_id="draft123")

    bundle = _collect_draft_inspect_bundle(client, args)

    assert bundle["draft_id"] == "draft123"
    assert bundle["registration_metadata"]["344-66"]["value"] == "Indices text"
    assert bundle["schema_id"] == "schema1"
    assert bundle["provider_id"] == "osf"


def test_parser_supports_draft_update_metadata():
    parser = build_parser()
    args = parser.parse_args(["draft", "update-metadata", "draft123", "fields.json"])
    assert args.handler is cmd_draft_update_metadata
    assert args.draft_id == "draft123"
    assert args.metadata_json == "fields.json"
