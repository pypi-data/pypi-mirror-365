# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Marc21 UI record response serializers."""


from flask_resources.serializers import JSONSerializer
from invenio_records_marc21.resources.serializers.deposit import Marc21DepositSerializer

from .schema import Marc21CatalogueDepositSchema


class Marc21CatalogueDepositSerializer(Marc21DepositSerializer):
    """UI JSON serializer implementation."""

    def __init__(
        self,
        format_serializer_cls: type = JSONSerializer,
        object_schema_cls: type = Marc21CatalogueDepositSchema,
        **options: dict,
    ) -> None:
        """Marc21 UI JSON Constructor.

        :param object_schema_cls: object schema serializing the Marc21 record. (default: `Marc21Schema`)
        :param object_key: str key dump ui specific information
        """
        super().__init__(
            format_serializer_cls=format_serializer_cls,
            object_schema_cls=object_schema_cls,
            **options,
        )
