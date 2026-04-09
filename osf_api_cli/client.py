"""Typed OSF client and resource services."""

from __future__ import annotations

import posixpath
import time
from collections.abc import Iterator
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote, urlencode, urljoin

import requests

from .config import DEFAULT_API_BASE, DEFAULT_TIMEOUT, ResolvedSettings, resolve_settings
from .errors import (
    OSFAuthError,
    OSFConfigError,
    OSFNotFoundError,
    OSFRateLimitError,
    OSFTransportError,
    OSFValidationError,
)
from .models import (
    Contributor,
    DraftRegistration,
    FileEntry,
    Project,
    Registration,
    RegistrationSchema,
    UploadResult,
    User,
    infer_object_id_timestamp,
)

WATERBUTLER_BASE = "https://files.osf.io/v1/"


def _normalize_remote_path(path: str | None) -> str:
    raw_path = (path or "/").strip()
    if not raw_path:
        return "/"
    normalized = posixpath.normpath("/" + raw_path.lstrip("/"))
    return "/" if normalized in {".", "/"} else normalized


def _split_remote_path(path: str) -> tuple[str, str]:
    normalized = _normalize_remote_path(path)
    return posixpath.dirname(normalized) or "/", posixpath.basename(normalized)


class OSFTransport:
    """Low-level transport with retries, pagination, and normalized errors."""

    def __init__(
        self,
        settings: ResolvedSettings,
        *,
        max_retries: int = 2,
        backoff_seconds: float = 0.4,
    ):
        self.settings = settings
        self.base_url = settings.base_url
        self.timeout = settings.timeout
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {settings.token}",
                "Accept": "application/vnd.api+json",
                "Content-Type": "application/vnd.api+json",
            }
        )

    def build_url(self, path: str, *, base_url: str | None = None) -> str:
        root = base_url or self.base_url
        return urljoin(root, path.lstrip("/"))

    def _error_message(self, response: requests.Response) -> str:
        try:
            body = response.json()
        except ValueError:
            text = response.text.strip()
            return text or f"OSF request failed with status {response.status_code}"
        errors = body.get("errors")
        if isinstance(errors, list) and errors:
            detail = errors[0].get("detail") or errors[0].get("title")
            if detail:
                return str(detail)
        return f"OSF request failed with status {response.status_code}"

    def _raise_response_error(self, response: requests.Response) -> None:
        message = self._error_message(response)
        status = response.status_code
        if status in {401, 403}:
            raise OSFAuthError(message, status_code=status)
        if status == 404:
            raise OSFNotFoundError(message, status_code=status)
        if status == 429:
            raise OSFRateLimitError(message, status_code=status)
        if status in {400, 409, 422}:
            raise OSFValidationError(message, status_code=status)
        raise OSFTransportError(message, status_code=status)

    def request(
        self,
        method: str,
        path_or_url: str,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        url = (
            path_or_url
            if path_or_url.startswith(("http://", "https://"))
            else self.build_url(path_or_url, base_url=base_url)
        )
        retryable_method = method.upper() == "GET"
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method,
                    url,
                    timeout=timeout or self.timeout,
                    **kwargs,
                )
            except requests.RequestException as exc:
                last_error = exc
                if retryable_method and attempt < self.max_retries:
                    time.sleep(self.backoff_seconds * (2**attempt))
                    continue
                raise OSFTransportError(str(exc)) from exc

            if response.status_code in {429, 500, 502, 503, 504} and retryable_method and attempt < self.max_retries:
                time.sleep(self.backoff_seconds * (2**attempt))
                continue
            if response.ok:
                return response
            self._raise_response_error(response)

        raise OSFTransportError(str(last_error) if last_error else "OSF request failed")

    def request_json(self, method: str, path_or_url: str, **kwargs: Any) -> dict[str, Any]:
        return self.request(method, path_or_url, **kwargs).json()

    def paginate(self, path: str, **params: Any) -> Iterator[dict[str, Any]]:
        next_url = self.build_url(path)
        page_params: dict[str, Any] = dict(params)
        while next_url:
            body = self.request_json("GET", next_url, params=page_params)
            for item in body.get("data", []):
                yield item
            next_url = body.get("links", {}).get("next")
            page_params = {}


class _Service:
    def __init__(self, client: "OSFClient"):
        self.client = client
        self.transport = client.transport


class UsersService(_Service):
    def me(self, *, force_refresh: bool = False) -> User:
        if force_refresh or self.client._me_cache is None:
            data = self.transport.request_json("GET", "users/me/")["data"]
            self.client._me_cache = User.from_api(data)
        return self.client._me_cache


class ProjectsService(_Service):
    def list(self) -> list[Project]:
        user_id = self.client.users.me().id
        return [
            Project.from_api(item)
            for item in self.transport.paginate(f"users/{user_id}/nodes/")
        ]

    def get(self, node_id: str) -> Project:
        data = self.transport.request_json("GET", f"nodes/{node_id}/")["data"]
        return Project.from_api(data)

    def create(
        self,
        *,
        title: str,
        description: str = "",
        public: bool = False,
        category: str = "project",
        tags: list[str] | None = None,
    ) -> Project:
        payload = {
            "data": {
                "type": "nodes",
                "attributes": {
                    "title": title,
                    "description": description,
                    "public": public,
                    "category": category,
                },
            }
        }
        if tags:
            payload["data"]["attributes"]["tags"] = tags
        data = self.transport.request_json("POST", "nodes/", json=payload)["data"]
        return Project.from_api(data)

    def update(self, node_id: str, **attrs: Any) -> Project:
        payload = {"data": {"type": "nodes", "id": node_id, "attributes": attrs}}
        data = self.transport.request_json("PATCH", f"nodes/{node_id}/", json=payload)["data"]
        return Project.from_api(data)

    def delete(self, node_id: str) -> None:
        self.transport.request("DELETE", f"nodes/{node_id}/")


class FilesService(_Service):
    def list_providers(self, node_id: str) -> list[dict[str, Any]]:
        return list(self.transport.paginate(f"nodes/{node_id}/files/"))

    def list_provider_names(self, node_id: str) -> list[str]:
        names: list[str] = []
        for item in self.list_providers(node_id):
            attrs = item.get("attributes", {})
            provider = attrs.get("name") or item.get("id")
            if isinstance(provider, str) and provider and provider not in names:
                names.append(provider)
        return names

    def _list_provider_path(
        self,
        node_id: str,
        *,
        provider: str,
        path: str = "/",
    ) -> list[FileEntry]:
        normalized = _normalize_remote_path(path)
        provider_path = quote(normalized.lstrip("/"), safe="/")
        endpoint = f"nodes/{node_id}/files/{provider}/"
        if provider_path:
            endpoint = f"{endpoint}{provider_path}"
        return [
            FileEntry.from_api(item, provider=provider)
            for item in self.transport.paginate(endpoint)
        ]

    def list(
        self,
        node_id: str,
        *,
        provider: str = "osfstorage",
        path: str = "/",
        recursive: bool = False,
    ) -> list[FileEntry]:
        if not recursive:
            return self._list_provider_path(node_id, provider=provider, path=path)
        entries: list[FileEntry] = []
        queue = [_normalize_remote_path(path)]
        seen_paths: set[str] = set()
        while queue:
            current = queue.pop(0)
            if current in seen_paths:
                continue
            seen_paths.add(current)
            for entry in self._list_provider_path(node_id, provider=provider, path=current):
                entries.append(entry)
                if entry.kind == "folder" and entry.materialized_path:
                    folder_path = _normalize_remote_path(entry.materialized_path)
                    if folder_path not in seen_paths:
                        queue.append(folder_path)
        return entries

    def list_all_providers(
        self,
        node_id: str,
        *,
        path: str = "/",
        recursive: bool = False,
    ) -> list[FileEntry]:
        entries: list[FileEntry] = []
        seen: set[tuple[str | None, str, str, str]] = set()
        for provider in self.list_provider_names(node_id):
            for entry in self.list(node_id, provider=provider, path=path, recursive=recursive):
                identity = (
                    entry.provider,
                    entry.materialized_path or entry.name,
                    entry.kind,
                    entry.id,
                )
                if identity in seen:
                    continue
                seen.add(identity)
                entries.append(entry)
        return entries

    def get(
        self,
        node_id: str,
        remote_path: str,
        *,
        provider: str = "osfstorage",
    ) -> FileEntry:
        normalized = _normalize_remote_path(remote_path)
        if normalized == "/":
            raise OSFValidationError("remote_path must not be '/'")
        parent_path, name = _split_remote_path(normalized)
        for item in self.list(node_id, provider=provider, path=parent_path):
            if item.materialized_path and _normalize_remote_path(item.materialized_path) == normalized:
                return item
            if item.name == name:
                return item
        raise OSFNotFoundError(f"No OSF file found at '{normalized}'", status_code=404)

    def upload(
        self,
        node_id: str,
        local_path: str | Path,
        *,
        provider: str = "osfstorage",
        remote_name: str | None = None,
        remote_path: str | None = None,
    ) -> UploadResult:
        if remote_name and remote_path:
            raise OSFValidationError("Use either remote_name or remote_path, not both.")
        source_path = Path(local_path)
        target_path = remote_path or remote_name or source_path.name
        parent_path, name = _split_remote_path(target_path)
        folder_path = quote(parent_path.lstrip("/"), safe="/")
        url = f"{WATERBUTLER_BASE}resources/{node_id}/providers/{provider}/"
        if folder_path:
            url = f"{url}{folder_path}/"
        url = f"{url}?{urlencode({'kind': 'file', 'name': name})}"
        with source_path.open("rb") as handle:
            data = self.transport.request_json(
                "PUT",
                url,
                data=handle,
                headers={
                    "Authorization": f"Bearer {self.client.settings.token}",
                    "Content-Type": "application/octet-stream",
                },
            )
        return UploadResult(
            name=name,
            provider=provider,
            remote_path=_normalize_remote_path(target_path),
            raw=data,
        )

    def download(self, download_url: str, dest: str | Path) -> Path:
        destination = Path(dest)
        response = self.transport.request("GET", download_url, stream=True)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    handle.write(chunk)
        return destination

    def download_by_path(
        self,
        node_id: str,
        remote_path: str,
        *,
        dest: str | Path | None = None,
        provider: str = "osfstorage",
    ) -> Path:
        entry = self.get(node_id, remote_path, provider=provider)
        if not entry.download_url:
            raise OSFValidationError(f"No download link available for '{remote_path}'")
        destination = Path(dest) if dest else Path(PurePosixPath(remote_path).name)
        return self.download(entry.download_url, destination)


class DraftsService(_Service):
    def list(self, node_id: str) -> list[DraftRegistration]:
        project = self.client.projects.get(node_id)
        return [
            DraftRegistration.from_api(item, project=project)
            for item in self.transport.paginate(f"nodes/{node_id}/draft_registrations/")
        ]

    def get(self, draft_id: str) -> DraftRegistration:
        data = self.transport.request_json("GET", f"draft_registrations/{draft_id}/")["data"]
        related_project = data.get("relationships", {}).get("branched_from", {}).get("data", {})
        project: Project | None = None
        if related_project.get("id"):
            try:
                project = self.client.projects.get(related_project["id"])
            except OSFTransportError:
                project = None
        return DraftRegistration.from_api(data, project=project)

    def create(
        self,
        node_id: str,
        *,
        schema_id: str,
        registration_metadata: dict[str, Any] | None = None,
    ) -> DraftRegistration:
        payload = {
            "data": {
                "type": "draft_registrations",
                "relationships": {
                    "registration_schema": {
                        "data": {"type": "registration_schemas", "id": schema_id}
                    }
                },
            }
        }
        if registration_metadata:
            payload["data"]["attributes"] = {
                "registration_metadata": registration_metadata
            }
        data = self.transport.request_json(
            "POST",
            f"nodes/{node_id}/draft_registrations/",
            json=payload,
        )["data"]
        return DraftRegistration.from_api(data, project=self.client.projects.get(node_id))

    def list_all(self) -> list[DraftRegistration]:
        items: list[DraftRegistration] = []
        for project in self.client.projects.list():
            for item in self.transport.paginate(f"nodes/{project.id}/draft_registrations/"):
                items.append(DraftRegistration.from_api(item, project=project))
        items.sort(key=lambda item: item.date_created or item.date_created_inferred or "", reverse=True)
        return items

    def update_metadata(
        self,
        draft_id: str,
        *,
        registration_metadata: dict[str, Any] | None = None,
        registration_responses: dict[str, Any] | None = None,
    ) -> DraftRegistration:
        attributes: dict[str, Any] = {}
        if registration_metadata is not None:
            attributes["registration_metadata"] = registration_metadata
        if registration_responses is not None:
            attributes["registration_responses"] = registration_responses
        if not attributes:
            raise ValueError("one of registration_metadata or registration_responses is required")
        payload = {
            "data": {
                "type": "draft_registrations",
                "id": draft_id,
                "attributes": attributes,
            }
        }
        data = self.transport.request_json(
            "PATCH",
            f"draft_registrations/{draft_id}/",
            json=payload,
        )["data"]
        related_project = data.get("relationships", {}).get("branched_from", {}).get("data", {})
        project: Project | None = None
        if related_project.get("id"):
            try:
                project = self.client.projects.get(related_project["id"])
            except OSFTransportError:
                project = None
        return DraftRegistration.from_api(data, project=project)


class RegistrationsService(_Service):
    def list(self, node_id: str) -> list[Registration]:
        project = self.client.projects.get(node_id)
        return [
            Registration.from_api(item, project=project)
            for item in self.transport.paginate(f"nodes/{node_id}/registrations/")
        ]

    def get(self, registration_id: str) -> Registration:
        data = self.transport.request_json("GET", f"registrations/{registration_id}/")["data"]
        return Registration.from_api(data)

    def list_all(self) -> list[Registration]:
        items: list[Registration] = []
        for project in self.client.projects.list():
            for item in self.transport.paginate(f"nodes/{project.id}/registrations/"):
                items.append(Registration.from_api(item, project=project))
        items.sort(key=lambda item: item.date_registered or item.date_created or "", reverse=True)
        return items


class ContributorsService(_Service):
    def list(self, node_id: str, *, embed_users: bool = True) -> list[Contributor]:
        params = {"embed": "users"} if embed_users else {}
        return [
            Contributor.from_api(item)
            for item in self.transport.paginate(f"nodes/{node_id}/contributors/", **params)
        ]


class SchemasService(_Service):
    def list(self) -> list[RegistrationSchema]:
        return [
            RegistrationSchema.from_api(item)
            for item in self.transport.paginate("schemas/registrations/")
        ]


class OSFClient:
    """Primary OSF client exposing typed services and compatibility helpers."""

    def __init__(
        self,
        *,
        token: str | None = None,
        profile: str | None = None,
        config_path: str | Path | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        legacy_credentials_path: str | Path | None = None,
        settings: ResolvedSettings | None = None,
    ):
        self.settings = settings or resolve_settings(
            token=token,
            profile=profile,
            config_path=config_path,
            base_url=base_url,
            timeout=timeout,
            legacy_credentials_path=legacy_credentials_path,
        )
        self.transport = OSFTransport(self.settings)
        self._me_cache: User | None = None
        self.users = UsersService(self)
        self.projects = ProjectsService(self)
        self.files = FilesService(self)
        self.drafts = DraftsService(self)
        self.registrations = RegistrationsService(self)
        self.contributors = ContributorsService(self)
        self.schemas = SchemasService(self)

    def whoami(self) -> User:
        return self.users.me()

    def me(self, *, force_refresh: bool = False) -> User:
        return self.users.me(force_refresh=force_refresh)

    def list_projects(self) -> list[Project]:
        return self.projects.list()

    def list_nodes(self) -> list[Project]:
        return self.list_projects()

    def get_project(self, node_id: str) -> Project:
        return self.projects.get(node_id)

    def get_node(self, node_id: str) -> Project:
        return self.get_project(node_id)

    def create_project(self, **kwargs: Any) -> Project:
        return self.projects.create(**kwargs)

    def update_project(self, node_id: str, **attrs: Any) -> Project:
        return self.projects.update(node_id, **attrs)

    def delete_project(self, node_id: str) -> None:
        self.projects.delete(node_id)

    def list_storage_providers(self, node_id: str) -> list[dict[str, Any]]:
        return self.files.list_providers(node_id)

    def list_file_providers(self, node_id: str) -> list[str]:
        return self.files.list_provider_names(node_id)

    def list_files(
        self,
        node_id: str,
        provider: str = "osfstorage",
        path: str = "/",
        recursive: bool = False,
    ) -> list[FileEntry]:
        return self.files.list(node_id, provider=provider, path=path, recursive=recursive)

    def list_node_files(
        self,
        node_id: str,
        provider: str = "osfstorage",
        path: str = "/",
        recursive: bool = False,
    ) -> list[FileEntry]:
        return self.list_files(node_id, provider=provider, path=path, recursive=recursive)

    def list_files_all_providers(
        self,
        node_id: str,
        path: str = "/",
        recursive: bool = False,
    ) -> list[FileEntry]:
        return self.files.list_all_providers(node_id, path=path, recursive=recursive)

    def get_file(self, node_id: str, remote_path: str, provider: str = "osfstorage") -> FileEntry:
        return self.files.get(node_id, remote_path, provider=provider)

    def upload_file(
        self,
        node_id: str,
        local_path: str | Path,
        remote_name: str | None = None,
        provider: str = "osfstorage",
        remote_path: str | None = None,
    ) -> UploadResult:
        return self.files.upload(
            node_id,
            local_path,
            provider=provider,
            remote_name=remote_name,
            remote_path=remote_path,
        )

    def download_file(self, download_url: str, dest: str | Path) -> Path:
        return self.files.download(download_url, dest)

    def download_file_by_path(
        self,
        node_id: str,
        remote_path: str,
        dest: str | Path | None = None,
        provider: str = "osfstorage",
    ) -> Path:
        return self.files.download_by_path(node_id, remote_path, dest=dest, provider=provider)

    def summarize_draft_registration(
        self,
        draft: dict[str, Any] | DraftRegistration,
        *,
        project: dict[str, Any] | Project | None = None,
    ) -> DraftRegistration:
        if isinstance(draft, DraftRegistration):
            return draft
        project_model: Project | None
        if isinstance(project, Project) or project is None:
            project_model = project
        else:
            project_model = Project.from_api(project)
        return DraftRegistration.from_api(draft, project=project_model)

    def list_draft_registrations(self, node_id: str) -> list[DraftRegistration]:
        return self.drafts.list(node_id)

    def get_draft_registration(self, draft_id: str) -> DraftRegistration:
        return self.drafts.get(draft_id)

    def create_draft_registration(
        self,
        node_id: str | None = None,
        schema_id: str | None = None,
        registration_metadata: dict[str, Any] | None = None,
        title: str | None = None,
        description: str | None = None,
    ) -> DraftRegistration:
        if not schema_id:
            raise ValueError("schema_id is required")
        if node_id is None:
            payload = {
                "data": {
                    "type": "draft_registrations",
                    "relationships": {
                        "registration_schema": {
                            "data": {"type": "registration_schemas", "id": schema_id}
                        }
                    },
                    "attributes": {},
                }
            }
            if title:
                payload["data"]["attributes"]["title"] = title
            if description:
                payload["data"]["attributes"]["description"] = description
            if registration_metadata:
                payload["data"]["attributes"]["registration_metadata"] = registration_metadata
            data = self.transport.request_json("POST", "draft_registrations/", json=payload)["data"]
            return DraftRegistration.from_api(data)
        return self.drafts.create(
            node_id,
            schema_id=schema_id,
            registration_metadata=registration_metadata,
        )

    def list_all_draft_registrations(self) -> list[DraftRegistration]:
        return self.drafts.list_all()

    def update_draft_registration_metadata(
        self,
        draft_id: str,
        registration_metadata: dict[str, Any],
    ) -> DraftRegistration:
        return self.drafts.update_metadata(
            draft_id,
            registration_metadata=registration_metadata,
        )

    def update_draft_registration_responses(
        self,
        draft_id: str,
        registration_responses: dict[str, Any],
    ) -> DraftRegistration:
        return self.drafts.update_metadata(
            draft_id,
            registration_responses=registration_responses,
        )

    def update_draft_registration(self, draft_id: str, **attrs: Any) -> DraftRegistration:
        metadata = attrs.pop("registration_metadata", None)
        responses = attrs.pop("registration_responses", None)
        if attrs:
            payload = {
                "data": {
                    "type": "draft_registrations",
                    "id": draft_id,
                    "attributes": attrs,
                }
            }
            data = self.transport.request_json(
                "PATCH",
                f"draft_registrations/{draft_id}/",
                json=payload,
            )["data"]
            return DraftRegistration.from_api(data)
        return self.drafts.update_metadata(
            draft_id,
            registration_metadata=metadata,
            registration_responses=responses,
        )

    def list_registrations(self, node_id: str) -> list[Registration]:
        return self.registrations.list(node_id)

    def get_registration(self, registration_id: str) -> Registration:
        return self.registrations.get(registration_id)

    def list_all_registrations(self) -> list[Registration]:
        return self.registrations.list_all()

    def list_schemas(self) -> list[RegistrationSchema]:
        return self.schemas.list()

    def list_contributors(self, node_id: str, *, embed_users: bool = True) -> list[Contributor]:
        return self.contributors.list(node_id, embed_users=embed_users)


__all__ = [
    "DEFAULT_API_BASE",
    "DEFAULT_TIMEOUT",
    "WATERBUTLER_BASE",
    "OSFClient",
    "OSFConfigError",
    "infer_object_id_timestamp",
]
