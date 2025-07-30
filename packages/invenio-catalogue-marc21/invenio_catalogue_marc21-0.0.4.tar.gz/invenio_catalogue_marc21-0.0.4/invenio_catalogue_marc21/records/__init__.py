# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Marc21 Records module."""

from .api import Marc21CatalogueDraft, Marc21CatalogueRecord

__all__ = (
    "Marc21CatalogueDraft",
    "Marc21CatalogueRecord",
)
