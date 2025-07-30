# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Catalogue service component for ."""


from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_alma.proxies import current_alma
from invenio_drafts_resources.resources import RecordResource
from invenio_records_marc21 import convert_marc21xml_to_json
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_headers,
    request_search_args,
    request_view_args,
)

from . import config


class Marc21CatalogueAlmaProxyResource(RecordResource):
    """Marc21 catalogue alma proxy resource."""

    config_name = "MARC21_CATALOGUE_ALMA_PROXY_CONFIG"
    default_config = config.Marc21CatalogueAlmaProxyResourceConfig

    def create_url_rules(self) -> list:
        """Create the URL rules for the record resources."""
        routes = self.config.routes

        def p(route: str) -> str:
            """Prefix a route with the URL prefix."""
            return f"{self.config.url_prefix}{route}"

        rules = [
            route("GET", p(routes["alma"]), self.alma),
        ]
        return rules

    @request_view_args
    @response_handler()
    def alma(self) -> tuple:
        """Get record from alma."""
        type_ = resource_requestctx.view_args["type"]
        value = resource_requestctx.view_args["pid_value"]

        search_key = "" if type_ == "mmsid" else "local_control_field_009"
        metadata = current_alma.alma_sru_service.get_record(value, search_key)[0]
        obj = convert_marc21xml_to_json(metadata)
        data = {
            "metadata": obj,
            "catalogue": {
                "parent": "",
                "root": "",
                "children": [],
            },
        }
        item = self.service.create(identity=g.identity, data=data)

        return item.to_dict(), 200


class Marc21CatalogueResource(RecordResource):
    """Marc21 Catalogue resource."""

    config_name = "MARC21_CATALOGUE_CONFIG"
    default_config = config.Marc21CatalogueResourceConfig

    def create_url_rules(self) -> list:
        """Create the URL rules for the record resource."""
        routes = self.config.routes

        def p(route: str) -> str:
            """Prefix a route with the URL prefix."""
            return f"{self.config.url_prefix}{route}"

        rules = [
            route("GET", p(routes["item"]), self.catalogue),
            route("POST", p(routes["add"]), self.add),
            route("GET", p(routes["edit"]), self.edit),
        ]
        return rules

    @request_search_args
    @request_view_args
    @response_handler()
    def catalogue(self) -> tuple:
        """Read an item."""
        item = self.service.catalogue(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            include_drafts=resource_requestctx.args.get("drafts", True),
        )
        return item, 200

    @request_data
    @request_view_args
    @response_handler()
    def add(self) -> tuple:
        """Read an item."""
        data = resource_requestctx.data
        item = self.service.add(
            identity=g.identity,
            data=data,
        )
        return item.to_dict(), 200

    @request_view_args
    @response_handler()
    def edit(self) -> tuple:
        """Edit an item."""
        item = self.service.edit(
            identity=g.identity,
            id_=resource_requestctx.view_args["pid_value"],
        )
        return item.to_dict(), 200


#
# Records
#
class Marc21CatalogueRecordResource(RecordResource):
    """Bibliographic record resource."""

    config_name = "MARC21_RECORDS_RECORD_CONFIG"
    default_config = config.Marc21CatalogueRecordResourceConfig

    def create_url_rules(self) -> list:
        """Create the URL rules for the record resource."""
        routes = self.config.routes

        def s(route: str) -> str:
            """Suffix a route with the URL prefix."""
            return f"{route}{self.config.url_prefix}"

        def p(route: str) -> str:
            """Prefix a route with the URL prefix."""
            return f"{self.config.url_prefix}{route}"

        rules = [
            # route("GET", p(routes["list"]), self.search),
            route("POST", p(routes["list"]), self.create),
            route("GET", p(routes["item"]), self.read),
            route("PUT", p(routes["item"]), self.update),
            route("DELETE", p(routes["item"]), self.delete),
            route("POST", p(routes["item-draft"]), self.edit),
            route("PUT", p(routes["item-draft"]), self.update_draft),
            route("DELETE", p(routes["item-draft"]), self.delete_draft),
            route("POST", p(routes["item-publish"]), self.publish),
        ]
        return rules

    @request_data
    @response_handler()
    def create(self) -> tuple[dict, int]:
        """Create an item.

        POST /catalogue/
        """
        data = resource_requestctx.data
        item = self.service.create(
            g.identity,
            data=data,
        )
        return item.to_dict(), 201

    @request_headers
    @request_view_args
    @request_data
    @response_handler()
    def update_draft(self) -> tuple[dict, int]:
        """Update a draft.

        PUT /catalogue/:pid_value/draft
        """
        data = resource_requestctx.data
        del data["tree"]  # TODO: should be done over the serializers
        item = self.service.update_draft(
            g.identity,
            resource_requestctx.view_args["pid_value"],
            data,
            revision_id=resource_requestctx.headers.get("if_match"),
        )
        return item.to_dict(), 200
