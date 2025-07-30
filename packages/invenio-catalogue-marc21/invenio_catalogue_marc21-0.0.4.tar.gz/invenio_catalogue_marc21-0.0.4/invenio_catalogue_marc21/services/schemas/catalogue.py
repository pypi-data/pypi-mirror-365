# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio module link multiple marc21 modules."""


from invenio_records_marc21.services.schemas import Marc21RecordSchema
from marshmallow import Schema
from marshmallow.fields import List, Str
from marshmallow_utils.fields import NestedAttribute


class CatalogueSchema(Schema):
    """Catalogue schema."""

    parent = Str(required=True)
    root = Str(required=True)
    children = List(Str())


class Marc21CatalogueSchema(Marc21RecordSchema):
    """Marc21CatalogueSchema."""

    catalogue = NestedAttribute(CatalogueSchema)
