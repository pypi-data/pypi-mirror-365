# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Marc21 catalogue fixture tasks."""


from celery import shared_task
from flask_principal import Identity, RoleNeed, UserNeed
from invenio_access.permissions import (
    any_user,
    authenticated_user,
    system_identity,
    system_user_id,
)

from ..proxies import current_catalogue_marc21
from .demo import create_fake_file


def get_user_identity(user_id: int) -> Identity:
    """Get user identity."""
    identity = Identity(user_id)
    # TODO: we need to get the user roles for specific user groups and add to the identity
    identity.provides.add(any_user)
    identity.provides.add(UserNeed(user_id))
    identity.provides.add(authenticated_user)
    identity.provides.add(RoleNeed("Marc21Manager"))
    return identity


def add_file_to_record(file_service, recid, file_path, identity):
    """Add file to record."""
    filename = "Report.pdf"
    data = [{"key": filename}]

    with file_path.open(mode="rb") as file_pointer:
        file_service.init_files(id_=recid, identity=identity, data=data)
        file_service.set_file_content(
            id_=recid, file_key=filename, identity=identity, stream=file_pointer
        )
        file_service.commit_file(id_=recid, file_key=filename, identity=identity)


@shared_task
def create_catalogue_marc21_record(
    user_id,
    data,
    data_chapters: list,
    access,
):
    """Create records for demo purposes."""
    if user_id == system_user_id:
        identity = system_identity
    else:
        identity = get_user_identity(user_id)

    service = current_catalogue_marc21.records_service
    draft_root = service.create(
        data=data,
        identity=identity,
        access=access,
    )
    # add fake file to record
    file_path = create_fake_file()
    add_file_to_record(service.draft_files, draft_root.id, file_path, identity)

    # create chapters as draft to have the pid
    chapter_draft = []
    for chapter in data_chapters:
        draft_chapter = service.create(
            data=chapter,
            identity=identity,
            access=access,
        )

        file_path = create_fake_file()
        add_file_to_record(service.draft_files, draft_chapter.id, file_path, identity)
        chapter_draft.append(draft_chapter)

    # extract root parent and the child list
    root = draft_root.id
    parent = root
    children = [chapter.id for chapter in chapter_draft]
    catalogue = {"root": "", "parent": "", "children": children}

    # update draft
    drafts = []

    # update root draft
    data = draft_root.data
    data["catalogue"] = catalogue
    drafts.append(
        service.update_draft(
            id_=draft_root.id,
            data=data,
            identity=identity,
        )
    )

    catalogue = {"root": root, "parent": parent, "children": []}
    for draft in chapter_draft:
        data = draft.data
        data["catalogue"] = catalogue
        drafts.append(
            service.update_draft(
                id_=draft.id,
                data=data,
                identity=identity,
            )
        )

    # publish drafts
    for draft in drafts:
        service.publish(id_=draft.id, identity=identity)
