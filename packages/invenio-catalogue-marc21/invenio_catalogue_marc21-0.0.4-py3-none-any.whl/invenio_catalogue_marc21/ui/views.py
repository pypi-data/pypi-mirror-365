# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio module link multiple marc21 modules."""

from flask import current_app, render_template
from flask_login import login_required
from invenio_records_marc21.ui.theme.deposit import empty_record as base_empty_record
from invenio_stats.proxies import current_stats

from ..resources.serializers import (
    Marc21CatalogueDepositSerializer,
    Marc21CatalogueSerializer,
    Marc21CatalogueUIJSONSerializer,
)
from .decorators import (
    pass_draft,
    pass_draft_files,
    pass_record_files,
    pass_record_or_draft,
)
from .deposit import deposit_config


def empty_record() -> dict:
    """Create an empty record."""
    record = base_empty_record()
    record["catalogue"] = {
        "root": "",
        "parent": "",
        "children": [],
    }
    del record["pids"]
    del record["id"]
    return record


@pass_record_or_draft
@pass_record_files
def record_detail(
    record=None,
    files=None,
    pid_value=None,
    is_preview=False,
):
    """Record detail page (aka landing page)."""
    files_dict = files.to_dict() if files else {}

    emitter = current_stats.get_event_emitter("marc21-record-view")
    if record is not None and emitter is not None:
        emitter(current_app, record=record._record, via_api=False)

    record_ui = Marc21CatalogueUIJSONSerializer().dump_obj(record.to_dict())

    tree = Marc21CatalogueSerializer().dump_obj(record.to_dict()["tree"])

    return render_template(
        "invenio_catalogue_marc21/landing_page/record.html",
        record=record_ui,
        pid=pid_value,
        files=files_dict,
        permissions=record.has_permissions_to(
            ["edit", "new_version", "manage", "update_draft", "read_files"],
        ),
        tree=tree,
        is_preview=is_preview,
        is_draft=record._record.is_draft,
    )


@login_required
def deposit_create():
    """Create a new deposit page."""
    # TODO: checkout to in deposit_edit
    # the permission system has to be established yet
    permissions = {
        "showMetadataAccess": False,
        "showFileAccess": False,
        "showFileUploader": True,
        "showImportFromAlma": True,
    }

    return render_template(
        "invenio_catalogue_marc21/deposit/index.html",
        record=empty_record(),
        files={"default_preview": None, "entries": [], "links": {}},
        # templates=deposit_templates(),
        forms_config=deposit_config(),
        permissions=permissions,
    )


@login_required
@pass_draft
@pass_draft_files
def deposit_edit(
    draft=None,
    draft_files=None,
    pid_value=None,
):
    """Edit an existing deposit."""
    serializer = Marc21CatalogueDepositSerializer()
    serialized_record = serializer.dump_obj(draft.to_dict())

    permissions = draft.has_permissions_to(
        [
            "new_version",
            "showMetadataAccess",
            "showFileAccess",
            "showFileUploader",
            "showImportFromAlma",
        ],
    )

    # TODO: should be clearly temporarly ;)
    permissions["showImportFromAlma"] = True
    permissions["showFileUploader"] = True

    return render_template(
        "invenio_catalogue_marc21/deposit/index.html",
        forms_config=deposit_config(apiUrl=f"/api/catalogue/{pid_value}/draft"),
        record=serialized_record,
        files=draft_files.to_dict(),
        permissions=permissions,
    )
