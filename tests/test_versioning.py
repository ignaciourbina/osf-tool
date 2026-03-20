"""Tests for versioning (save/load/diff)."""

from osf_workflow import VersionManager


class TestVersioning:
    def test_save_and_load(self, parsed_form, tmp_path):
        vm = VersionManager(tmp_path / "versions")
        record = vm.save(parsed_form, "v1-baseline", "Initial parse")
        assert record.label == "v1-baseline"

        loaded = vm.load("v1-baseline")
        assert len(loaded.all_fields()) == len(parsed_form.all_fields())

    def test_list_versions(self, parsed_form, tmp_path):
        vm = VersionManager(tmp_path / "versions")
        vm.save(parsed_form, "v1")
        vm.save(parsed_form, "v2", "second")
        versions = vm.list_versions()
        assert len(versions) == 2
        assert versions[0].label == "v1"

    def test_diff_versions(self, parsed_form, tmp_path):
        vm = VersionManager(tmp_path / "versions")
        vm.save(parsed_form, "v1")

        parsed_form.edit_field("title", "Changed Title")
        vm.save(parsed_form, "v2")

        diffs = vm.diff("v1", "v2")
        slugs = [d.slug for d in diffs]
        assert "title" in slugs

    def test_load_nonexistent(self, tmp_path):
        vm = VersionManager(tmp_path / "versions")
        import pytest
        with pytest.raises(FileNotFoundError):
            vm.load("nonexistent")
