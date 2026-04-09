"""Typed OSF resource models."""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from datetime import UTC, datetime
from typing import Any


def infer_object_id_timestamp(resource_id: str | None) -> str | None:
    """Infer a UTC creation timestamp from a Mongo-style ObjectId."""
    if not resource_id or len(resource_id) < 8:
        return None
    prefix = resource_id[:8]
    if any(ch not in "0123456789abcdefABCDEF" for ch in prefix):
        return None
    try:
        timestamp = int(prefix, 16)
    except ValueError:
        return None
    return datetime.fromtimestamp(timestamp, tz=UTC).isoformat().replace("+00:00", "Z")


def _serialize(value: Any, *, include_raw: bool) -> Any:
    if is_dataclass(value):
        data: dict[str, Any] = {}
        for info in fields(value):
            if info.name == "raw" and not include_raw:
                continue
            data[info.name] = _serialize(getattr(value, info.name), include_raw=include_raw)
        return data
    if isinstance(value, list):
        return [_serialize(item, include_raw=include_raw) for item in value]
    if isinstance(value, tuple):
        return [_serialize(item, include_raw=include_raw) for item in value]
    if isinstance(value, dict):
        return {
            key: _serialize(item, include_raw=include_raw)
            for key, item in value.items()
        }
    return value


class SerializableModel:
    def to_dict(self, *, include_raw: bool = False) -> dict[str, Any]:
        return _serialize(self, include_raw=include_raw)


@dataclass(slots=True)
class User(SerializableModel):
    id: str
    full_name: str
    email: str | None
    profile_url: str | None
    employment: list[dict[str, Any]]
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "User":
        attrs = data.get("attributes", {})
        links = data.get("links", {})
        employment = attrs.get("employment", [])
        if not isinstance(employment, list):
            employment = []
        return cls(
            id=data["id"],
            full_name=attrs.get("full_name") or data["id"],
            email=attrs.get("email"),
            profile_url=links.get("html"),
            employment=employment,
            raw=data,
        )


@dataclass(slots=True)
class Project(SerializableModel):
    id: str
    title: str
    description: str | None
    category: str | None
    public: bool
    tags: list[str]
    date_created: str | None
    date_modified: str | None
    url: str | None
    api_url: str | None
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Project":
        attrs = data.get("attributes", {})
        links = data.get("links", {})
        return cls(
            id=data["id"],
            title=attrs.get("title") or data["id"],
            description=attrs.get("description"),
            category=attrs.get("category"),
            public=bool(attrs.get("public")),
            tags=list(attrs.get("tags", [])),
            date_created=attrs.get("date_created"),
            date_modified=attrs.get("date_modified"),
            url=links.get("html"),
            api_url=links.get("self"),
            raw=data,
        )


@dataclass(slots=True)
class FileEntry(SerializableModel):
    id: str
    name: str
    kind: str
    provider: str | None
    size: int | None
    materialized_path: str | None
    date_modified: str | None
    download_url: str | None
    url: str | None
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any], *, provider: str | None = None) -> "FileEntry":
        attrs = data.get("attributes", {})
        links = data.get("links", {})
        name = attrs.get("name") or attrs.get("materialized_path") or data["id"]
        return cls(
            id=data["id"],
            name=name,
            kind=attrs.get("kind", "?"),
            provider=provider,
            size=attrs.get("size"),
            materialized_path=attrs.get("materialized_path"),
            date_modified=attrs.get("date_modified"),
            download_url=links.get("download"),
            url=links.get("html") or links.get("move"),
            raw=data,
        )


@dataclass(slots=True)
class UploadResult(SerializableModel):
    name: str
    provider: str
    remote_path: str
    raw: dict[str, Any] = field(repr=False)


@dataclass(slots=True)
class DraftRegistration(SerializableModel):
    id: str
    title: str | None
    title_display: str
    date_created: str | None
    date_modified: str | None
    date_created_inferred: str | None
    date_source: str
    url: str | None
    api_url: str | None
    project_id: str | None
    project_title: str | None
    project_url: str | None
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_api(
        cls,
        data: dict[str, Any],
        *,
        project: Project | None = None,
    ) -> "DraftRegistration":
        attrs = data.get("attributes", {})
        links = data.get("links", {})
        date_created = attrs.get("date_created") or attrs.get("datetime_initiated")
        date_modified = attrs.get("date_modified") or attrs.get("datetime_updated")
        inferred = None if date_created else infer_object_id_timestamp(data.get("id"))
        if date_created or date_modified:
            date_source = "api"
        elif inferred:
            date_source = "inferred_from_id"
        else:
            date_source = "missing"
        title = attrs.get("title")
        return cls(
            id=data["id"],
            title=title,
            title_display=title or "(untitled)",
            date_created=date_created,
            date_modified=date_modified,
            date_created_inferred=inferred,
            date_source=date_source,
            url=links.get("html"),
            api_url=links.get("self"),
            project_id=project.id if project else None,
            project_title=project.title if project else None,
            project_url=project.url if project else None,
            raw=data,
        )


@dataclass(slots=True)
class Registration(SerializableModel):
    id: str
    title: str | None
    title_display: str
    date_registered: str | None
    date_created: str | None
    date_modified: str | None
    url: str | None
    api_url: str | None
    project_id: str | None
    project_title: str | None
    project_url: str | None
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_api(
        cls,
        data: dict[str, Any],
        *,
        project: Project | None = None,
    ) -> "Registration":
        attrs = data.get("attributes", {})
        links = data.get("links", {})
        title = attrs.get("title")
        return cls(
            id=data["id"],
            title=title,
            title_display=title or "(untitled)",
            date_registered=attrs.get("date_registered"),
            date_created=attrs.get("date_created"),
            date_modified=attrs.get("date_modified"),
            url=links.get("html"),
            api_url=links.get("self"),
            project_id=project.id if project else None,
            project_title=project.title if project else None,
            project_url=project.url if project else None,
            raw=data,
        )


@dataclass(slots=True)
class Contributor(SerializableModel):
    id: str
    name: str
    permission: str | None
    bibliographic: bool
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Contributor":
        attrs = data.get("attributes", {})
        user_data = data.get("embeds", {}).get("users", {}).get("data", {})
        name = user_data.get("attributes", {}).get("full_name") or data["id"]
        return cls(
            id=data["id"],
            name=name,
            permission=attrs.get("permission"),
            bibliographic=bool(attrs.get("bibliographic")),
            raw=data,
        )


@dataclass(slots=True)
class RegistrationSchema(SerializableModel):
    id: str
    name: str
    schema_version: str
    raw: dict[str, Any] = field(repr=False)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "RegistrationSchema":
        attrs = data.get("attributes", {})
        return cls(
            id=data["id"],
            name=attrs.get("name", "?"),
            schema_version=str(attrs.get("schema_version", "")),
            raw=data,
        )
