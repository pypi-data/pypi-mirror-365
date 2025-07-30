# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Catalogue service component for ."""

from typing import Final

from flask_resources import RequestBodyParser, ResponseHandler
from flask_resources.parsers import MultiDictSchema
from flask_resources.serializers import JSONSerializer
from invenio_drafts_resources.resources import RecordResourceConfig
from invenio_records_resources.resources.records.args import SearchRequestArgsSchema
from marshmallow.fields import Bool, Int, Str

from .deserializers.deserializer import Marc21CatalogueDeserializer
from .serializers import Marc21CatalogueXMLSerializer

# from .serializers.catalogue import Marc21CatalogueSerializer
from .serializers.deposit import Marc21CatalogueDepositSerializer
from .serializers.ui import Marc21CatalogueUIJSONSerializer

url_prefix = "/catalogue"


class CatalogueSearchArgsSchema(MultiDictSchema):
    """Search URL query string arguments."""

    drafts = Bool()


class Marc21CatalogueAlmaProxyResourceConfig(RecordResourceConfig):
    """Marc21 catalogue proxy resource config."""

    blueprint_name: Final[str] = "marc21_catalogue_alma_proxy"
    url_prefix: Final[str] = url_prefix

    default_accept_mimetype: Final[str] = "application/json"

    response_handlers: Final[dict] = {
        "application/json": ResponseHandler(Marc21CatalogueDepositSerializer()),
    }

    links_config: Final[dict] = {}

    routes: Final[dict] = {
        "alma": "/alma/<type>/<pid_value>",
    }

    # Request parsing
    request_search_args = CatalogueSearchArgsSchema
    request_args = SearchRequestArgsSchema
    request_view_args: Final[dict] = {
        "pid_value": Str(),
        "type": Str(),
    }
    request_headers: Final[dict] = {"if_match": Int()}
    # request_body_parsers: Final[dict] = {
    #     "application/json": RequestBodyParser(Marc21CatalogueDeserializer()),
    # }


class Marc21CatalogueResourceConfig(RecordResourceConfig):
    """Marc21 Record resource configuration."""

    blueprint_name: Final[str] = "marc21_catalogue"
    url_prefix: Final[str] = url_prefix

    default_accept_mimetype: Final[str] = "application/json"

    response_handlers: Final[dict] = {
        "application/json": ResponseHandler(Marc21CatalogueDepositSerializer()),
    }

    links_config: Final[dict] = {}

    routes: Final[dict] = {
        "item": "/<pid_value>/catalogue",
        "add": "/<pid_value>/add",
        "edit": "/<pid_value>/edit",
    }

    # Request parsing
    request_search_args = CatalogueSearchArgsSchema
    request_args = SearchRequestArgsSchema
    request_view_args: Final[dict] = {
        "pid_value": Str(),
    }
    request_headers: Final[dict] = {"if_match": Int()}
    request_body_parsers: Final[dict] = {
        "application/json": RequestBodyParser(Marc21CatalogueDeserializer()),
    }


class Marc21CatalogueRecordResourceConfig(RecordResourceConfig):
    """Marc21 Record resource configuration."""

    blueprint_name = "marc21_catalogue_records"
    url_prefix = url_prefix

    default_accept_mimetype = "application/json"

    response_handlers: Final[dict] = {
        "application/json": ResponseHandler(JSONSerializer()),
        "application/marcxml": ResponseHandler(Marc21CatalogueXMLSerializer()),
        "application/vnd.inveniomarc21.ui.v1+json": ResponseHandler(
            Marc21CatalogueUIJSONSerializer(),
        ),
        "application/vnd.inveniomarc21.v1+json": ResponseHandler(
            Marc21CatalogueDepositSerializer(),
        ),
    }
    links_config: Final[dict] = {}

    routes: Final[dict] = {
        "search": "/search",
        "list": "",
        "item": "/<pid_value>",
        "item-draft": "/<pid_value>/draft",
        "item-publish": "/<pid_value>/draft/actions/publish",
    }

    # Request parsing
    request_args = SearchRequestArgsSchema
    request_headers: Final[dict] = {"if_match": Int()}
    request_body_parsers: Final[dict] = {
        "application/json": RequestBodyParser(Marc21CatalogueDeserializer()),
    }

    request_view_args: Final[dict] = {
        "pid_value": Str(),
        "pid_type": Str(),
    }
