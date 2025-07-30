# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Blueprints."""


from flask import Blueprint, Flask
from invenio_pidstore.errors import PIDDeletedError, PIDDoesNotExistError
from invenio_records_resources.services.errors import PermissionDeniedError

from .errors import (
    not_found_error,
    record_permission_denied_error,
    record_tombstone_error,
)
from .filters import format_file_size
from .views import deposit_create, deposit_edit, record_detail


#
# Registration
#
def create_blueprint(app: Flask) -> Blueprint:
    """Register blueprint routes on app."""
    routes = app.config.get("MARC21_CATALOGUE_UI_ENDPOINTS")

    blueprint = Blueprint(
        "invenio_catalogue_marc21",
        __name__,
        template_folder="templates",
        static_folder="static",
        url_prefix="/catalogue",
    )

    # Record URL rules
    blueprint.add_url_rule(
        routes["record-detail"],
        view_func=record_detail,
    )

    blueprint.add_url_rule(
        routes["deposit-create"],
        view_func=deposit_create,
    )

    blueprint.add_url_rule(
        routes["deposit-edit"],
        view_func=deposit_edit,
    )

    # Register error handlers
    blueprint.register_error_handler(PIDDeletedError, record_tombstone_error)
    blueprint.register_error_handler(PIDDoesNotExistError, not_found_error)
    blueprint.register_error_handler(KeyError, not_found_error)
    blueprint.register_error_handler(
        PermissionDeniedError,
        record_permission_denied_error,
    )

    # Register jinja filters
    blueprint.add_app_template_filter(format_file_size)

    return blueprint
