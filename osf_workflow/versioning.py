"""Versioning: save/load/diff OSFPreregistration snapshots as JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Union

from .schema import FieldDiff, OSFPreregistration


@dataclass
class VersionRecord:
    label: str
    timestamp: str
    notes: str
    filepath: str


class VersionManager:
    """Manage versioned JSON snapshots of OSFPreregistration objects."""

    def __init__(self, versions_dir: Union[str, Path]):
        self.versions_dir = Path(versions_dir)
        self.versions_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        form: OSFPreregistration,
        label: str,
        notes: str = "",
    ) -> VersionRecord:
        """Serialize form to a JSON snapshot."""
        ts = datetime.now(timezone.utc).isoformat()
        filepath = self.versions_dir / f"{label}.json"

        payload = {
            "label": label,
            "timestamp": ts,
            "notes": notes,
            "form": form.to_dict(),
        }

        filepath.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

        return VersionRecord(
            label=label,
            timestamp=ts,
            notes=notes,
            filepath=str(filepath),
        )

    def load(self, label: str) -> OSFPreregistration:
        """Deserialize a form from a JSON snapshot."""
        filepath = self.versions_dir / f"{label}.json"
        if not filepath.exists():
            raise FileNotFoundError(f"No snapshot found for label '{label}'")

        payload = json.loads(filepath.read_text())
        return OSFPreregistration.from_dict(payload["form"])

    def list_versions(self) -> list[VersionRecord]:
        """Return all saved versions, sorted by timestamp."""
        records = []
        for p in sorted(self.versions_dir.glob("*.json")):
            payload = json.loads(p.read_text())
            records.append(
                VersionRecord(
                    label=payload["label"],
                    timestamp=payload["timestamp"],
                    notes=payload.get("notes", ""),
                    filepath=str(p),
                )
            )
        records.sort(key=lambda r: r.timestamp)
        return records

    def diff(self, label_a: str, label_b: str) -> list[FieldDiff]:
        """Compare two snapshots and return field-level diffs."""
        form_a = self.load(label_a)
        form_b = self.load(label_b)
        return form_a.diff(form_b)
