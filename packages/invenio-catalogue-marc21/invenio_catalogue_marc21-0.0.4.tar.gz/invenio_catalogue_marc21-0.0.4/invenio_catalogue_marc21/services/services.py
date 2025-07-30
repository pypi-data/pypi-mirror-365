# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio module link multiple marc21 modules."""

from flask_principal import Identity
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_marc21.services import Marc21RecordService
from invenio_records_resources.services.records.results import RecordItem
from invenio_records_resources.services.uow import unit_of_work
from sqlalchemy.exc import NoResultFound


class Marc21CatalogueService(Marc21RecordService):
    """Marc21 record service class."""

    def tree(
        self,
        identity: Identity,
        id_: str,
        *,
        include_drafts: bool = True,
        parent=None,
        root=None,
    ) -> dict:
        """Build a tree of linked records.

        :param identity: Identity of user creating the record.
        :param id_: Record PID value.
        :param include_deleted: Include deleted records.
        :param level: child or deep
        """
        try:
            record = self.read(identity, id_)
        except (NoResultFound, PIDDoesNotExistError):
            record = self.read_draft(identity, id_)

        children = record._record.get("catalogue", {}).get("children", [])

        try:
            parent = parent or self.read(
                identity, record._record["catalogue"]["parent"]
            )
            root = root or self.read(identity, record._record["catalogue"]["root"])
        except (NoResultFound, PIDDoesNotExistError):
            try:
                parent = parent or self.read_draft(
                    identity, record._record["catalogue"]["parent"]
                )
                root = root or self.read_draft(
                    identity, record._record["catalogue"]["root"]
                )
            except PIDDoesNotExistError:
                parent = {}
                root = {}

        return {
            "children": [
                (
                    self.tree(
                        identity,
                        child,
                        include_drafts=include_drafts,
                        parent=record,
                        root=root,
                    )
                )
                for child in children
            ],
            "node": record,
            "parent": parent,
            "root": root,
        }

    @unit_of_work()
    def update_draft(
        self,
        identity,
        id_,
        data=None,
        metadata=None,
        revision_id=None,
        access=None,
        uow=None,
    ):

        item = super().update_draft(identity, id_, data, metadata, revision_id, access)

        # TODO:
        # think of moving this to a component
        # it may be clearer, but there is more configuration necessary which makes the invenio.cfg more complicated.
        # it would be nice to add elements to the components list from the package in a more dynamic way,
        # it would be nice to preserve some sorting so that the component keeps an index or a ordering in the sense,
        # component needs applied before another. or other, one depends on another, like alembic scripts
        # the question is how to implement it without killing the performance.
        parent_id = data["catalogue"]["parent"]
        if parent_id:
            parent = self.edit(identity, parent_id)
            parent_data = parent.data
            if id_ not in parent_data["catalogue"]["children"]:
                parent_data["catalogue"]["children"].append(id_)
                super().update_draft(identity, parent_id, parent_data)

        return item

    def add(self, identity: Identity, data: dict) -> RecordItem:
        """Add.

        this method does only creates a new record. this means that there is not
        yet added a entry to the children attribute in the parent node. this
        enables the option to clean up unused nodes by a task.

        the update draft method is then taking care of connecting the node to the parent.

        QUESTION:
        should the update_draft method be overritten or should that addition to
        parent functionality be done by a component

        QUESTION:
        should the add be safeguarded by a permission system?
        """
        return super().create(identity=identity, data=data)
