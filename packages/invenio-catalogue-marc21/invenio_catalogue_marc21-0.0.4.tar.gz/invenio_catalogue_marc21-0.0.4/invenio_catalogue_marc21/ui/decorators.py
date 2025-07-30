# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Marc21 decorators backend."""

from functools import wraps

from flask import g
from invenio_records_resources.services.errors import PermissionDeniedError
from sqlalchemy.orm.exc import NoResultFound

from ..proxies import current_catalogue_marc21


def _service():
    """Get the record service."""
    return current_catalogue_marc21.records_service


def _files_service():
    """Get the record files service."""
    return current_catalogue_marc21.records_service.files


def _draft_files_service():
    """Get the record files service."""
    return current_catalogue_marc21.records_service.draft_files


def pass_draft(func):
    """Decorator to retrieve the draft using the record service."""

    @wraps(func)
    def view(**kwargs):
        pid_value = kwargs.get("pid_value")
        kwargs["draft"] = _service().read_draft(id_=pid_value, identity=g.identity)
        return func(**kwargs)

    return view


def pass_draft_files(func):
    """Decorate a view to pass a draft's files using the files service."""

    @wraps(func)
    def view(**kwargs):
        try:
            pid_value = kwargs.get("pid_value")
            files = _draft_files_service().list_files(
                id_=pid_value, identity=g.identity
            )
            kwargs["draft_files"] = files

        except PermissionDeniedError:
            # this is handled here because we don't want a 404 on the landing
            # page when a user is allowed to read the metadata but not the
            # files
            kwargs["draft_files"] = None

        return func(**kwargs)

    return view


def pass_record_or_draft(f):
    """Decorate to retrieve the record or draft using the record service."""

    @wraps(f)
    def view(**kwargs):
        pid_value = kwargs.get("pid_value")
        is_preview = kwargs.get("is_preview")

        if is_preview:
            try:
                record = _service().read_draft(id_=pid_value, identity=g.identity)
            except NoResultFound:
                record = _service().read(id_=pid_value, identity=g.identity)
        else:
            record = _service().read(id_=pid_value, identity=g.identity)

        kwargs["record"] = record
        return f(**kwargs)

    return view


def pass_record_files(f):
    """Decorate a view to pass a record's files using the files service."""

    @wraps(f)
    def view(**kwargs):
        is_preview = kwargs.get("is_preview")
        pid_value = kwargs.get("pid_value")

        try:
            if is_preview:
                files = draft_files_service().list_files(
                    id_=pid_value,
                    identity=g.identit,
                )
            else:
                files = _files_service().list_files(id_=pid_value, identity=g.identity)
        except PermissionDeniedError:
            files = None
        except NoResultFound:
            files = _files_service().list_files(id_=pid_value, identity=g.identity)

        kwargs["files"] = files

        return f(**kwargs)

    return view
