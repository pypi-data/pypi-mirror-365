# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2025 TU Wien.
#
# Invenio-Utilities-TUW is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Utilities for the CLI commands."""

import json
import os
from os.path import basename, isdir, isfile, join

import click
from invenio_db import db
from invenio_pidstore.errors import PIDAlreadyExists
from invenio_pidstore.models import PersistentIdentifier
from invenio_rdm_records.proxies import current_rdm_records_service as service


def read_metadata(metadata_file_path):
    """Read the record metadata from the specified JSON file."""
    metadata = None
    with open(metadata_file_path, "r") as metadata_file:
        metadata = json.load(metadata_file)

    if metadata is None:
        raise TypeError(f"not a valid json file: {metadata_file_path}")

    return metadata


def create_record_from_metadata(
    metadata, identity, vanity_pid=None, vanity_pid_type="recid"
):
    """Create a draft from the specified metadata."""
    if vanity_pid is not None:
        # check if the vanity PID is already taken, before doing anything stupid
        count = PersistentIdentifier.query.filter_by(
            pid_value=vanity_pid, pid_type=vanity_pid_type
        ).count()

        if count > 0:
            raise PIDAlreadyExists(pid_type=vanity_pid_type, pid_value=vanity_pid)

    draft = service.create(identity=identity, data=metadata)._record

    if vanity_pid:
        # service.update_draft() is called to update the IDs in the record's metadata
        # (via record.commit()), re-index the record, and commit the db session
        if service.indexer:
            service.indexer.delete(draft)

        draft.pid.pid_value = vanity_pid
        db.session.commit()

        draft = service.update_draft(
            vanity_pid, identity=identity, data=metadata
        )._record

    return draft


def patch_metadata(metadata: dict, patch: dict) -> dict:
    """Replace the fields mentioned in the patch, while leaving others as is.

    The first argument's content will be changed during the process.
    """
    for key in patch.keys():
        val = patch[key]
        if isinstance(val, dict):
            patch_metadata(metadata[key], val)
        else:
            metadata[key] = val

    return metadata


def get_object_uuid(pid_value, pid_type):
    """Fetch the UUID of the referenced object."""
    uuid = (
        PersistentIdentifier.query.filter_by(pid_value=pid_value, pid_type=pid_type)
        .first()
        .object_uuid
    )

    return uuid


def convert_to_recid(pid_value, pid_type):
    """Fetch the recid of the referenced object."""
    if pid_type != "recid":
        object_uuid = get_object_uuid(pid_value=pid_value, pid_type=pid_type)
        query = PersistentIdentifier.query.filter_by(
            object_uuid=object_uuid,
            pid_type="recid",
        )
        pid_value = query.first().pid_value

    return pid_value


def set_record_owner(record, owner, commit=True):
    """Set the record's owner, assuming an RDMRecord-like record object."""
    parent = record.parent

    parent.access.owned_by = owner
    if commit:
        parent.commit()
        db.session.commit()


def bytes_to_human(size):
    """Make the size (in bytes) more human-readable."""
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    unit = units[0]
    for u in units[1:]:
        if size < 1024:
            break

        size /= 1024
        unit = u

    return f"{size:.2f} {unit}"


def is_owned_by(user, record):
    """Check if the record is owned by the given user."""
    owner = record.parent.access.owned_by
    return owner and owner.owner_id == user.id


def collect_file_paths(paths):
    """Collect file paths from the given paths.

    If one of the given paths is a directory, its path will be replaced with the
    paths of all files it contains.
    If it contains any subdirectories however, then it will be skipped instead.
    """
    paths_ = []
    for path in paths:
        if isdir(path):
            # add all files (no recursion into sub-dirs) from the directory
            content = os.listdir(path)
            file_names = [basename(fn) for fn in content if isfile(join(path, fn))]

            if len(content) != len(file_names):
                ignored = [basename(fn) for fn in content if not isfile(join(path, fn))]
                msg = f"ignored in '{path}': {ignored}"
                click.secho(msg, fg="yellow", err=True)

            paths_ = [join(path, fn) for fn in file_names]
            paths_.extend(paths_)

        elif isfile(path):
            paths_.append(path)

    return paths_


def auto_increase_bucket_limits(bucket, filepaths, to_unlimited=False):
    """Dynamically increase the bucket quota if necessary."""
    file_sizes = [os.path.getsize(filepath) for filepath in filepaths]
    sum_sizes = sum(file_sizes)
    max_size = max(file_sizes)

    if bucket.quota_left is not None:
        if to_unlimited:
            bucket.quota_size = None

        else:
            # see how big the files are, and compare it against the bucket's quota
            req_extra_quota = sum_sizes - bucket.quota_left

            # if we need some extra quota, increase it
            if req_extra_quota > 0:
                bucket.quota_size += req_extra_quota

    if bucket.max_file_size and bucket.max_file_size < max_size:
        # do similar checks for the maximum file size
        if to_unlimited:
            bucket.max_file_size = None
        else:
            bucket.max_file_size = max_size

    # make changes known
    db.session.flush()
