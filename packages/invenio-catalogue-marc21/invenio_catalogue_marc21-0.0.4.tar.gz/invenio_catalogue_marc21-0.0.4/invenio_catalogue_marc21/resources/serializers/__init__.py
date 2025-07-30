# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Marc21 Resources serializers module."""

from .base import Marc21CatalogueSchema, Marc21CatalogueXMLSerializer
from .catalogue import Marc21CatalogueSerializer
from .deposit import Marc21CatalogueDepositSerializer
from .ui import Marc21CatalogueUIJSONSerializer

__all__ = (
    "Marc21CatalogueDepositSerializer",
    "Marc21CatalogueSchema",
    "Marc21CatalogueSerializer",
    "Marc21CatalogueUIJSONSerializer",
    "Marc21CatalogueXMLSerializer",
)
