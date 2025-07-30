# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Metadata field for marc21 records."""


from marshmallow.fields import Field


def field_controlfield(value: str, start: int = 0, end: int = -1) -> str:
    """MARC21 get sub string of a controlfields from json."""
    if isinstance(value, str):
        return value[start:end]
    return value


def field_subfields(value: list) -> list[dict]:
    """MARC21 get list of subfields from json."""
    subfields = []
    if isinstance(value, list):
        subfields = [field.get("subfields", {}) for field in value]
    return subfields


def field_subfield(key: str, subfields: dict) -> str:
    """Find subfield in a list of subfields dicts."""
    subfield = subfields.get(key, [])
    if isinstance(subfield, list):
        subfield = ", ".join(subfield)
    return subfield if subfield else ""


class MetadataUIField(Field):
    """Schema for the record metadata."""

    def _serialize(self, value, attr, obj, **kwargs: dict):
        """Serialise access status."""
        fields = value.get("fields", {})
        out = {}

        if value:
            publication_year = field_controlfield(
                fields.get("008", "               "),
                7,
                11,
            )  # substring 7-10
            standard_book_number = field_subfields(fields.get("020", []))
            other_identifiers = field_subfields(fields.get("024", []))
            main_entry_personal_name = field_subfields(fields.get("100", []))
            title_statement = field_subfields(fields.get("245", []))
            physical_description = field_subfields(fields.get("300", []))

            added_entry_personal_name = field_subfields(fields.get("700", []))
            corporate_name = field_subfields(fields.get("710", []))  # 2_
            publication_location = field_subfields(fields.get("751", []))  # $a and $b

            ## OLD
            # manufacture_copyright = field_subfields(fields.get("264", []))

            # general_note = field_subfields(fields.get("500", []))
            # dissertation_note = field_subfields(fields.get("502", []))
            out = {}
            if other_identifiers:
                out["other_standard_identifiers"] = {
                    "identifier": field_subfield("a", other_identifiers[0]),
                    "code": field_subfield("2", other_identifiers[0]),
                }
            if standard_book_number:
                out["standard_book_number"] = {
                    "standard_book_number": field_subfield(
                        "a", standard_book_number[0]
                    ),
                }
            if main_entry_personal_name:
                out["main_entry_personal_name"] = {
                    "personal_name": field_subfield("a", main_entry_personal_name[0])
                }
            if added_entry_personal_name:
                out["added_entry_personal_name"] = [
                    {"personal_name": field_subfield("a", creator)}
                    for creator in added_entry_personal_name
                ]
            if title_statement:
                out["title_statement"] = {
                    "title": field_subfield("a", title_statement[0]),
                    "additional_title": field_subfield("b", title_statement[0]),
                }
            if physical_description:
                out["physical_description"] = {
                    "extent": field_subfield("a", physical_description[0])
                }
            if corporate_name:
                out["corporate_name"] = {
                    "corporate_name_or_jurisdiction_name_as_entry": field_subfield(
                        "a", corporate_name[0]
                    )
                }
            if publication_location:
                out["geographic_name"] = {
                    "geographic_name": field_subfield("a", publication_location[0])
                }
            if publication_year:
                out["publication_year"] = publication_year

            trdzout = {
                "publication_year": publication_year,
                # "dissertation_note": {
                #     "dissertation_note": field_subfield("a", dissertation_note)
                # },
                # "general_note": {"general_note": field_subfield("a", general_note)},
                # "production_publication_distribution_manufacture_and_copyright_notice": {
                #     "date_of_production_publication_distribution_manufacture_or_copyright_notice": field_subfield(
                #         "c", manufacture_copyright
                #     )
                # },
                # "language_code": {
                #     "language_code_of_text_sound_track_or_separate_title": field_subfield(
                #         "a", language_code
                #     )
                # },
            }

        return out
