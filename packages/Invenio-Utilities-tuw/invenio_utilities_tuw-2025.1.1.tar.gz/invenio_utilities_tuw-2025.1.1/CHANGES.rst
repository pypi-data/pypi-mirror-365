..
    Copyright (C) 2020 - 2025 TU Wien.

    Invenio-Utilities-TUW is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======


Version v2025.1.0 (released 2025-07-29)

- fix: remove unexpected keyword arg for `click.argument()`


Version v2025.1.0 (released 2025-07-29)

- project: update package metadata, bump python requirement, unpin Invenio-App-RDM
- chore: fix some complaints from SonarQube


Version v2025.0.0 (released 2025-03-10)

- global: remove capabilities for multiple record owners
- global: drop old way of fetching records service
- drafts: update "files {add,remove}" command to also work with already published drafts
- records: add "files fix-state" command to fix files manager state and lock the bucket
- vocabularies: add basic vocabulary management commands


Version v2024.2 (released 2024-06-24, updated 2024-09-19)

- v12 compat: Replace ``Flask-BabelEx`` with ``Invenio-i18n``
- global: modernize setup and base it on ``uv``


Version 2024.1 (released 2024-02-08, updated 2024-03-13)

- Add CLI commands for generating simple reports about the number of records
- Add CLI command for listing stale drafts


Version 2022.2 (released 2022-07-19, updated 2022-11-23)

- v9 compat: Replace usage of user.profile with user.user_profile
- Add CLI command for showing users' API tokens
- Add CLI command for calling all known services' ``rebuild_index()``
- Migrate from setup.py to setup.cfg


Version 2022.1 (released 2022-03-25, updated 2022-07-04)

- Rename old 'orphans' subcommand for files to 'zombies'
- Add 'orphans' subcommand for files that operates on orphaned DB entries
- Add command to verify the integrity of all files
- Update file verification commands for drafts and records
- Automatically increase bucket limits when adding files to drafts


Version 2021.2 (released 2021-12-07, updated 2021-12-15)

- Bump dependencies (InvenioRDM v7)
- Add option to show/hide users' full names


Version 2021.1 (released 2021-07-15)

- Initial public release.
