# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# invenio-catalogue-marc21 is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


"""Command-line tools for demo module."""

from collections.abc import Callable
from functools import wraps

import click
from flask.cli import with_appcontext
from invenio_accounts.proxies import current_datastore
from invenio_db import db

from .fixtures.demo import create_fake_catalogue_record
from .fixtures.tasks import create_catalogue_marc21_record


def get_user(user_email: str):
    """Get user."""
    with db.session.no_autoflush:
        user = current_datastore.get_user_by_email(user_email)

    if not user:
        msg = f"NO user found for email: {user_email}"
        raise RuntimeError(msg)

    return user


def wrap_messages(before: str, after: str) -> Callable:
    """Wrap messages with entry and exit message."""

    def decorator[T](func: Callable[..., T]) -> Callable:
        @wraps(func)
        def wrapper(**kwargs: dict) -> None:
            """Wrapper."""
            click.secho(before, fg="blue")
            try:
                func(**kwargs)
            except RuntimeError as error:
                click.secho(str(error), fg="red")
            else:
                click.secho(after, fg="green")

        return wrapper

    return decorator


@click.group()
def catalogue() -> None:
    """InvenioMarc21 records commands."""


@catalogue.command("demo")
@with_appcontext
@click.option(
    "-u",
    "--user-email",
    default="user@demo.org",
    show_default=True,
    help="User e-mail of an existing user.",
)
@click.option(
    "--number",
    "-n",
    "n_records",
    default=1,
    show_default=True,
    type=int,
    help="Number of records will be created.",
)
@click.option(
    "--chapters",
    "-c",
    "n_chapters",
    default=15,
    show_default=True,
    type=int,
    help="Number of chapters will be created.",
)
@with_appcontext
@wrap_messages(
    before="Creating demo records...",
    after="Created records!",
)
def demo(user_email: str, n_records: int, n_chapters: int) -> None:
    """Create number of fake records for demo purposes."""
    user = get_user(user_email)

    for _ in range(n_records):
        data, data_chapters, data_access = create_fake_catalogue_record(n_chapters)
        create_catalogue_marc21_record.delay(user.id, data, data_chapters, data_access)
