# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Deserializers."""

from marshmallow_utils.fields import SanitizedUnicode

from ..serializers.base import Marc21CatalogueSchema


class Marc21DeserializeSchema(Marc21CatalogueSchema):
    """Marc21DeserializeSchema."""

    class Meta:
        """Meta."""

        additional = (
            "tree",
            "id",
            "versions",
            "pids",
            "is_published",
            "access",
            "status",
            "parent",
            "links",
            "files",
        )

    id = SanitizedUnicode()
