"""CLI entry point for osf-api-cli."""

from __future__ import annotations

import argparse
import json
import sys

from .client import OSFClient, OSFClientError


def _json_out(data: object) -> None:
    print(json.dumps(data, indent=2))


def _brief_node(n: dict) -> dict:
    a = n.get("attributes", {})
    return {"id": n["id"], "title": a.get("title"), "category": a.get("category")}


def cmd_me(client: OSFClient, _args: argparse.Namespace) -> None:
    user = client.me()
    a = user["attributes"]
    print(f"User ID:  {user['id']}")
    print(f"Name:     {a['full_name']}")
    print(f"Email:    {a.get('email', 'N/A')}")
    print(f"Active:   {a['active']}")
    print(f"Joined:   {a['date_registered']}")


def cmd_nodes(client: OSFClient, args: argparse.Namespace) -> None:
    nodes = client.list_nodes()
    if args.json:
        _json_out([_brief_node(n) for n in nodes])
    else:
        if not nodes:
            print("No nodes found.")
            return
        for n in nodes:
            a = n.get("attributes", {})
            print(f"  {n['id']}  {a.get('title', '—')}  [{a.get('category', '')}]")


def cmd_node(client: OSFClient, args: argparse.Namespace) -> None:
    node = client.get_node(args.node_id)
    if args.json:
        _json_out(node)
    else:
        a = node["attributes"]
        print(f"ID:          {node['id']}")
        print(f"Title:       {a['title']}")
        print(f"Category:    {a.get('category')}")
        print(f"Description: {a.get('description', '')[:120]}")
        print(f"Public:      {a.get('public')}")
        print(f"Created:     {a.get('date_created')}")
        print(f"Modified:    {a.get('date_modified')}")


def cmd_files(client: OSFClient, args: argparse.Namespace) -> None:
    files = client.list_node_files(args.node_id)
    if args.json:
        _json_out(files)
    else:
        if not files:
            print("No files found.")
            return
        for f in files:
            a = f.get("attributes", {})
            kind = a.get("kind", "?")
            name = a.get("name", "—")
            size = a.get("size")
            size_str = f"  ({size} bytes)" if size else ""
            print(f"  [{kind}] {name}{size_str}")


def cmd_drafts(client: OSFClient, args: argparse.Namespace) -> None:
    drafts = client.list_draft_registrations()
    if args.json:
        _json_out(drafts)
    else:
        if not drafts:
            print("No draft registrations found.")
            return
        for d in drafts:
            a = d.get("attributes", {})
            print(f"  {d['id']}  {a.get('title', '(untitled)')}")


def cmd_registrations(client: OSFClient, args: argparse.Namespace) -> None:
    regs = client.list_user_registrations()
    if args.json:
        _json_out(regs)
    else:
        if not regs:
            print("No registrations found.")
            return
        for r in regs:
            a = r.get("attributes", {})
            print(f"  {r['id']}  {a.get('title', '(untitled)')}  public={a.get('public')}")


def cmd_schemas(client: OSFClient, args: argparse.Namespace) -> None:
    schemas = client.list_registration_schemas()
    for s in schemas:
        a = s.get("attributes", {})
        print(f"  {s['id']}  {a.get('name', '—')}  (v{a.get('schema_version', '?')})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="osf-api",
        description="CLI for the OSF API v2",
    )
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("me", help="Show authenticated user profile")
    sub.add_parser("nodes", help="List your nodes / projects")

    p_node = sub.add_parser("node", help="Show a specific node")
    p_node.add_argument("node_id", help="Node GUID")

    p_files = sub.add_parser("files", help="List files in a node")
    p_files.add_argument("node_id", help="Node GUID")

    sub.add_parser("drafts", help="List draft registrations")
    sub.add_parser("registrations", help="List your registrations")
    sub.add_parser("schemas", help="List available registration schemas")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        client = OSFClient()
    except OSFClientError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    dispatch = {
        "me": cmd_me,
        "nodes": cmd_nodes,
        "node": cmd_node,
        "files": cmd_files,
        "drafts": cmd_drafts,
        "registrations": cmd_registrations,
        "schemas": cmd_schemas,
    }

    try:
        dispatch[args.command](client, args)
    except OSFClientError as e:
        print(f"API Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
