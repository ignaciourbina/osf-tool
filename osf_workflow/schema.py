"""Data model for OSF Preregistration forms."""

from __future__ import annotations

import re
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union


class ResponseType(Enum):
    FREE_TEXT = "free_text"
    RADIO = "radio"
    MULTI_SELECT = "multi_select"


# ── Response value objects ──────────────────────────────────────────────


@dataclass
class FreeTextResponse:
    text: str

    def to_dict(self) -> dict:
        return {"type": "free_text", "text": self.text}

    @classmethod
    def from_dict(cls, d: dict) -> FreeTextResponse:
        return cls(text=d["text"])


@dataclass
class RadioResponse:
    selected: Optional[str]
    options: list[str]

    def to_dict(self) -> dict:
        return {
            "type": "radio",
            "selected": self.selected,
            "options": self.options,
        }

    @classmethod
    def from_dict(cls, d: dict) -> RadioResponse:
        return cls(selected=d["selected"], options=d["options"])


@dataclass
class MultiSelectResponse:
    selections: dict[str, bool]

    def to_dict(self) -> dict:
        return {"type": "multi_select", "selections": self.selections}

    @classmethod
    def from_dict(cls, d: dict) -> MultiSelectResponse:
        return cls(selections=d["selections"])


Response = Union[FreeTextResponse, RadioResponse, MultiSelectResponse]


def response_from_dict(d: dict) -> Response:
    rtype = d["type"]
    if rtype == "free_text":
        return FreeTextResponse.from_dict(d)
    if rtype == "radio":
        return RadioResponse.from_dict(d)
    if rtype == "multi_select":
        return MultiSelectResponse.from_dict(d)
    raise ValueError(f"Unknown response type: {rtype}")


# ── Diff ────────────────────────────────────────────────────────────────


@dataclass
class FieldDiff:
    slug: str
    field_name: str
    old_value: str
    new_value: str


# ── Field / Section / Form ──────────────────────────────────────────────


def _slugify(title: str) -> str:
    """Convert heading text to a slug: 'Study design*' → 'study_design'."""
    s = title.strip().rstrip("*").strip()
    s = re.sub(r"[^a-zA-Z0-9\s]", "", s)
    s = re.sub(r"\s+", "_", s.strip())
    return s.lower()


@dataclass
class OSFField:
    slug: str
    title: str
    required: bool
    section_slug: str
    prompt_text: str
    response_type: ResponseType
    response: Response
    table_index: Optional[int]
    para_indices: list[int] = field(default_factory=list)
    dirty: bool = False

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "title": self.title,
            "required": self.required,
            "section_slug": self.section_slug,
            "prompt_text": self.prompt_text,
            "response_type": self.response_type.value,
            "response": self.response.to_dict(),
            "table_index": self.table_index,
            "para_indices": self.para_indices,
        }

    @classmethod
    def from_dict(cls, d: dict) -> OSFField:
        return cls(
            slug=d["slug"],
            title=d["title"],
            required=d["required"],
            section_slug=d["section_slug"],
            prompt_text=d["prompt_text"],
            response_type=ResponseType(d["response_type"]),
            response=response_from_dict(d["response"]),
            table_index=d["table_index"],
            para_indices=d.get("para_indices", []),
        )


@dataclass
class OSFSection:
    slug: str
    title: str
    fields: OrderedDict[str, OSFField] = field(default_factory=OrderedDict)
    para_index: int = 0

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "title": self.title,
            "para_index": self.para_index,
            "fields": {k: v.to_dict() for k, v in self.fields.items()},
        }

    @classmethod
    def from_dict(cls, d: dict) -> OSFSection:
        sec = cls(
            slug=d["slug"],
            title=d["title"],
            para_index=d.get("para_index", 0),
        )
        for k, v in d["fields"].items():
            sec.fields[k] = OSFField.from_dict(v)
        return sec


@dataclass
class OSFFormMetadata:
    template_name: str = "OSF Preregistration"
    source_path: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "template_name": self.template_name,
            "source_path": self.source_path,
        }

    @classmethod
    def from_dict(cls, d: dict) -> OSFFormMetadata:
        return cls(
            template_name=d.get("template_name", "OSF Preregistration"),
            source_path=d.get("source_path"),
        )


class OSFPreregistration:
    """Top-level container for a parsed OSF Preregistration form."""

    def __init__(
        self,
        metadata: OSFFormMetadata,
        sections: OrderedDict[str, OSFSection],
        source_path: Optional[str] = None,
    ):
        self.metadata = metadata
        self.sections = sections
        self.source_path = source_path
        # Build flat slug → field index for fast lookup
        self._field_index: dict[str, OSFField] = {}
        for sec in self.sections.values():
            for fld in sec.fields.values():
                self._field_index[fld.slug] = fld

    # ── Query ───────────────────────────────────────────────────────

    def get_field(self, slug: str) -> OSFField:
        if slug not in self._field_index:
            raise KeyError(
                f"Unknown field '{slug}'. "
                f"Valid slugs: {sorted(self._field_index.keys())}"
            )
        return self._field_index[slug]

    def all_fields(self) -> list[OSFField]:
        return list(self._field_index.values())

    def required_fields(self) -> list[OSFField]:
        return [f for f in self._field_index.values() if f.required]

    def section_names(self) -> list[str]:
        return list(self.sections.keys())

    def summary(self) -> dict:
        fields = self.all_fields()
        by_type = {}
        for f in fields:
            by_type[f.response_type.value] = by_type.get(f.response_type.value, 0) + 1
        return {
            "total_fields": len(fields),
            "required": len(self.required_fields()),
            "optional": len(fields) - len(self.required_fields()),
            "sections": len(self.sections),
            "by_type": by_type,
        }

    # ── Edit (type-checked) ─────────────────────────────────────────

    def edit_field(self, slug: str, value) -> None:
        fld = self.get_field(slug)

        if fld.response_type == ResponseType.FREE_TEXT:
            if not isinstance(value, str):
                raise TypeError(
                    f"Field '{slug}' requires FREE_TEXT (str), "
                    f"got {type(value).__name__}"
                )
            fld.response = FreeTextResponse(text=value)
            fld.dirty = True

        elif fld.response_type == ResponseType.RADIO:
            if not isinstance(value, str):
                raise TypeError(
                    f"Field '{slug}' requires RADIO (str from options), "
                    f"got {type(value).__name__}"
                )
            if not isinstance(fld.response, RadioResponse):
                raise TypeError(f"Internal error: field '{slug}' response is not RadioResponse")
            valid = fld.response.options
            if value not in valid:
                raise ValueError(
                    f"Invalid option '{value}' for field '{slug}'. "
                    f"Valid options: {valid}"
                )
            fld.response = RadioResponse(selected=value, options=valid)
            fld.dirty = True

        elif fld.response_type == ResponseType.MULTI_SELECT:
            if not isinstance(value, dict):
                raise TypeError(
                    f"Field '{slug}' requires MULTI_SELECT (dict[str, bool]), "
                    f"got {type(value).__name__}"
                )
            if not isinstance(fld.response, MultiSelectResponse):
                raise TypeError(f"Internal error: field '{slug}' response is not MultiSelectResponse")
            valid_labels = set(fld.response.selections.keys())
            for k in value:
                if k not in valid_labels:
                    raise ValueError(
                        f"Unknown option '{k}' for field '{slug}'. "
                        f"Valid options: {sorted(valid_labels)}"
                    )
            fld.response.selections.update(value)
            fld.dirty = True

        else:
            raise ValueError(f"Unknown response type: {fld.response_type}")

    # ── Diff ────────────────────────────────────────────────────────

    def diff(self, other: OSFPreregistration) -> list[FieldDiff]:
        diffs: list[FieldDiff] = []
        all_slugs = set(self._field_index.keys()) | set(other._field_index.keys())
        for slug in sorted(all_slugs):
            if slug not in self._field_index:
                diffs.append(FieldDiff(slug, slug, "<absent>", "<present>"))
                continue
            if slug not in other._field_index:
                diffs.append(FieldDiff(slug, slug, "<present>", "<absent>"))
                continue
            old_resp = self._field_index[slug].response.to_dict()
            new_resp = other._field_index[slug].response.to_dict()
            if old_resp != new_resp:
                diffs.append(FieldDiff(
                    slug=slug,
                    field_name=self._field_index[slug].title,
                    old_value=str(old_resp),
                    new_value=str(new_resp),
                ))
        return diffs

    # ── Serialize ───────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "metadata": self.metadata.to_dict(),
            "sections": {k: v.to_dict() for k, v in self.sections.items()},
            "source_path": self.source_path,
        }

    @classmethod
    def from_dict(cls, d: dict) -> OSFPreregistration:
        meta = OSFFormMetadata.from_dict(d["metadata"])
        sections = OrderedDict()
        for k, v in d["sections"].items():
            sections[k] = OSFSection.from_dict(v)
        return cls(
            metadata=meta,
            sections=sections,
            source_path=d.get("source_path"),
        )

    def to_markdown(self) -> str:
        lines = [
            f"# {self.metadata.template_name}",
            "",
        ]
        for sec in self.sections.values():
            lines.append(f"## {sec.title}")
            lines.append("")
            for fld in sec.fields.values():
                req = " (required)" if fld.required else ""
                lines.append(f"### {fld.title}{req}")
                if fld.response_type == ResponseType.FREE_TEXT:
                    text = fld.response.text if isinstance(fld.response, FreeTextResponse) else ""
                    lines.append(f"**Response:** {text or '(empty)'}")
                elif fld.response_type == ResponseType.RADIO:
                    resp = fld.response
                    if isinstance(resp, RadioResponse):
                        for opt in resp.options:
                            marker = "(x)" if opt == resp.selected else "( )"
                            lines.append(f"  {marker} {opt}")
                elif fld.response_type == ResponseType.MULTI_SELECT:
                    resp = fld.response
                    if isinstance(resp, MultiSelectResponse):
                        for label, checked in resp.selections.items():
                            marker = "[x]" if checked else "[ ]"
                            lines.append(f"  {marker} {label}")
                lines.append("")
        return "\n".join(lines)
