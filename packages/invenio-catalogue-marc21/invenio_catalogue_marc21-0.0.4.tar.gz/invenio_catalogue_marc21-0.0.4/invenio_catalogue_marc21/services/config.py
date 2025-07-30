# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio module link multiple marc21 modules."""

from invenio_records_marc21.services import Marc21RecordServiceConfig
from invenio_records_resources.services.base.config import FromConfig

from ..records import Marc21CatalogueDraft, Marc21CatalogueRecord
from .components import DefaultCatalogueComponents
from .links import DefaultServiceLinks
from .results import RecordItem
from .schemas import Marc21CatalogueSchema


class Marc21CatalogueServiceConfig(Marc21RecordServiceConfig):
    """Marc21 record service config."""

    record_cls = Marc21CatalogueRecord
    draft_cls = Marc21CatalogueDraft
    schema = Marc21CatalogueSchema
    # schema_parent = Marc21ParentSchema
    result_item_cls = RecordItem
    schema_secret_link = None
    review = None

    links_item = FromConfig(
        "MARC21_RECORDS_SERVICE_LINKS",
        default=DefaultServiceLinks,
    )

    components = FromConfig(
        "MARC21_CATALOGUE_SERVICE_COMPONENTS",
        default=DefaultCatalogueComponents,
    )
