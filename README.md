# 🐱 CatCB

**A little tool that makes everyday work easier.**

CatCB is a small Windows application I built to make my everyday work a little easier. It started with a simple idea: keep frequently used text snippets in one place and make them quick and easy to use.

Over time, it grew into something more than that. I added features, adjusted the interface to suit the way I like to work, and turned it into a personal productivity tool that I now want to share with others.

It's built around a simple idea: less time repeating the same tasks, more time getting things done.

## ✨ What can CatCB do?

- **Manage text snippets** — keep frequently used text organized into custom categories.
- **Work with multiple snippets** — select, copy, move, and delete several items at once.
- **Stay organized** — use custom categories and icons to make content easier to find.
- **Undo and redo** — recover from changes while working with your snippets.
- **Prepare emails and reports** — use the built-in Report & Outlook Studio tools to put content together more easily.
- **Work with Outlook messages** — prepare drafts and save messages as `.msg` files, including attachments where supported.
- **Make it your own** — personalize parts of the interface to suit your preferences.
- **Keep your work saved** — your application data is stored locally in your Windows user profile.

CatCB is a personal project, so features and the interface may evolve as I continue improving it.

## 📥 Download

The easiest way to get started is to download the latest compiled Windows version.

**[➡️ Download CatCB from GitHub Releases](https://github.com/bejlintkiraly/CatCB/releases/latest)**

1. Open the Releases page.
2. Download `CatCB.exe` from the latest release.
3. Save it somewhere convenient on your Windows PC.
4. Run the application.

You don't need to build the application from source just to use the prebuilt release.

### A note about Windows SmartScreen

Since CatCB is an independently published application and its executable may not have a trusted digital signature or an established download reputation, Windows SmartScreen may display a warning when you launch it.

This warning does not automatically mean the application is malicious, but it should not be ignored either.

Make sure you downloaded the executable from the official CatCB GitHub Releases page. If Windows displays a warning and you are not comfortable proceeding, cancel the launch. Only choose to continue if you have verified the source and are satisfied that you trust the file.

## 🖥️ Requirements

- A Windows PC.
- The prebuilt release for normal use.
- Microsoft Outlook Classic, installed and configured, for features that rely on its desktop integration.

Some features may depend on your local Windows and Outlook configuration.

## 🛠️ Building from source

Want to build CatCB yourself? Here's the general process.

1. Make sure Python is installed on your Windows PC and available to the build script.
2. Open the [CatCB repository](https://github.com/bejlintkiraly/CatCB).
3. Download the source code and extract the archive to a folder.
4. Open the extracted folder.
5. Run `BUILD_TEST_EXE.bat`.
6. When the build completes successfully, look for the generated executable in the `dist` folder.

The exact build output depends on the script and the environment. If the build fails, check the error message and make sure the required Python components are available.

The project is intended to be buildable in a regular Windows user environment, although corporate restrictions or local security policies may affect the process.

## 💾 Where is my data stored?

CatCB stores its application data locally under your Windows user profile:

```text
%APPDATA%\CatCB\state.json
```

This allows your saved data to remain separate from the executable, so replacing the application with a newer release does not normally mean starting from scratch.

**A quick tip:** back up your CatCB data before making major changes or experimenting with a new build. Your saved snippets and settings may be important to you.

Also, remember that anything you save in your snippets may contain personal or sensitive information. Don't share your configuration file publicly without checking its contents first.

## 🔄 Updates

Check the [GitHub Releases page](https://github.com/bejlintkiraly/CatCB/releases) for new versions and their changelogs.

Before updating, it's a good idea to close CatCB and keep a backup of your saved data. Only download releases from the official repository.

## 💬 Feedback and suggestions

CatCB started as a tool for my own workflow, and that's still a big part of what makes it special to me.

If you find a bug, have an idea for an improvement, or simply want to share your experience, feel free to open an issue on GitHub.

Constructive feedback is always welcome!

**[Report a bug or suggest an improvement](https://github.com/bejlintkiraly/CatCB/issues)**

## 📄 Source code and usage terms

Copyright (c) 2026 bejlintkiraly. All rights reserved.

This repository is publicly available so people can discover and inspect the CatCB project.

No general license is granted to reuse, copy, modify, redistribute, or incorporate the source code into other projects. Such use requires prior permission from the copyright holder, unless otherwise required by applicable law or the terms governing use of the GitHub platform.

You may download and use the official prebuilt releases for personal use. Permission to use the application does not grant permission to redistribute the executable or publish modified versions.

No third-party rights are granted or changed by this notice.

## ⚠️ Disclaimer

CatCB is provided "as is", without warranties of any kind. Use it at your own discretion and keep backups of important data.

CatCB is an independent personal project and is not affiliated with, endorsed by, or officially connected to Microsoft.

---

*Made with a lot of tweaking, a little stubbornness, and a cat-inspired touch. 🐱*
