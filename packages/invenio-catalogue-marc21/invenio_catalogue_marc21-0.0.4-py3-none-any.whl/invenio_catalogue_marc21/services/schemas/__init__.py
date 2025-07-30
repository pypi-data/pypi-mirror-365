# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio module link multiple marc21 modules."""


from .catalogue import CatalogueSchema, Marc21CatalogueSchema

__all__ = (
    "CatalogueSchema",
    "Marc21CatalogueSchema",
)
