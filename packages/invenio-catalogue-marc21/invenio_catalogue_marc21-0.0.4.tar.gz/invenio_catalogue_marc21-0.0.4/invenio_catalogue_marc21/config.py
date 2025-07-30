# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio module link multiple marc21 modules."""

MARC21_CATALOGUE_BASE_TEMPLATE = "invenio_catalogue_marc21/base.html"
"""Default base template for the demo page."""


MARC21_CATALOGUE_UI_ENDPOINTS = {
    "record-detail": "/<pid_value>",
    "deposit-create": "/uploads/new",
    "deposit-edit": "/uploads/<pid_value>",
}
"""UI endpoints for invenio-catalogue-marc21."""
