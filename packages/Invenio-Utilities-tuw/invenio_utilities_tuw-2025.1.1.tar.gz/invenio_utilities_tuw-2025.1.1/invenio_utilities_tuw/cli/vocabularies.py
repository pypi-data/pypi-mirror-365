# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-Utilities-TUW is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Management commands for vocabularies."""

import os
import sys

import click
import dictdiffer
import yaml
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.records.api import VocabularyType
from sqlalchemy.exc import NoResultFound

special_vocabulary_types = [
    "affiliations",
    "awards",
    "funders",
    "names",
    "subjects",
]


def _get_service_for_type(vocab_type: str):
    """Get the registered service for the given vocabulary type."""
    if vocab_type in special_vocabulary_types:
        return current_service_registry.get(vocab_type), False

    if vocab_type not in {vt.id for vt in VocabularyType.query.all()}:
        raise LookupError(f"could not find vocabulary type '{vocab_type}'")

    return current_service_registry.get("vocabularies"), True


@click.group("vocabularies")
def vocabularies():
    """Management commands for vocabularies."""


@vocabularies.command("list-types")
@with_appcontext
def list_vocabulary_types():
    """List the available vocabulary types."""
    types = {vt.id for vt in VocabularyType.query.all()}
    for t in sorted(types):
        if t in special_vocabulary_types:
            click.secho(t, fg="green")
        else:
            click.echo(t)


@vocabularies.command("update")
@click.argument(
    "filepath",
    required=True,
)
@click.argument(
    "vocabulary_id",
    required=True,
)
@click.option(
    "--type",
    "-t",
    "vocab_type",
    required=False,
    default=None,
    help="vocabulary type for the entry to add or update",
)
@with_appcontext
def add_or_update(vocab_type: str | None, filepath: str, vocabulary_id: str):
    """Add or update the vocabulary."""
    if not vocab_type:
        file_name = os.path.basename(filepath)
        vocab_type, _ = os.path.splitext(file_name)

    try:
        service, needs_type = _get_service_for_type(vocab_type)
    except LookupError as e:
        click.secho(e, fg="red", err=True)
        sys.exit(1)

    with open(filepath, "r") as f:
        vocab_entries = yaml.safe_load(f)
        try:
            vocab_entry, *_ = [e for e in vocab_entries if e.get("id") == vocabulary_id]
        except ValueError:
            click.secho(f"could not find entry '{vocabulary_id}'", fg="red", err=True)
            sys.exit(1)

    # the special vocabularies don't need their type specified as part of the ID,
    # but generic vocabulary types do
    id_ = (vocab_type, vocabulary_id) if needs_type else vocabulary_id

    try:
        # first we try to update an existing vocabulary entry
        old_entry = service.read(system_identity, id_)._obj
        old_entry.setdefault("id", vocabulary_id)
        old_entry.pop("$schema")
        old_entry.pop("pid", None)
        old_entry.pop("type", None)

        # check if an update is actually necessary
        diffs = list(dictdiffer.diff(vocab_entry, old_entry))
        if diffs:
            if needs_type:
                vocab_entry["type"] = vocab_type

            new_entry = service.update(system_identity, id_, vocab_entry)._obj
            click.echo(f"updated '{vocab_type}' vocabulary: {new_entry}")
        else:
            click.secho("no updates necessary", fg="green")

    except (NoResultFound, PIDDoesNotExistError):
        # if the lookup failed, we need to add the vocabulary entry
        if needs_type:
            vocab_entry["type"] = vocab_type

        new_entry = service.create(system_identity, vocab_entry)._obj
        click.echo(f"added '{vocab_type}' vocabulary: {new_entry}")
