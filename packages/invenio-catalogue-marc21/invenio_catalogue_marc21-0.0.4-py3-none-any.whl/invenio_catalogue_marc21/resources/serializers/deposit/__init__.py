# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Marc21 Catalogue Deposit serializers module."""

from .schema import Marc21CatalogueDepositSchema
from .serializer import Marc21CatalogueDepositSerializer

__all__ = (
    "Marc21CatalogueDepositSchema",
    "Marc21CatalogueDepositSerializer",
)
