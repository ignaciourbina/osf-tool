"""Tests for the OSF form parser."""

from osf_workflow.schema import ResponseType


class TestParserStructure:
    def test_sections_count(self, parsed_form):
        assert len(parsed_form.sections) == 7

    def test_section_names(self, parsed_form):
        expected = [
            "metadata",
            "study_information",
            "design_plan",
            "sampling_plan",
            "variables",
            "analysis_plan",
            "other",
        ]
        assert list(parsed_form.sections.keys()) == expected

    def test_total_fields(self, parsed_form):
        fields = parsed_form.all_fields()
        # 28 fields total (some may vary if the doc has extra Heading 3s)
        assert len(fields) >= 26
        assert len(fields) <= 30

    def test_required_fields(self, parsed_form):
        required = parsed_form.required_fields()
        assert len(required) >= 12


class TestFieldTypes:
    def test_free_text_fields(self, parsed_form):
        for slug in ["title", "description", "hypotheses", "study_design", "sample_size"]:
            fld = parsed_form.get_field(slug)
            assert fld.response_type == ResponseType.FREE_TEXT, f"{slug} should be FREE_TEXT"

    def test_radio_fields(self, parsed_form):
        for slug in ["license", "study_type", "existing_data"]:
            fld = parsed_form.get_field(slug)
            assert fld.response_type == ResponseType.RADIO, f"{slug} should be RADIO"

    def test_multi_select_field(self, parsed_form):
        fld = parsed_form.get_field("blinding")
        assert fld.response_type == ResponseType.MULTI_SELECT

    def test_radio_options_populated(self, parsed_form):
        fld = parsed_form.get_field("study_type")
        assert len(fld.response.options) == 4
        assert fld.response.options[0].startswith("Experiment")

    def test_license_options_populated(self, parsed_form):
        fld = parsed_form.get_field("license")
        assert len(fld.response.options) == 17

    def test_existing_data_options(self, parsed_form):
        fld = parsed_form.get_field("existing_data")
        assert len(fld.response.options) == 5

    def test_blinding_options(self, parsed_form):
        fld = parsed_form.get_field("blinding")
        assert len(fld.response.selections) == 4


class TestTableLinkage:
    # "subject" and "tags" use OSF platform widgets — no 1x1 table in the docx
    NO_TABLE_FIELDS = {"subject", "tags"}

    def test_free_text_fields_have_tables(self, parsed_form):
        for fld in parsed_form.all_fields():
            if fld.response_type == ResponseType.FREE_TEXT and fld.slug not in self.NO_TABLE_FIELDS:
                assert fld.table_index is not None, (
                    f"FREE_TEXT field '{fld.slug}' should have a table_index"
                )


class TestSummary:
    def test_summary_structure(self, parsed_form):
        s = parsed_form.summary()
        assert "total_fields" in s
        assert "required" in s
        assert "by_type" in s
        assert s["sections"] == 7
