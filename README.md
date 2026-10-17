# CatCB

**CatCB** is a lightweight, dark-mode desktop-style IT productivity app for keeping reusable snippets, commands, incident updates, shift handovers, and Outlook email templates in one searchable place.

> Created by Bejlint 💚. CatCB is a personal project and is not an official product of any employer.

## Features

- Searchable snippet library, categories, favorites, multi-select, and clipboard operations.
- Custom categories and icons, right-click context menus, undo/redo, autosave, and Recycle Bin.
- Outlook Classic draft creation, `.msg` export, and optional report attachments.
- Local JSON settings and data, backup/import/export, and an in-app update center.
- Native Windows app window using pywebview and Microsoft Edge WebView2.

## Build on Windows

1. Download or clone this repository and extract it into a writable folder.
2. Install a supported Python version and ensure the `py` launcher works.
3. Run `BUILD_TEST_EXE.bat` as your normal user (do not run as administrator unless your organization specifically requires it).
4. The builder installs the needed Python packages for the current user and produces `dist\CatCB.exe`. Successful build logs are written as `CatCB_build.log` next to the build files.
5. Microsoft Edge WebView2 Runtime is required for the native UI. Outlook integration additionally requires Outlook Classic with a configured profile.

Corporate endpoint protection may block unsigned self-built executables. Follow your organization's software approval policies; do not bypass them.

## Local data and privacy

CatCB stores the user's snippets and settings in `%APPDATA%\CatCB\state.json`. Logs and temporary update files are stored under the user's CatCB application-data directory. Outlook drafts are saved under `%USERPROFILE%\Documents\CatCB\EmailDrafts` when requested.

The repository intentionally contains **no personal configuration file, built EXE, build log, user snippet library, or company-specific recipient defaults**. The Report Email Studio recipient fields start empty. Avoid committing work data, real recipient lists, screenshots of internal systems, access tokens, certificates, or secrets.

## Releases and updates

The source currently includes the local update-package workflow. A trusted release endpoint/repository and release process must be configured before remote auto-update checks can be enabled safely. See `CatCB_Auto_Update_Guide.txt` for the design notes. Do not publish real update hashes or download links until a release EXE has been built and reviewed.

## Version

Source baseline: **v1.10.2**.
See [CHANGELOG.md](CHANGELOG.md) for the version summary.

## License

## License

Copyright (c) 2026 bejlintkiraly. All rights reserved.

This project is publicly available for viewing on GitHub, but no license is granted to use, copy, modify, or redistribute the source code. All rights are reserved unless explicit permission is granted by the copyright holder.
