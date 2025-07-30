# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Helper proxy to the state object."""

from flask import current_app
from werkzeug.local import LocalProxy

current_catalogue_marc21 = LocalProxy(
    lambda: current_app.extensions["invenio-catalogue-marc21"]
)
"""Helper proxy to get the current records marc21 extension."""
