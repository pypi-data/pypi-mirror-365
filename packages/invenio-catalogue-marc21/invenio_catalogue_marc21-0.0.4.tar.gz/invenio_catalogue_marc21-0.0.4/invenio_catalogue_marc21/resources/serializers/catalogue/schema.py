# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Schema for marc21 catalogue ui records."""

from functools import partial

from invenio_i18n import get_locale
from marshmallow import Schema
from marshmallow.fields import Dict, List, Nested
from marshmallow_utils.fields import FormatDate as BaseFormatDatetime
from marshmallow_utils.fields import SanitizedUnicode

from ..fields import MetadataUIField

FormatDatetime = partial(BaseFormatDatetime, locale=get_locale)


class Marc21CatalogueMetadataSchema(Schema):
    """Schema for dumping extra information for the UI."""

    id = SanitizedUnicode(data_key="id")

    additional = (
        # "access",
        # "status",
        # "parent",
        # "links",
        # "files",
        # "is_published",
    )
    links = Dict()
    metadata = MetadataUIField()

    created = FormatDatetime(format="medium")

    updated = FormatDatetime(format="medium")


class Marc21CatalogueSchema(Schema):
    """Marc21 catalogue schema."""

    root = Nested(Marc21CatalogueMetadataSchema())
    node = Nested(Marc21CatalogueMetadataSchema())
    parent = Nested(Marc21CatalogueMetadataSchema())
    children = List(Nested(lambda: Marc21CatalogueSchema()))
