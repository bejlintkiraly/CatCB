# CatCB 🐱

### A little tool that makes everyday work easier. 🐾

<p align="center">
  <img src="assets/KYg9ryo-funny-cat-desktop-wallpaper.jpg" alt="A curious cat welcoming you to CatCB" width="750">
</p>

Hey, welcome to CatCB! 😸

CatCB started with a pretty simple idea: I wanted a place to keep all the text snippets I use regularly, so I wouldn't have to keep searching for them or typing the same things over and over again.

One thing led to another, I kept adding little improvements, changed the interface until it felt right, and eventually ended up with a much more useful tool than I originally planned.

So, here it is! I thought I'd share it in case somebody else finds it useful, too.

And yes, I clearly have a thing for cats. You're going to notice. 🐈

## 🐾 So, what does CatCB actually do?

CatCB is a small Windows app that helps me save time on repetitive tasks. It keeps frequently used text in one place and makes it easier to reuse whenever I need it.

Here's what you can do with it:

- **Save text snippets** in your own categories, so you can find them without digging through old notes.
- **Select and manage multiple snippets** instead of handling everything one item at a time.
- **Copy, cut, paste and delete** snippets using the available shortcuts.
- **Undo and redo changes** when you need to go back a step.
- **Customize your organization** with categories and icons.
- **Prepare reports** using Report Studio.
- **Work with email content** using Outlook Studio and supported Outlook features.
- **Save Outlook messages as `.msg` files**, including attachments where supported.
- **Keep your data locally** in your Windows user profile.

The whole point is to make everyday work a little less repetitive. Nothing complicated — just a handy tool that does what I need it to do. 🐈‍⬛

## 😻 A peek inside

Here's what CatCB looks like in action.

<p align="center">
  <img src="assets/main-window.png" alt="CatCB main application window" width="850">
</p>

<p align="center">
  <em>Your snippets, your categories, your way of working. 🐾</em>
</p>

*More screenshots may find their way here as the project grows.*

## 🐱 Get CatCB

Want to give it a try?

The easiest option is to download the latest compiled Windows version from GitHub.

<p align="center">
  <a href="https://github.com/bejlintkiraly/CatCB/releases/latest">
    <strong>🐾 Download CatCB — latest release</strong>
  </a>
</p>

1. Open the [latest Releases page](https://github.com/bejlintkiraly/CatCB/releases/latest).
2. Download `CatCB.exe`.
3. Save it somewhere convenient on your PC.
4. Run it and have a look around. 😸

You don't need Python or any development tools just to use the prebuilt version.

<p align="center">
  <img src="assets/ehzDdxV.jpg" alt="A little cat keeping an eye on the download" width="420">
</p>

### 🛡️ A quick note about Windows SmartScreen

Because CatCB is an independently published application, Windows SmartScreen may show a warning when you first launch it. This can happen with applications that don't have an established reputation or a trusted digital signature.

That warning doesn't automatically mean an application is malicious, but it shouldn't be ignored either.

For your own peace of mind, download CatCB only from the official GitHub Releases page. If you're unsure about the file or don't trust its source, don't run it.

## 🖥️ What do you need?

Not much!

- A Windows PC.
- The downloaded CatCB executable.
- Microsoft Outlook Classic installed and configured if you want to use features that depend on its desktop integration.

Some features may behave differently depending on your Windows and Outlook setup.

## 🔧 Curious about the source code?

The repository includes the files used to build CatCB, along with a Windows build script.

If you'd like to build it yourself:

1. Install Python and make sure the required components are available.
2. Download the source code from this repository.
3. Extract it into a folder.
4. Run `BUILD_TEST_EXE.bat`.
5. If the build finishes successfully, look for `CatCB.exe` in the `dist` folder.

The exact requirements depend on the current build script and your environment. If something goes wrong, check the error output first.

If you just want to use CatCB, downloading the prebuilt release is the easier route. 🐈

## 💾 Where does CatCB keep my data?

Your application data is stored locally under your Windows user profile:

```text
%APPDATA%\CatCB\state.json
```

Keeping the data separate from the executable means that replacing CatCB with a newer version normally won't require you to start from scratch.

Still, please make a backup before trying a new build or making major changes. It's better to be safe than sorry — and cats are notoriously bad at recovering lost files. 🐱

One more thing: if you've saved personal or sensitive information in your snippets, check your data before sharing the file with anyone.

## 🔄 Updates

When a new version is available, you'll find it on the Releases page:

**[🐾 Browse CatCB releases](https://github.com/bejlintkiraly/CatCB/releases)**

Before updating, close CatCB and back up your data if it contains anything important. Always download releases from the official repository.

## 💬 Found a bug? Have an idea?

I'd love to hear how CatCB works for you.

If you spot a bug, run into something confusing, or have an idea for a feature, feel free to open an issue on GitHub.

I can't promise every suggestion will make it into the app, but thoughtful feedback is always welcome. After all, there's always room to make a good little tool even better. 🐾

<p align="center">
  <a href="https://github.com/bejlintkiraly/CatCB/issues">
    <strong>🐈 Open an issue or suggest an improvement</strong>
  </a>
</p>

<p align="center">
  <img src="assets/Fva28N5.jpg" alt="A fluffy cat taking a little break" width="380">
</p>

## 📜 License and usage

Copyright (c) 2026 bejlintkiraly. All rights reserved.

This project is publicly available for viewing on GitHub, but no license is granted to use, copy, modify, or redistribute the source code. All rights are reserved unless explicit permission is granted by the copyright holder.

You may download and use the official prebuilt releases for personal use. Permission to use the application does not grant permission to redistribute the executable or publish modified versions.

No third-party rights are granted or changed by this notice.

## ⚠️ A small disclaimer

CatCB is provided "as is", without warranties of any kind. Use it at your own discretion and keep backups of important data.

CatCB is an independent personal project. It is not affiliated with, endorsed by, or officially connected to Microsoft.

<p align="center">
  <img src="assets/m9v64v6.jpg" alt="One last little cat saying goodbye" width="460">
</p>

<p align="center">
  <strong>Thanks for stopping by! 🐱</strong>
  <br>
  Made with a lot of tweaking, a little stubbornness, and an unreasonable number of cat pictures. 🐈‍⬛
</p>
