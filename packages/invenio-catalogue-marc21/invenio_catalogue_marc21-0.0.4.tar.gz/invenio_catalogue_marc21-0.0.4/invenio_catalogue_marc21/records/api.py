# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


"""Marc21 Catalogue Api."""

from invenio_records.systemfields import ConstantField, DictField
from invenio_records_marc21.records import Marc21Draft, Marc21Record

from .systemfields import CatalogueCheckField


class Marc21CatalogueDraft(Marc21Draft):
    """Marc21 catalogue draft API."""

    schema = ConstantField(
        "$schema", "local://marc21-catalogue/marc21-catalogue-v1.0.0.json"
    )

    catalogue = DictField(key="catalogue", clear_none=False, create_if_missing=True)

    is_catalogue = CatalogueCheckField(dump=True, value="marc21-catalogue")


class Marc21CatalogueRecord(Marc21Record):
    """Marc21 catalogue API."""

    schema = ConstantField(
        "$schema", "local://marc21-catalogue/marc21-catalogue-v1.0.0.json"
    )

    catalogue = DictField(key="catalogue", clear_none=False, create_if_missing=True)

    is_catalogue = CatalogueCheckField(dump=True, value="marc21-catalogue")
