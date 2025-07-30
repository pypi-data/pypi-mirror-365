# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Deserializers."""

from flask_resources import JSONDeserializer

from .schema import Marc21DeserializeSchema


class Marc21CatalogueDeserializer(JSONDeserializer):
    """Marc21 json deserializer."""

    def __init__(self, schema: type = Marc21DeserializeSchema) -> None:
        """Deserializer initialization."""
        self.schema = schema

    def deserialize(self, data: dict) -> None:
        """Deserialize."""
        data = super().deserialize(data)
        return self.schema().load(data)
