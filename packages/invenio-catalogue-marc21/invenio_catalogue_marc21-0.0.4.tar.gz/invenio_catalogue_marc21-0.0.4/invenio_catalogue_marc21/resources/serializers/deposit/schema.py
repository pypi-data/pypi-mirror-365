# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Schema for marc21 catalogue ui records."""

from invenio_records_marc21.resources.serializers.deposit.schema import (
    MetadataDepositField,
)
from marshmallow.fields import Boolean, Method

from ..base import Marc21CatalogueSchema


def create_tree(tree: dict) -> dict:
    """Create Tree."""
    root = tree["root"]
    parent = tree["parent"]
    node = tree["node"]

    try:
        name = node["metadata"]["fields"]["245"][0]["subfields"]["a"]
    except KeyError:
        name = "N/A"

    try:
        root_id = root["id"]
        parent_id = parent["id"]
    except KeyError:
        root_id = ""
        parent_id = ""

    return {
        "name": name,
        "node": node["id"],
        "self_html": f"/catalogue/uploads/{node["id"]}",  # should be comming from node.links?
        "root": root_id,  # get("id", ""),
        "parent": parent_id,  # .get("id", ""),
        "children": [create_tree(child) for child in tree["children"]],
    }


class Marc21CatalogueDepositSchema(Marc21CatalogueSchema):
    """Marc21 catalogue deposit schema."""

    class Meta:
        """Meta class to accept unknwon fields."""

        additional = (
            # "access",
            # "status",
            # "parent",
            # "links",
            # "files",
            "is_published",
            # "pids",
            "versions",
        )

    links = Method(serialize="set_links")
    metadata = MetadataDepositField()
    # catalogue = Method(serialize="set_catalogue_root")
    tree = Method(serialize="create_tree")
    is_catalogue = Boolean()

    def create_tree(self, obj: dict, **__: dict) -> dict:
        """Create tree."""
        return create_tree(obj["tree"])

    def set_links(self, obj: dict, **__: dict) -> dict:
        """Set links."""
        # TODO: that should be done differently somehow
        # it should not be necessary to do this explicitly since the links are in obj
        return obj["links"]
