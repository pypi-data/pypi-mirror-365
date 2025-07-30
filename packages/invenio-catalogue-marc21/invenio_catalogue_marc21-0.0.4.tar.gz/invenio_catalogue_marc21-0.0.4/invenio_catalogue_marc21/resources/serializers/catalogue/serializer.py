# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Marc21 UI record response serializers."""


from flask_resources.serializers import JSONSerializer, MarshmallowSerializer

from .schema import Marc21CatalogueSchema


class Marc21CatalogueSerializer(MarshmallowSerializer):
    """Marc21 Catalogue serializer implementation."""

    def __init__(
        self,
        format_serializer_cls: type = JSONSerializer,
        object_schema_cls: type = Marc21CatalogueSchema,
        **options: dict,
    ) -> None:
        """Marc21 Base Serializer Constructor.

        :param schema_cls: Default Marc21Schema
        :param options: Json encoding options.
        """
        super().__init__(
            format_serializer_cls=format_serializer_cls,
            object_schema_cls=object_schema_cls,
            **options,
        )

    def dump_obj(self, obj: dict) -> dict:
        """Dump the object into a JSON string."""
        return self.object_schema.dump(obj)

    def dump_list(self, obj_list: dict) -> dict:
        """Serialize a list of records.

        :param obj_list: List of records instance.
        """
        records = obj_list["hits"]["hits"]
        obj_list["hits"]["hits"] = [self.dump_obj(obj) for obj in records]
        return obj_list
