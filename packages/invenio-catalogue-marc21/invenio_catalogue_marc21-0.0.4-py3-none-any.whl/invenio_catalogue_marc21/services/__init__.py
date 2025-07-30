# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio module link multiple marc21 modules."""


from .config import Marc21CatalogueServiceConfig
from .services import Marc21CatalogueService

__all__ = (
    "Marc21CatalogueService",
    "Marc21CatalogueServiceConfig",
)
