# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2025 TU Wien.
#
# Invenio-Utilities-TUW is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Management commands for drafts."""

import json
import os
import sys
from collections import namedtuple
from datetime import datetime, timedelta, timezone
from os.path import basename, isdir, isfile, join

import click
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_rdm_records.proxies import current_rdm_records_service as service
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.uow import UnitOfWork

from ..utils import get_identity_for_user, get_user_by_identifier
from .options import (
    option_as_user,
    option_owner,
    option_pid_type,
    option_pid_value,
    option_pretty_print,
    option_raw,
    option_vanity_pid,
)
from .utils import (
    auto_increase_bucket_limits,
    collect_file_paths,
    convert_to_recid,
    create_record_from_metadata,
    patch_metadata,
    read_metadata,
    set_record_owner,
)


@click.group()
def drafts():
    """Management commands for creation and publication of drafts."""


@drafts.command("list")
@option_as_user
@with_appcontext
def list_drafts(user):
    """List all drafts accessible to the given user."""
    identity = get_identity_for_user(user)
    recids = [
        dm.json["id"]
        for dm in service.draft_cls.model_cls.query.all()
        if dm is not None and dm.json is not None
    ]

    for recid in recids:
        try:
            draft = service.read_draft(id_=recid, identity=identity)
            recid = draft.id
            title = draft.data["metadata"].get("title", "-")
            files = draft._record.files
            if files.enabled:
                num_files = f"{len(files.entries):02}"
            else:
                num_files = "no"

            click.secho(f"{recid}\t{num_files} files\t{title}", fg="green")
        except PermissionDeniedError:
            pass


@drafts.command("create")
@click.argument("metadata_path", type=click.Path(exists=True))
@option_as_user
@click.option(
    "--publish",
    "-p",
    is_flag=True,
    default=False,
    help="publish the draft after creation (default: false)",
)
@option_owner
@option_vanity_pid
@with_appcontext
def create_draft(metadata_path, publish, user, owner, vanity_pid):
    """Create a new record draft with the specified metadata.

    The specified metadata path can either point to a JSON file containing the metadata,
    or it can point to a directory.
    In the former case, no files will be added to the created draft.
    In the latter case, it is assumed that the directory contains a file called
    "metadata.json".
    Further, all files contained in the "files/" subdirectory will be added to the
    draft, if such a subdirectory exists.
    """
    recid = None
    file_service = service.draft_files
    identity = get_identity_for_user(user)

    if isfile(metadata_path):
        metadata = read_metadata(metadata_path)
        draft = create_record_from_metadata(metadata, identity, vanity_pid=vanity_pid)
        recid = draft["id"]
        draft.files.enabled = False
        draft.commit()

    elif isdir(metadata_path):
        metadata_file_path = join(metadata_path, "metadata.json")
        deposit_files_path = join(metadata_path, "files")
        if not isfile(metadata_file_path):
            raise FileNotFoundError(metadata_file_path)

        metadata = read_metadata(metadata_file_path)
        draft = create_record_from_metadata(metadata, identity)
        recid = draft["id"]
        draft.files.enabled = True
        draft.commit()

        file_names = []
        file_paths = []
        if isdir(deposit_files_path):

            content = os.listdir(deposit_files_path)
            file_names = [
                basename(fn) for fn in content if isfile(join(deposit_files_path, fn))
            ]

            for fn in file_names:
                file_paths.append(join(deposit_files_path, fn))

            if len(content) != len(file_names):
                ignored = [
                    basename(fn)
                    for fn in content
                    if not isfile(join(deposit_files_path, fn))
                ]
                msg = f"ignored in '{deposit_files_path}': {ignored}"
                click.secho(msg, fg="yellow", err=True)

        auto_increase_bucket_limits(draft.files.bucket, file_paths)
        file_service.init_files(
            id_=recid, identity=identity, data=[{"key": fn} for fn in file_names]
        )

        for fn in file_names:
            file_path = join(deposit_files_path, fn)
            with open(file_path, "rb") as deposit_file:
                file_service.set_file_content(
                    id_=recid, file_key=fn, identity=identity, stream=deposit_file
                )

            file_service.commit_file(id_=recid, file_key=fn, identity=identity)

    else:
        raise TypeError(f"neither a file nor a directory: {metadata_path}")

    if owner:
        owner = get_user_by_identifier(owner)
        set_record_owner(draft, owner)
        if service.indexer:
            service.indexer.index(draft)

    if publish:
        service.publish(id_=recid, identity=identity)

    # commit, as there are code paths that don't have a commit otherwise
    db.session.commit()
    click.secho(recid, fg="green")


@drafts.command("show")
@option_pid_value
@option_pid_type
@option_as_user
@option_pretty_print
@option_raw
@with_appcontext
def show_draft(pid, pid_type, user, pretty_print, raw):
    """Show the stored data for the specified draft."""
    pid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    indent = 2 if pretty_print else None

    draft = service.read_draft(id_=pid, identity=identity)
    data = draft._record.model.json if raw else draft.data
    data = json.dumps(data, indent=indent)

    click.echo(data)


@drafts.command("update")
@click.argument("metadata_file", type=click.File("r"))
@option_pid_value
@option_pid_type
@option_as_user
@click.option(
    "--patch/--replace",
    "-P/-R",
    default=False,
    help=(
        "replace the draft's metadata entirely, or leave unmentioned fields as-is "
        "(default: replace)"
    ),
)
@option_owner
@with_appcontext
def update_draft(metadata_file, pid, pid_type, user, patch, owner):
    """Update the specified draft's metadata."""
    pid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    metadata = json.load(metadata_file)

    if patch:
        draft_data = service.read_draft(id_=pid, identity=identity).data.copy()
        metadata = patch_metadata(draft_data, metadata)

    if owner:
        draft = service.read_draft(id_=pid, identity=identity)._record
        owner = get_user_by_identifier(owner)
        set_record_owner(draft, owner)

    service.update_draft(id_=pid, identity=identity, data=metadata)
    click.secho(pid, fg="green")


@drafts.command("publish")
@option_pid_value
@option_pid_type
@option_as_user
@with_appcontext
def publish_draft(pid, pid_type, user):
    """Publish the specified draft."""
    pid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    service.publish(id_=pid, identity=identity)

    click.secho(pid, fg="green")


@drafts.command("delete")
@option_pid_value
@option_pid_type
@option_as_user
@with_appcontext
def delete_draft(pid, pid_type, user):
    """Delete the specified draft."""
    pid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    service.delete_draft(id_=pid, identity=identity)

    click.secho(pid, fg="red")


@drafts.group()
def files():
    """Manage files deposited with the draft."""


@files.command("add")
@click.argument("filepaths", metavar="PATH", type=click.Path(exists=True), nargs=-1)
@option_pid_value
@option_pid_type
@option_as_user
@with_appcontext
def add_files(filepaths, pid, pid_type, user):
    """Add the specified files to the draft."""
    recid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    file_service = service.draft_files
    draft = service.read_draft(id_=recid, identity=identity)._record

    # check if any of the files' basenames are duplicate
    paths = collect_file_paths(filepaths)
    keys = [basename(fp) for fp in paths]
    if len(set(keys)) != len(keys):
        click.secho(
            "aborting: duplicates in file names detected", fg="yellow", err=True
        )
        sys.exit(1)

    # check for existing duplicates
    existing_file_keys = list(draft.files.entries.keys())
    if any(k for k in keys if k in existing_file_keys):
        click.secho(
            "aborting: reuse of existing file names detected", fg="yellow", err=True
        )
        sys.exit(1)

    uow = UnitOfWork(db.session)
    try:
        # prepare the draft's file manager and bucket for files
        bucket_was_locked = draft.files.bucket.locked
        files_were_enabled = draft.files.enabled
        draft.files.bucket.locked = False
        if not files_were_enabled:
            draft.files.enabled = True
            draft.commit()
        db.session.flush()

        auto_increase_bucket_limits(draft.files.bucket, paths)
        file_service.init_files(
            id_=recid,
            identity=identity,
            data=[{"key": basename(fp)} for fp in paths],
            uow=uow,
        )

        for fp in paths:
            fn = basename(fp)
            with open(fp, "rb") as deposit_file:
                file_service.set_file_content(
                    id_=recid,
                    file_key=fn,
                    identity=identity,
                    stream=deposit_file,
                    uow=uow,
                )
            file_service.commit_file(id_=recid, file_key=fn, identity=identity, uow=uow)
        click.secho(recid, fg="green")

        # if the draft has already been published, we may need to enable the files for
        # the published record as well
        if draft.is_published and not files_were_enabled:
            record = service.record_cls.get_record(draft.id)
            record.files.enabled = True
            record.commit()

        uow.commit()

    except Exception as e:
        uow.rollback()
        if draft.files.enabled != files_were_enabled:
            draft.files.enabled = files_were_enabled
            draft.commit()

        click.secho(f"aborted due to error: {e}", fg="red", err=True)

    finally:
        if bucket_was_locked != draft.files.bucket.locked:
            draft.files.bucket.locked = bucket_was_locked

    db.session.commit()


@files.command("remove")
@click.argument("filekeys", metavar="FILE", nargs=-1)
@option_pid_value
@option_pid_type
@option_as_user
@with_appcontext
def remove_files(filekeys, pid, pid_type, user):
    """Remove the given deposited files from the draft.

    Note that this operation does not remove the files from storage!
    """
    recid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    file_service = service.draft_files
    draft = service.read_draft(id_=recid, identity=identity)._record

    bucket_was_locked = draft.files.bucket.locked
    draft.files.bucket.locked = False
    uow = UnitOfWork(db.session)
    try:
        for file_key in filekeys:
            try:
                file_service.delete_file(
                    id_=recid, file_key=file_key, identity=identity, uow=uow
                )
                click.secho(file_key, fg="red")

            except KeyError as err:
                click.secho(f"error: {err}", fg="yellow", err=True)

        if not draft.files.entries:
            draft.files.enabled = False
            draft.commit()

        uow.commit()

    except Exception as e:
        uow.rollback()
        click.secho(f"aborted due to error: {e}", fg="red", err=True)

    finally:
        draft.files.bucket.locked = bucket_was_locked
        db.session.commit()


@files.command("list")
@option_pid_value
@option_pid_type
@option_as_user
@with_appcontext
def list_files(pid, pid_type, user):
    """Show a list of files deposited with the draft."""
    recid = convert_to_recid(pid, pid_type)
    identity = get_identity_for_user(user)
    draft = service.read_draft(id_=recid, identity=identity)._record

    for name, rec_file in draft.files.entries.items():
        fi = rec_file.file
        if fi:
            click.secho(f"{name}\t{fi.uri}\t{fi.checksum}", fg="green")
        else:
            click.secho(name, fg="red")


@files.command("verify")
@option_pid_value
@option_pid_type
@with_appcontext
def verify_files(pid, pid_type):
    """Verify the checksums for each of the draft's files."""
    recid = convert_to_recid(pid, pid_type)
    draft = service.read_draft(id_=recid, identity=system_identity)._record
    num_errors = 0

    for name, rec_file in draft.files.entries.items():
        if not rec_file.file:
            click.secho(name, fg="red")

        elif rec_file.file.verify_checksum():
            click.secho(name, fg="green")

        else:
            click.secho(f"{name}: failed checksum verification", fg="yellow", err=True)
            num_errors += 1

    # persist the 'last_check_at' timestamp for each file
    db.session.commit()

    if num_errors > 0:
        click.secho(
            f"{num_errors} files failed the checksum verification",
            fg="yellow",
            err=True,
        )
        sys.exit(1)


@files.command("fix-state")
@option_pid_value
@option_pid_type
@with_appcontext
def fix_state(pid, pid_type):
    """Fix the draft's file manager state and lock the bucket."""
    recid = convert_to_recid(pid, pid_type)
    draft = service.read_draft(id_=recid, identity=system_identity)._record
    draft.files.lock()
    draft.files.enabled = bool(draft.files.entries)
    draft.commit()
    db.session.commit()


@drafts.command("list-stale")
@click.option(
    "--days",
    "-d",
    "num_days",
    help="threshold after how many days a draft is considered stale",
    default=30,
    type=int,
)
@with_appcontext
def list_stale_drafts(num_days):
    """List all drafts that haven't been updated for a while."""
    dc, mc = service.draft_cls, service.draft_cls.model_cls
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=abs(num_days))

    # `draft.status` uses the system field:
    # `invenio_rdm_records.records.systemfields.draft_status.DraftStatus`
    stale_drafts = [
        draft
        for draft in (
            dc(model.data, model=model)
            for model in mc.query.filter(mc.updated <= cutoff_date).all()
        )
        if draft and draft.status in ["new_version_draft", "draft"]
    ]

    # collect infos about stale drafts
    draft_info = namedtuple("DraftInfo", ["recid", "title", "uploader", "updated"])
    stale_draft_infos = []
    for draft in stale_drafts:
        recid = draft.pid.pid_value
        title = draft.metadata.get("title", "[UNNAMED]")
        uploader = draft.parent.access.owned_by
        uploader_email = uploader.resolve().email if uploader else "[N/A]"
        updated = draft.updated.date() if draft.updated else "[N/A]"
        stale_draft_infos.append(draft_info(recid, title, uploader_email, updated))

    # print the info about stale drafts, sorted by the owner's email address
    max_email_len = max((len(di.uploader) for di in stale_draft_infos))
    for info in sorted(stale_draft_infos, key=lambda di: di.uploader):
        email = info.uploader.rjust(max_email_len)
        click.echo(f'{info.recid} - {email} @ {info.updated} - "{info.title}"')
