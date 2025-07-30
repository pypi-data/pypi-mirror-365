# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio module ui filters."""


def format_file_size(size_in_bytes: int) -> str:
    """Format file size."""
    if size_in_bytes < 1024 * 1024:
        # Size is less than 1 MB, format as kB
        size_in_kb = size_in_bytes / 1024
        return f"{size_in_kb:.2f} kB"

    # Size is 1 MB or more, format as MB
    size_in_mb = size_in_bytes / 1024 / 1024
    return f"{size_in_mb:.2f} MB"
