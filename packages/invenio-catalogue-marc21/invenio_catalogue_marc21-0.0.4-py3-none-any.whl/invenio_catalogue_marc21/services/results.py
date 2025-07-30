# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Results."""

from invenio_records_resources.services.records.results import (
    RecordItem as BaseRecordItem,
)


class RecordItem(BaseRecordItem):
    """Record item catalogue marc21."""

    def to_dict(self) -> dict:
        """Get a dictionary for the record."""
        data = super().to_dict()
        data["tree"] = self._service.tree(
            self._identity,
            data["id"],
            # include_drafts=False,
        )
        return data
