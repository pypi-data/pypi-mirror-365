# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Serializers base."""

from .schema import CatalogueSchema, Marc21CatalogueSchema
from .serializer import Marc21CatalogueXMLSerializer

__all__ = (
    "CatalogueSchema",
    "Marc21CatalogueSchema",
    "Marc21CatalogueXMLSerializer",
)
