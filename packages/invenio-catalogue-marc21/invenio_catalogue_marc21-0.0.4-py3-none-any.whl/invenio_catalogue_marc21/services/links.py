# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Marc21 Record Service links."""

from invenio_drafts_resources.services.records.config import is_draft, is_record
from invenio_rdm_records.services.config import has_doi, is_record_and_has_doi
from invenio_records_resources.services import ConditionalLink
from invenio_records_resources.services.base.links import Link
from invenio_records_resources.services.records.links import RecordLink


class SwitchLinks:
    """Switch link."""

    def __init__(self, cond: list[tuple] | None = None) -> None:
        """Construct."""
        # conditions are a tuple of 1: is the condition and 2: the template
        self._conditions = cond

    def should_render(self, obj, ctx):
        """Determine if the link should be rendered."""
        for condition, template in self._conditions:
            if condition(obj, ctx):
                return template.should_render(obj, ctx)

    def expand(self, obj, ctx):
        """Determine if the link should be rendered."""
        for condition, template in self._conditions:
            if condition(obj, ctx):
                return template.expand(obj, ctx)


def is_catalogue(record, ctx):
    """Shortcut for links to determine if record is a catalogue record."""
    return "marc21-catalogue" in record.get("$schema", "")


def is_base_marc21_record(record, ctx):
    """Shortcut for links to determine if a record is a base marc21 record."""
    # TODO!!!!!!!!
    # this is only a shortcut. it should be implemented more directly
    return not is_catalogue(record, ctx)


DefaultServiceLinks = {
    "self": SwitchLinks(
        cond=[
            (
                is_catalogue,
                ConditionalLink(
                    cond=is_record,
                    if_=RecordLink("{+api}/catalogue/{id}"),
                    else_=RecordLink("{+api}/catalogue/{id}/draft"),
                ),
            ),
            (
                is_base_marc21_record,
                ConditionalLink(
                    cond=is_record,
                    if_=RecordLink("{+api}/publications/{id}"),
                    else_=RecordLink("{+api}/publications/{id}/draft"),
                ),
            ),
        ],
    ),
    "self_html": SwitchLinks(
        cond=[
            (
                is_catalogue,
                ConditionalLink(
                    cond=is_record,
                    if_=RecordLink("{+ui}/catalogue/{id}"),
                    else_=RecordLink("{+ui}/catalogue/uploads/{id}"),
                ),
            ),
            (
                is_base_marc21_record,
                ConditionalLink(
                    cond=is_record,
                    if_=RecordLink("{+ui}/publications/{id}"),
                    else_=RecordLink("{+ui}/publications/uploads/{id}"),
                ),
            ),
        ],
    ),
    "self_doi": Link(
        "{+ui}/publications/{+pid_doi}",
        when=is_record_and_has_doi,
        vars=lambda record, vars_: vars_.update(
            {
                f"pid_{scheme}": pid["identifier"].split("/")[-1]
                for (scheme, pid) in record.pids.items()
            },
        ),
    ),
    "doi": Link(
        "https://doi.org/{+pid_doi}",
        when=has_doi,
        vars=lambda record, vars_: vars_.update(
            {
                f"pid_{scheme}": pid["identifier"]
                for (scheme, pid) in record.pids.items()
            },
        ),
    ),
    "files": ConditionalLink(
        cond=is_record,
        if_=RecordLink("{+api}/publications/{id}/files"),
        else_=RecordLink("{+api}/publications/{id}/draft/files"),
    ),
    "latest": SwitchLinks(
        cond=[
            (
                is_catalogue,
                RecordLink("{+ui}/catalogue/{id}/versions/latest"),
            ),
            (
                is_base_marc21_record,
                RecordLink("{+ui}/publications/{id}/versions/latest"),
            ),
        ],
    ),
    "latest_html": SwitchLinks(
        cond=[
            (
                is_catalogue,
                RecordLink("{+ui}/catalogue/{id}/latest"),
            ),
            (
                is_base_marc21_record,
                RecordLink("{+ui}/publications/{id}/latest"),
            ),
        ],
    ),
    "draft": SwitchLinks(
        cond=[
            (
                is_catalogue,
                RecordLink("{+ui}/catalogue/uploads/{id}", when=is_record),
            ),
            (
                is_base_marc21_record,
                RecordLink("{+ui}/publications/uploads/{id}", when=is_record),
            ),
        ],
    ),
    "publish": SwitchLinks(
        cond=[
            (
                is_catalogue,
                RecordLink(
                    "{+api}/catalogue/{id}/draft/actions/publish",
                    when=is_draft,
                ),
            ),
            (
                is_base_marc21_record,
                RecordLink(
                    "{+api}/publications/{id}/draft/actions/publish",
                    when=is_draft,
                ),
            ),
        ],
    ),
    "catalogue": SwitchLinks(
        cond=[
            (
                is_catalogue,
                RecordLink("{+api}/catalogue/{id}/catalogue"),
            ),
        ],
    ),
    "versions": RecordLink("{+api}/publications/{id}/versions"),
}
