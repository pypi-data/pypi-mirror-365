# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Marc21 catalogue record response serializers."""

from flask_resources.serializers import JSONSerializer
from invenio_records_marc21.resources.serializers import Marc21XMLSerializer

from .schema import Marc21CatalogueSchema


class Marc21CatalogueXMLSerializer(Marc21XMLSerializer):
    """Marc21 XML export serializer implementation."""

    def __init__(
        self,
        format_serializer_cls: type = JSONSerializer,
        object_schema_cls: type = Marc21CatalogueSchema,
        **options: dict,
    ) -> None:
        """Marc21 Json Serializer Constructor.

        :param schema_cls: Default Marc21Schema
        :param options: Json encoding options.
        """
        super().__init__(
            format_serializer_cls=format_serializer_cls,
            object_schema_cls=object_schema_cls,
            **options,
        )
