"""Tests for schema type protection and serialization."""

import pytest

from osf_workflow.schema import (
    FreeTextResponse,
    MultiSelectResponse,
    OSFPreregistration,
    RadioResponse,
    ResponseType,
    response_from_dict,
)


class TestTypeProtection:
    def test_free_text_accepts_str(self, parsed_form):
        parsed_form.edit_field("title", "My Study Title")
        fld = parsed_form.get_field("title")
        assert fld.response.text == "My Study Title"
        assert fld.dirty is True

    def test_free_text_rejects_dict(self, parsed_form):
        with pytest.raises(TypeError, match="FREE_TEXT"):
            parsed_form.edit_field("title", {"key": "val"})

    def test_radio_accepts_valid_option(self, parsed_form):
        parsed_form.edit_field("study_type", "Other")
        fld = parsed_form.get_field("study_type")
        assert fld.response.selected == "Other"
        assert fld.dirty is True

    def test_radio_rejects_invalid_option(self, parsed_form):
        with pytest.raises(ValueError, match="Invalid option"):
            parsed_form.edit_field("study_type", "Not a real option")

    def test_radio_rejects_dict(self, parsed_form):
        with pytest.raises(TypeError, match="RADIO"):
            parsed_form.edit_field("study_type", {"Other": True})

    def test_multi_select_accepts_dict(self, parsed_form):
        fld = parsed_form.get_field("blinding")
        first_opt = list(fld.response.selections.keys())[0]
        parsed_form.edit_field("blinding", {first_opt: True})
        assert fld.response.selections[first_opt] is True
        assert fld.dirty is True

    def test_multi_select_rejects_str(self, parsed_form):
        with pytest.raises(TypeError, match="MULTI_SELECT"):
            parsed_form.edit_field("blinding", "some text")

    def test_multi_select_rejects_unknown_label(self, parsed_form):
        with pytest.raises(ValueError, match="Unknown option"):
            parsed_form.edit_field("blinding", {"Fake option": True})

    def test_unknown_slug_raises(self, parsed_form):
        with pytest.raises(KeyError, match="Unknown field"):
            parsed_form.edit_field("nonexistent_field", "value")


class TestSerialization:
    def test_roundtrip_dict(self, parsed_form):
        d = parsed_form.to_dict()
        restored = OSFPreregistration.from_dict(d)
        assert len(restored.all_fields()) == len(parsed_form.all_fields())

    def test_field_dict_roundtrip(self, parsed_form):
        for fld in parsed_form.all_fields():
            d = fld.to_dict()
            assert d["slug"] == fld.slug
            assert d["response_type"] == fld.response_type.value

    def test_response_from_dict(self):
        ft = FreeTextResponse(text="hello").to_dict()
        assert isinstance(response_from_dict(ft), FreeTextResponse)

        radio = RadioResponse(selected="A", options=["A", "B"]).to_dict()
        assert isinstance(response_from_dict(radio), RadioResponse)

        ms = MultiSelectResponse(selections={"X": True, "Y": False}).to_dict()
        assert isinstance(response_from_dict(ms), MultiSelectResponse)


class TestDiff:
    def test_diff_detects_change(self, parsed_form):
        d = parsed_form.to_dict()
        other = OSFPreregistration.from_dict(d)
        other.edit_field("title", "Changed Title")
        diffs = parsed_form.diff(other)
        slugs = [d.slug for d in diffs]
        assert "title" in slugs

    def test_diff_no_changes(self, parsed_form):
        d = parsed_form.to_dict()
        other = OSFPreregistration.from_dict(d)
        diffs = parsed_form.diff(other)
        assert len(diffs) == 0


class TestMarkdown:
    def test_to_markdown(self, parsed_form):
        md = parsed_form.to_markdown()
        assert "# OSF Preregistration" in md
        assert "## Metadata" in md
        assert "### Title*" in md
