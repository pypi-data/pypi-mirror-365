# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Marc21 Resources serializers module."""

from .schema import Marc21CatalogueSchema
from .serializer import Marc21CatalogueSerializer

__all__ = (
    "Marc21CatalogueSchema",
    "Marc21CatalogueSerializer",
)
