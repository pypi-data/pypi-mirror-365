# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Marc21 Resources serializers module."""

from .schema import Marc21CatalogueUISchema, Marc21CatalogueUIXMLSchema
from .serializer import Marc21CatalogueUIJSONSerializer

__all__ = (
    "Marc21CatalogueUIJSONSerializer",
    "Marc21CatalogueUISchema",
    "Marc21CatalogueUIXMLSchema",
)
