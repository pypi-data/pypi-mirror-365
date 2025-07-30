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
from invenio_rdm_records.resources.serializers.ui.fields import AccessStatusField
from marshmallow.fields import Dict
from marshmallow_utils.fields import FormatDate as BaseFormatDatetime

from ..base import Marc21CatalogueSchema
from ..fields import MetadataUIField

FormatDatetime = partial(BaseFormatDatetime, locale=get_locale)


class Marc21CatalogueUISchema(Marc21CatalogueSchema):
    """Schema for dumping extra information for the UI."""

    additional = (
        # "access",
        "status",
        # "parent",
        "links",
        # "files",
        # "is_published",
    )

    access_status = AccessStatusField(attribute="access", dump_only=True)

    metadata = MetadataUIField()

    created = FormatDatetime(format="long")

    updated = FormatDatetime(format="long")


class Marc21CatalogueUIXMLSchema(Marc21CatalogueUISchema):
    """Schema for dumping extra information for the UI."""

    metadata = Dict()
