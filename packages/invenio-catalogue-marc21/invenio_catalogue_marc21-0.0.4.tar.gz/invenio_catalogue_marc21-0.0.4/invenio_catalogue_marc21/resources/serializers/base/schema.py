# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
"""Schemas for marc21 records serializers."""

# from invenio_records_marc21.resources.serializers.schema import Marc21Schema
from invenio_records_marc21.services.schemas import Marc21RecordSchema
from marshmallow import Schema
from marshmallow.fields import Boolean, List, Method, Nested, String


class CatalogueSchema(Schema):
    """Schema for a catalogue records."""

    root = String()
    parent = String()
    children = List(String())


class Marc21CatalogueSchema(Marc21RecordSchema):
    """Schema for dumping extra information for the marc21 record."""

    # class Meta:
    #     """Meta class to accept unknown fields."""

    #     additional = (
    #         "access",
    #         "status",
    #         "parent",
    #         "links",
    #         "files",
    #     )

    id = String()

    catalogue = Nested(CatalogueSchema)
    is_catalogue = Boolean()
    metadata = Method(deserialize="load_metadata")

    def load_metadata(self, value: dict) -> dict:
        """Load metadata."""
        fields = {}

        for field in value["fields"]:
            if int(field["id"]) < 10:
                fields[field["id"]] = field["subfield"]
            else:
                if field["id"] not in fields:
                    fields[field["id"]] = []

                subfields = {
                    v[0:1]: [v[2:].strip()] for v in field["subfield"].split("$$")[1:]
                }

                fields[field["id"]].append(
                    {
                        "ind1": field["ind1"],
                        "ind2": field["ind2"],
                        "subfields": subfields,
                    },
                )
        return {
            "fields": fields,
            "leader": value["leader"],
        }
