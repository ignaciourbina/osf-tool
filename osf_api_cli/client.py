"""OSF API v2 client — thin wrapper over requests with JSON-API handling."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterator

import requests
from dotenv import load_dotenv

# Load .env from project root
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)

_DEFAULT_BASE = "https://api.osf.io/v2"


class OSFClientError(Exception):
    """Raised when the OSF API returns an error response."""

    def __init__(self, status_code: int, detail: str, response: requests.Response | None = None):
        self.status_code = status_code
        self.detail = detail
        self.response = response
        super().__init__(f"HTTP {status_code}: {detail}")


class OSFClient:
    """Authenticated client for the OSF API v2 (JSON-API)."""

    def __init__(self, token: str | None = None, base_url: str | None = None):
        self.token = token or os.environ.get("OSF_TOKEN")
        if not self.token:
            raise OSFClientError(0, "No OSF token provided. Set OSF_TOKEN in .env or pass token=")
        self.base_url = (base_url or os.environ.get("OSF_API_BASE") or _DEFAULT_BASE).rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
        })

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def _url(self, path: str) -> str:
        path = path.strip("/")
        return f"{self.base_url}/{path}/"

    def _handle_response(self, resp: requests.Response) -> dict:
        if resp.status_code == 204:
            return {}
        if resp.status_code >= 400:
            try:
                body = resp.json()
                errors = body.get("errors", [])
                detail = "; ".join(e.get("detail", str(e)) for e in errors) if errors else resp.text
            except ValueError:
                detail = resp.text
            raise OSFClientError(resp.status_code, detail, resp)
        return resp.json()

    def get(self, path: str, params: dict | None = None) -> dict:
        resp = self._session.get(self._url(path), params=params)
        return self._handle_response(resp)

    def post(self, path: str, payload: dict) -> dict:
        resp = self._session.post(self._url(path), json=payload)
        return self._handle_response(resp)

    def patch(self, path: str, payload: dict) -> dict:
        resp = self._session.patch(self._url(path), json=payload)
        return self._handle_response(resp)

    def put(self, path: str, payload: dict) -> dict:
        resp = self._session.put(self._url(path), json=payload)
        return self._handle_response(resp)

    def delete(self, path: str) -> dict:
        resp = self._session.delete(self._url(path))
        return self._handle_response(resp)

    def paginate(self, path: str, params: dict | None = None) -> Iterator[dict]:
        """Yield every resource across all pages."""
        url = self._url(path)
        while url:
            resp = self._session.get(url, params=params)
            body = self._handle_response(resp)
            yield from body.get("data", [])
            url = body.get("links", {}).get("next")
            params = None  # params only on first request; next URL is absolute

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def me(self) -> dict:
        """Get the authenticated user's profile."""
        return self.get("users/me")["data"]

    def get_user(self, user_id: str) -> dict:
        return self.get(f"users/{user_id}")["data"]

    # ------------------------------------------------------------------
    # Nodes (projects / components)
    # ------------------------------------------------------------------

    def list_my_nodes(self, user_id: str | None = None) -> list[dict]:
        """List the authenticated user's own nodes (not all public nodes)."""
        uid = user_id or self.me()["id"]
        return list(self.paginate(f"users/{uid}/nodes"))

    def list_nodes(self, **filters: str) -> list[dict]:
        """Search all nodes with filters. Without filters this paginates ALL public nodes — use list_my_nodes() instead."""
        if not filters:
            return self.list_my_nodes()
        params = {f"filter[{k}]": v for k, v in filters.items()}
        return list(self.paginate("nodes", params or None))

    def get_node(self, node_id: str, embed: list[str] | None = None) -> dict:
        params: dict[str, str] = {}
        if embed:
            for e in embed:
                params.setdefault("embed", e)
            # JSON-API allows repeated embed params; use comma-sep as fallback
            params = {"embed": ",".join(embed)} if len(embed) > 1 else params
        return self.get(f"nodes/{node_id}", params or None)["data"]

    def create_node(self, title: str, category: str = "project", description: str = "") -> dict:
        payload = {
            "data": {
                "type": "nodes",
                "attributes": {
                    "title": title,
                    "category": category,
                    "description": description,
                },
            }
        }
        return self.post("nodes", payload)["data"]

    def update_node(self, node_id: str, **attrs: Any) -> dict:
        payload = {
            "data": {
                "type": "nodes",
                "id": node_id,
                "attributes": attrs,
            }
        }
        return self.patch(f"nodes/{node_id}", payload)["data"]

    def delete_node(self, node_id: str) -> None:
        self.delete(f"nodes/{node_id}")

    # ------------------------------------------------------------------
    # Node children / contributors / files
    # ------------------------------------------------------------------

    def list_node_children(self, node_id: str) -> list[dict]:
        return list(self.paginate(f"nodes/{node_id}/children"))

    def list_node_contributors(self, node_id: str) -> list[dict]:
        return list(self.paginate(f"nodes/{node_id}/contributors"))

    def list_node_files(self, node_id: str, provider: str = "osfstorage") -> list[dict]:
        return list(self.paginate(f"nodes/{node_id}/files/{provider}"))

    # ------------------------------------------------------------------
    # Files
    # ------------------------------------------------------------------

    def get_file(self, file_id: str) -> dict:
        return self.get(f"files/{file_id}")["data"]

    def download_file(self, file_id: str) -> bytes:
        """Download file contents by file ID."""
        meta = self.get_file(file_id)
        download_url = meta["links"]["download"]
        resp = self._session.get(download_url)
        if resp.status_code >= 400:
            raise OSFClientError(resp.status_code, f"Download failed: {resp.text}", resp)
        return resp.content

    def upload_file(self, node_id: str, name: str, data: bytes,
                    provider: str = "osfstorage") -> dict:
        """Upload a file to a node's storage provider."""
        upload_url = f"{self.base_url}/nodes/{node_id}/files/{provider}/"
        # Get the upload link from the provider listing
        resp = self._session.get(upload_url)
        body = self._handle_response(resp)
        upload_link = body["data"][0]["links"]["upload"] if body.get("data") else None
        if not upload_link:
            # Construct Waterbutler URL directly
            upload_link = f"https://files.osf.io/v1/resources/{node_id}/providers/{provider}/"

        resp = self._session.put(
            upload_link,
            params={"kind": "file", "name": name},
            data=data,
            headers={"Content-Type": "application/octet-stream"},
        )
        if resp.status_code >= 400:
            raise OSFClientError(resp.status_code, f"Upload failed: {resp.text}", resp)
        return resp.json()

    # ------------------------------------------------------------------
    # Draft Registrations
    # ------------------------------------------------------------------

    def list_draft_registrations(self) -> list[dict]:
        return list(self.paginate("draft_registrations"))

    def get_draft_registration(self, draft_id: str) -> dict:
        return self.get(f"draft_registrations/{draft_id}")["data"]

    def create_draft_registration(
        self,
        schema_id: str,
        title: str = "",
        description: str = "",
        node_id: str | None = None,
    ) -> dict:
        attrs: dict[str, Any] = {}
        if title:
            attrs["title"] = title
        if description:
            attrs["description"] = description

        relationships: dict[str, Any] = {
            "registration_schema": {
                "data": {"type": "registration-schemas", "id": schema_id}
            }
        }
        if node_id:
            relationships["branched_from"] = {
                "data": {"type": "nodes", "id": node_id}
            }

        payload = {
            "data": {
                "type": "draft-registrations",
                "attributes": attrs,
                "relationships": relationships,
            }
        }
        return self.post("draft_registrations", payload)["data"]

    def update_draft_registration(self, draft_id: str, **attrs: Any) -> dict:
        payload = {
            "data": {
                "type": "draft-registrations",
                "id": draft_id,
                "attributes": attrs,
            }
        }
        return self.patch(f"draft_registrations/{draft_id}", payload)["data"]

    # ------------------------------------------------------------------
    # Registrations
    # ------------------------------------------------------------------

    def list_registrations(self, **filters: str) -> list[dict]:
        params = {f"filter[{k}]": v for k, v in filters.items()}
        return list(self.paginate("registrations", params or None))

    def get_registration(self, reg_id: str) -> dict:
        return self.get(f"registrations/{reg_id}")["data"]

    def list_user_registrations(self, user_id: str | None = None) -> list[dict]:
        uid = user_id or self.me()["id"]
        return list(self.paginate(f"users/{uid}/registrations"))

    # ------------------------------------------------------------------
    # Registration Schemas
    # ------------------------------------------------------------------

    def list_registration_schemas(self) -> list[dict]:
        return list(self.paginate("schemas/registrations"))

    def get_registration_schema(self, schema_id: str) -> dict:
        return self.get(f"schemas/registrations/{schema_id}")["data"]

    # ------------------------------------------------------------------
    # Institutions
    # ------------------------------------------------------------------

    def list_user_institutions(self, user_id: str | None = None) -> list[dict]:
        uid = user_id or self.me()["id"]
        return list(self.paginate(f"users/{uid}/institutions"))

    # ------------------------------------------------------------------
    # Preprints
    # ------------------------------------------------------------------

    def list_user_preprints(self, user_id: str | None = None) -> list[dict]:
        uid = user_id or self.me()["id"]
        return list(self.paginate(f"users/{uid}/preprints"))
