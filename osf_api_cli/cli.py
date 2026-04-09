"""Nested CLI for OSF research workflows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .client import DEFAULT_TIMEOUT, OSFClient
from .errors import OSFError
from .models import (
    Contributor,
    DraftRegistration,
    FileEntry,
    Project,
    Registration,
    RegistrationSchema,
    UploadResult,
    User,
)

INSPECT_INCLUDE_CHOICES = {"project", "contributors", "files", "drafts", "registrations"}
DEFAULT_INSPECT_INCLUDES = (
    "project",
    "contributors",
    "files",
    "drafts",
    "registrations",
)


def _jsonable(value: Any, *, include_raw: bool) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict(include_raw=include_raw)
    if isinstance(value, list):
        return [_jsonable(item, include_raw=include_raw) for item in value]
    if isinstance(value, dict):
        return {
            key: _jsonable(item, include_raw=include_raw)
            for key, item in value.items()
        }
    return value


def _yaml_dump(value: Any, *, indent: int = 0) -> str:
    prefix = "  " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.append(_yaml_dump(item, indent=indent + 1))
            else:
                lines.append(f"{prefix}{key}: {json.dumps(item)}")
        return "\n".join(lines)
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.append(_yaml_dump(item, indent=indent + 1))
            else:
                lines.append(f"{prefix}- {json.dumps(item)}")
        return "\n".join(lines)
    return f"{prefix}{json.dumps(value)}"


def _emit_structured(value: Any, args: argparse.Namespace) -> None:
    payload = _jsonable(value, include_raw=args.verbose)
    if args.output == "json":
        print(json.dumps(payload, indent=2))
    elif args.output == "yaml":
        print(_yaml_dump(payload))
    else:
        raise ValueError("structured output requires json or yaml")


def _table(rows: list[list[str]], headers: list[str]) -> None:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    fmt = "  ".join(f"{{:<{width}}}" for width in widths)
    print(fmt.format(*headers))
    print(fmt.format(*("-" * width for width in widths)))
    for row in rows:
        print(fmt.format(*row))


def _print_kv(data: list[tuple[str, str]]) -> None:
    width = max(len(key) for key, _ in data)
    for key, value in data:
        print(f"{key:<{width}}  {value}")


def _parse_include(value: str) -> list[str]:
    requested = [item.strip().lower() for item in value.split(",") if item.strip()]
    if not requested or requested == ["all"]:
        return list(DEFAULT_INSPECT_INCLUDES)
    invalid = [item for item in requested if item not in INSPECT_INCLUDE_CHOICES]
    if invalid:
        allowed = ", ".join(sorted(INSPECT_INCLUDE_CHOICES))
        raise ValueError(f"Unknown include target(s): {', '.join(invalid)}. Allowed: {allowed}, all")
    ordered: list[str] = []
    for item in requested:
        if item not in ordered:
            ordered.append(item)
    return ordered


def _write_structured_file(value: Any, args: argparse.Namespace, destination: str) -> Path:
    payload = _jsonable(value, include_raw=args.verbose)
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in {".yaml", ".yml"}:
        path.write_text(_yaml_dump(payload) + "\n", encoding="utf-8")
    else:
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _collect_project_inspect_bundle(
    client: OSFClient,
    args: argparse.Namespace,
) -> dict[str, Any]:
    include = _parse_include(args.include)
    bundle: dict[str, Any] = {
        "node_id": args.node_id,
        "include": include,
    }
    if "project" in include:
        bundle["project"] = client.projects.get(args.node_id)
    if "contributors" in include:
        bundle["contributors"] = client.contributors.list(args.node_id)
    if "files" in include:
        providers = client.files.list_provider_names(args.node_id)
        bundle["providers"] = providers
        if args.all_providers:
            bundle["files"] = client.files.list_all_providers(
                args.node_id,
                path=args.path,
                recursive=args.recursive,
            )
            bundle["file_context"] = {
                "providers": "all",
                "path": args.path,
                "recursive": args.recursive,
            }
        else:
            bundle["files"] = client.files.list(
                args.node_id,
                provider=args.provider,
                path=args.path,
                recursive=args.recursive,
            )
            bundle["file_context"] = {
                "providers": [args.provider],
                "path": args.path,
                "recursive": args.recursive,
            }
    if "drafts" in include:
        bundle["drafts"] = client.drafts.list(args.node_id)
    if "registrations" in include:
        bundle["registrations"] = client.registrations.list(args.node_id)
    return bundle


def _collect_draft_inspect_bundle(
    client: OSFClient,
    args: argparse.Namespace,
) -> dict[str, Any]:
    draft = client.drafts.get(args.draft_id)
    attrs = draft.raw.get("attributes", {})
    relationships = draft.raw.get("relationships", {})
    return {
        "draft_id": args.draft_id,
        "draft": draft,
        "registration_metadata": attrs.get("registration_metadata", {}),
        "registration_responses": attrs.get("registration_responses", {}),
        "description": attrs.get("description"),
        "tags": attrs.get("tags", []),
        "has_project": attrs.get("has_project"),
        "schema_id": relationships.get("registration_schema", {}).get("data", {}).get("id"),
        "provider_id": relationships.get("provider", {}).get("data", {}).get("id"),
        "branched_from": relationships.get("branched_from", {}).get("data", {}),
    }


def _handle_user(user: User, args: argparse.Namespace) -> None:
    if args.output != "table":
        _emit_structured(user, args)
        return
    rows = [
        ("Name", user.full_name),
        ("ID", user.id),
        ("Email", user.email or "N/A"),
        ("Profile", user.profile_url or "N/A"),
    ]
    if user.employment:
        job = user.employment[0]
        rows.append(
            (
                "Affiliation",
                f"{job.get('institution', '')} — {job.get('department', '')}".strip(" —"),
            )
        )
    _print_kv(rows)


def _handle_projects(projects: list[Project] | Project, args: argparse.Namespace) -> None:
    if args.output != "table":
        _emit_structured(projects, args)
        return
    if isinstance(projects, Project):
        _print_kv(
            [
                ("Title", projects.title),
                ("ID", projects.id),
                ("Category", projects.category or "N/A"),
                ("Public", str(projects.public)),
                ("Created", projects.date_created or "N/A"),
                ("Modified", projects.date_modified or "N/A"),
                ("Description", projects.description or "(none)"),
                ("Tags", ", ".join(projects.tags) or "(none)"),
                ("URL", projects.url or "N/A"),
            ]
        )
        return
    rows = [
        [item.id, "public" if item.public else "private", item.title]
        for item in projects
    ]
    if not rows:
        print("(no projects)")
        return
    _table(rows, ["ID", "Visibility", "Title"])


def _handle_files(files: list[FileEntry] | UploadResult | Path, args: argparse.Namespace) -> None:
    if args.output != "table":
        _emit_structured(files, args)
        return
    if isinstance(files, list):
        include_provider = any(item.provider for item in files)
        rows = []
        for item in files:
            row = [
                item.kind,
                item.name,
                str(item.size or ""),
                (item.date_modified or "")[:10],
            ]
            if include_provider:
                row.insert(0, item.provider or "")
            rows.append(row)
        if not rows:
            print("(no files)")
            return
        headers = ["Kind", "Name", "Size", "Modified"]
        if include_provider:
            headers.insert(0, "Provider")
        _table(rows, headers)
        return
    if isinstance(files, UploadResult):
        _print_kv(
            [
                ("Name", files.name),
                ("Provider", files.provider),
                ("Remote Path", files.remote_path),
            ]
        )
        return
    print(str(files))


def _handle_drafts(drafts: list[DraftRegistration] | DraftRegistration, args: argparse.Namespace) -> None:
    if args.output != "table":
        _emit_structured(drafts, args)
        return
    if isinstance(drafts, DraftRegistration):
        _print_kv(
            [
                ("Title", drafts.title_display),
                ("ID", drafts.id),
                ("Project", drafts.project_title or "N/A"),
                ("Created", drafts.date_created or drafts.date_created_inferred or "N/A"),
                ("Modified", drafts.date_modified or "N/A"),
                ("Source", drafts.date_source),
                ("URL", drafts.url or "N/A"),
            ]
        )
        return
    rows = [
        [
            item.project_id or "",
            item.id,
            item.project_title or "",
            item.title_display,
            (item.date_created or item.date_created_inferred or "")[:19],
            item.date_source,
        ]
        for item in drafts
    ]
    if not rows:
        print("(no draft registrations)")
        return
    _table(rows, ["Project", "Draft", "Project Title", "Draft Title", "Created", "Source"])


def _handle_registrations(
    registrations: list[Registration] | Registration,
    args: argparse.Namespace,
) -> None:
    if args.output != "table":
        _emit_structured(registrations, args)
        return
    if isinstance(registrations, Registration):
        _print_kv(
            [
                ("Title", registrations.title_display),
                ("ID", registrations.id),
                ("Project", registrations.project_title or "N/A"),
                ("Registered", registrations.date_registered or "N/A"),
                ("Created", registrations.date_created or "N/A"),
                ("Modified", registrations.date_modified or "N/A"),
                ("URL", registrations.url or "N/A"),
            ]
        )
        return
    rows = [
        [
            item.project_id or "",
            item.id,
            item.project_title or "",
            item.title_display,
            (item.date_registered or item.date_created or "")[:19],
        ]
        for item in registrations
    ]
    if not rows:
        print("(no registrations)")
        return
    _table(rows, ["Project", "Registration", "Project Title", "Title", "Registered"])


def _handle_contributors(contributors: list[Contributor], args: argparse.Namespace) -> None:
    if args.output != "table":
        _emit_structured(contributors, args)
        return
    rows = [
        [item.id, item.name, item.permission or "?", "yes" if item.bibliographic else "no"]
        for item in contributors
    ]
    if not rows:
        print("(no contributors)")
        return
    _table(rows, ["ID", "Name", "Permission", "Bibliographic"])


def _handle_schemas(schemas: list[RegistrationSchema], args: argparse.Namespace) -> None:
    if args.output != "table":
        _emit_structured(schemas, args)
        return
    rows = [[item.id, item.name, item.schema_version] for item in schemas]
    if not rows:
        print("(no schemas)")
        return
    _table(rows, ["ID", "Name", "Version"])


def _require_node_or_all(args: argparse.Namespace) -> None:
    if not args.all_projects and not args.node_id:
        raise ValueError("Provide a node_id or pass --all-projects.")


def cmd_auth_whoami(client: OSFClient, args: argparse.Namespace) -> None:
    _handle_user(client.whoami(), args)


def cmd_auth_check(client: OSFClient, args: argparse.Namespace) -> None:
    user = client.whoami()
    if args.output != "table":
        _emit_structured(
            {
                "status": "ok",
                "profile": client.settings.profile,
                "token_source": client.settings.token_source,
                "user": user,
            },
            args,
        )
        return
    _print_kv(
        [
            ("Status", "ok"),
            ("Profile", client.settings.profile),
            ("Token Source", client.settings.token_source),
            ("User", f"{user.full_name} ({user.id})"),
        ]
    )


def cmd_project_list(client: OSFClient, args: argparse.Namespace) -> None:
    _handle_projects(client.projects.list(), args)


def cmd_project_get(client: OSFClient, args: argparse.Namespace) -> None:
    _handle_projects(client.projects.get(args.node_id), args)


def cmd_project_create(client: OSFClient, args: argparse.Namespace) -> None:
    tags = [item.strip() for item in args.tags.split(",")] if args.tags else None
    _handle_projects(
        client.projects.create(
            title=args.title,
            description=args.description,
            public=args.public,
            category=args.category,
            tags=tags,
        ),
        args,
    )


def cmd_project_inspect(client: OSFClient, args: argparse.Namespace) -> None:
    bundle = _collect_project_inspect_bundle(client, args)
    export_path: Path | None = None
    if args.dest:
        export_path = _write_structured_file(bundle, args, args.dest)
    if args.output != "table":
        _emit_structured(bundle, args)
        return
    project = bundle.get("project")
    project_title = project.title if isinstance(project, Project) else args.node_id
    rows = [
        ("Project", project_title),
        ("Node ID", args.node_id),
        ("Included", ", ".join(bundle["include"])),
    ]
    if "contributors" in bundle:
        rows.append(("Contributors", str(len(bundle["contributors"]))))
    if "files" in bundle:
        rows.append(("Files", str(len(bundle["files"]))))
        rows.append(("Providers", ", ".join(bundle.get("providers", [])) or "(none)"))
    if "drafts" in bundle:
        rows.append(("Drafts", str(len(bundle["drafts"]))))
    if "registrations" in bundle:
        rows.append(("Registrations", str(len(bundle["registrations"]))))
    if export_path is not None:
        rows.append(("Exported", str(export_path)))
    _print_kv(rows)


def cmd_draft_inspect(client: OSFClient, args: argparse.Namespace) -> None:
    bundle = _collect_draft_inspect_bundle(client, args)
    export_path: Path | None = None
    if args.dest:
        export_path = _write_structured_file(bundle, args, args.dest)
    if args.output != "table":
        _emit_structured(bundle, args)
        return
    draft = bundle["draft"]
    rows = [
        ("Draft", draft.title_display),
        ("Draft ID", draft.id),
        ("Created", draft.date_created or draft.date_created_inferred or "N/A"),
        ("Modified", draft.date_modified or "N/A"),
        ("Schema", str(bundle.get("schema_id") or "N/A")),
        ("Provider", str(bundle.get("provider_id") or "N/A")),
        ("Has Project", str(bundle.get("has_project"))),
        ("Metadata Fields", str(len(bundle["registration_metadata"]))),
    ]
    if export_path is not None:
        rows.append(("Exported", str(export_path)))
    _print_kv(rows)


def cmd_file_list(client: OSFClient, args: argparse.Namespace) -> None:
    _handle_files(
        client.files.list_all_providers(args.node_id, path=args.path, recursive=args.recursive)
        if args.all_providers
        else client.files.list(
            args.node_id,
            provider=args.provider,
            path=args.path,
            recursive=args.recursive,
        ),
        args,
    )


def cmd_file_upload(client: OSFClient, args: argparse.Namespace) -> None:
    local_path = Path(args.local_path)
    if not local_path.exists():
        raise FileNotFoundError(f"{local_path} does not exist")
    result = client.files.upload(
        args.node_id,
        local_path,
        provider=args.provider,
        remote_name=args.name,
        remote_path=args.remote_path,
    )
    _handle_files(result, args)


def cmd_file_download(client: OSFClient, args: argparse.Namespace) -> None:
    result = client.files.download_by_path(
        args.node_id,
        args.remote_path,
        dest=args.dest,
        provider=args.provider,
    )
    _handle_files(result, args)


def cmd_draft_list(client: OSFClient, args: argparse.Namespace) -> None:
    _require_node_or_all(args)
    if args.all_projects:
        drafts = client.drafts.list_all()
    else:
        drafts = client.drafts.list(args.node_id)
    _handle_drafts(drafts, args)


def cmd_draft_get(client: OSFClient, args: argparse.Namespace) -> None:
    _handle_drafts(client.drafts.get(args.draft_id), args)


def cmd_draft_update_metadata(client: OSFClient, args: argparse.Namespace) -> None:
    payload_path = Path(args.metadata_json)
    if not payload_path.exists():
        raise FileNotFoundError(f"{payload_path} does not exist")
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("update JSON must be an object keyed by OSF field id")
    nested_values = [value for value in payload.values() if isinstance(value, dict)]
    if nested_values and all({"value", "extra", "comments"} <= set(value.keys()) for value in nested_values):
        draft = client.drafts.update_metadata(
            args.draft_id,
            registration_metadata=payload,
        )
    else:
        draft = client.drafts.update_metadata(
            args.draft_id,
            registration_responses=payload,
        )
    if args.output != "table":
        _emit_structured(draft, args)
        return
    rows = [
        ("Draft", draft.title_display),
        ("Draft ID", draft.id),
        ("Updated Fields", str(len(payload))),
        ("Source", str(payload_path)),
    ]
    _print_kv(rows)


def cmd_registration_list(client: OSFClient, args: argparse.Namespace) -> None:
    _require_node_or_all(args)
    if args.all_projects:
        registrations = client.registrations.list_all()
    else:
        registrations = client.registrations.list(args.node_id)
    _handle_registrations(registrations, args)


def cmd_registration_get(client: OSFClient, args: argparse.Namespace) -> None:
    _handle_registrations(client.registrations.get(args.registration_id), args)


def cmd_contributor_list(client: OSFClient, args: argparse.Namespace) -> None:
    _handle_contributors(client.contributors.list(args.node_id), args)


def cmd_schema_list(client: OSFClient, args: argparse.Namespace) -> None:
    _handle_schemas(client.schemas.list(), args)


def build_parser() -> argparse.ArgumentParser:
    display_parent = argparse.ArgumentParser(add_help=False)
    display_parent.add_argument("--output", choices=["table", "json", "yaml"], default="table")
    display_parent.add_argument("--json", action="store_true", help="Alias for --output json")
    display_parent.add_argument("--verbose", action="store_true", help="Include raw payloads in structured output")
    display_parent.add_argument("--quiet", action="store_true", help="Suppress non-structured success output")
    display_parent.add_argument("--no-color", action="store_true", help="Disable colorized output")

    parser = argparse.ArgumentParser(
        prog="osf",
        description="Research-grade CLI for the OSF API.",
        parents=[display_parent],
    )
    parser.add_argument("--profile", default=None, help="Named auth profile")
    parser.add_argument("--config-file", default=None, help="Path to config TOML")
    parser.add_argument("--token", default=None, help="OSF personal access token")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="HTTP timeout in seconds")

    root = parser.add_subparsers(dest="resource", required=True)

    auth = root.add_parser("auth", help="Authentication and identity commands")
    auth_sub = auth.add_subparsers(dest="action", required=True)
    auth_sub.add_parser("whoami", aliases=["me"], help="Show the authenticated OSF user", parents=[display_parent]).set_defaults(handler=cmd_auth_whoami)
    auth_sub.add_parser("check", aliases=["status"], help="Check authentication status", parents=[display_parent]).set_defaults(handler=cmd_auth_check)

    project = root.add_parser("project", aliases=["projects"], help="Project and node commands")
    project_sub = project.add_subparsers(dest="action", required=True)
    project_sub.add_parser("list", aliases=["ls"], help="List your projects", parents=[display_parent]).set_defaults(handler=cmd_project_list)
    project_get = project_sub.add_parser("get", aliases=["show"], help="Get a project by node ID", parents=[display_parent])
    project_get.add_argument("node_id", help="OSF node ID")
    project_get.set_defaults(handler=cmd_project_get)
    project_create = project_sub.add_parser("create", aliases=["new"], help="Create a project", parents=[display_parent])
    project_create.add_argument("title", help="Project title")
    project_create.add_argument("-d", "--description", default="", help="Project description")
    project_create.add_argument("--public", action="store_true", help="Make the project public")
    project_create.add_argument("--category", default="project", help="OSF project category")
    project_create.add_argument("--tags", default="", help="Comma-separated tags")
    project_create.set_defaults(handler=cmd_project_create)
    project_inspect = project_sub.add_parser(
        "inspect",
        aliases=["export"],
        help="Aggregate project metadata across related resources",
        parents=[display_parent],
    )
    project_inspect.add_argument("node_id", help="OSF node ID")
    project_inspect.add_argument(
        "--include",
        default=",".join(DEFAULT_INSPECT_INCLUDES),
        help="Comma-separated resources to include: project,contributors,files,drafts,registrations,all",
    )
    project_inspect.add_argument("--dest", default=None, help="Optional path to write the structured export")
    project_inspect.add_argument("-p", "--provider", default="osfstorage", help="Storage provider for file inspection")
    project_inspect.add_argument("--path", default="/", help="Provider path for file inspection")
    project_inspect.add_argument("--recursive", action="store_true", help="Recurse into nested folders during file inspection")
    project_inspect.add_argument("--all-providers", action="store_true", help="Inspect files across all available providers")
    project_inspect.set_defaults(handler=cmd_project_inspect)

    file_parser = root.add_parser("file", aliases=["files"], help="File and storage commands")
    file_sub = file_parser.add_subparsers(dest="action", required=True)
    file_list = file_sub.add_parser("list", aliases=["ls"], help="List project files", parents=[display_parent])
    file_list.add_argument("node_id", help="OSF node ID")
    file_list.add_argument("-p", "--provider", default="osfstorage", help="Storage provider")
    file_list.add_argument("--path", default="/", help="Provider path")
    file_list.add_argument("--recursive", action="store_true", help="Recurse into nested folders")
    file_list.add_argument("--all-providers", action="store_true", help="Aggregate files across all providers")
    file_list.set_defaults(handler=cmd_file_list)
    file_upload = file_sub.add_parser("upload", aliases=["put"], help="Upload a file", parents=[display_parent])
    file_upload.add_argument("node_id", help="OSF node ID")
    file_upload.add_argument("local_path", help="Local file path")
    file_upload.add_argument("-p", "--provider", default="osfstorage", help="Storage provider")
    file_upload.add_argument("-n", "--name", default=None, help="Remote file name")
    file_upload.add_argument("--remote-path", default=None, help="Remote path inside the provider")
    file_upload.set_defaults(handler=cmd_file_upload)
    file_download = file_sub.add_parser("download", aliases=["get"], help="Download a file by remote path", parents=[display_parent])
    file_download.add_argument("node_id", help="OSF node ID")
    file_download.add_argument("remote_path", help="Remote file path")
    file_download.add_argument("--dest", default=None, help="Local destination path")
    file_download.add_argument("-p", "--provider", default="osfstorage", help="Storage provider")
    file_download.set_defaults(handler=cmd_file_download)

    draft = root.add_parser("draft", aliases=["drafts"], help="Draft registration commands")
    draft_sub = draft.add_subparsers(dest="action", required=True)
    draft_list = draft_sub.add_parser("list", aliases=["ls"], help="List draft registrations", parents=[display_parent])
    draft_list.add_argument("node_id", nargs="?", help="OSF node ID")
    draft_list.add_argument("--all-projects", action="store_true", help="List drafts across all accessible projects")
    draft_list.set_defaults(handler=cmd_draft_list)
    draft_get = draft_sub.add_parser("get", aliases=["show"], help="Get a draft registration by ID", parents=[display_parent])
    draft_get.add_argument("draft_id", help="Draft registration ID")
    draft_get.set_defaults(handler=cmd_draft_get)
    draft_inspect = draft_sub.add_parser(
        "inspect",
        aliases=["export"],
        help="Inspect or export a draft registration by draft ID",
        parents=[display_parent],
    )
    draft_inspect.add_argument("draft_id", help="Draft registration ID")
    draft_inspect.add_argument("--dest", default=None, help="Optional path to write the structured export")
    draft_inspect.set_defaults(handler=cmd_draft_inspect)
    draft_update = draft_sub.add_parser(
        "update-metadata",
        help="Patch a draft registration's registration_metadata from a JSON file",
        parents=[display_parent],
    )
    draft_update.add_argument("draft_id", help="Draft registration ID")
    draft_update.add_argument("metadata_json", help="Path to JSON object keyed by OSF field id")
    draft_update.set_defaults(handler=cmd_draft_update_metadata)

    registration = root.add_parser("registration", aliases=["registrations"], help="Completed registration commands")
    registration_sub = registration.add_subparsers(dest="action", required=True)
    registration_list = registration_sub.add_parser("list", aliases=["ls"], help="List registrations", parents=[display_parent])
    registration_list.add_argument("node_id", nargs="?", help="OSF node ID")
    registration_list.add_argument("--all-projects", action="store_true", help="List registrations across all accessible projects")
    registration_list.set_defaults(handler=cmd_registration_list)
    registration_get = registration_sub.add_parser("get", aliases=["show"], help="Get a registration by ID", parents=[display_parent])
    registration_get.add_argument("registration_id", help="Registration ID")
    registration_get.set_defaults(handler=cmd_registration_get)

    contributor = root.add_parser("contributor", aliases=["contributors"], help="Contributor commands")
    contributor_sub = contributor.add_subparsers(dest="action", required=True)
    contributor_list = contributor_sub.add_parser("list", aliases=["ls"], help="List project contributors", parents=[display_parent])
    contributor_list.add_argument("node_id", help="OSF node ID")
    contributor_list.set_defaults(handler=cmd_contributor_list)

    schema = root.add_parser("schema", aliases=["schemas"], help="Registration schema commands")
    schema_sub = schema.add_subparsers(dest="action", required=True)
    schema_sub.add_parser("list", aliases=["ls"], help="List registration schemas", parents=[display_parent]).set_defaults(handler=cmd_schema_list)

    my_drafts = root.add_parser("my-drafts", help="List draft registrations across all accessible projects", parents=[display_parent])
    my_drafts.set_defaults(handler=cmd_draft_list, node_id=None, all_projects=True, action="list")

    my_registrations = root.add_parser("my-registrations", help="List registrations across all accessible projects", parents=[display_parent])
    my_registrations.set_defaults(handler=cmd_registration_list, node_id=None, all_projects=True, action="list")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.json:
        args.output = "json"
    try:
        client = OSFClient(
            token=args.token,
            profile=args.profile,
            config_path=args.config_file,
            timeout=args.timeout,
        )
        args.handler(client, args)
    except (OSFError, FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
