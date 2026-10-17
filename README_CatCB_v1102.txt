CatCB v1.10.2 — Taskbar, Selection & Updater Bugfix
===================================================

IMPORTANT: ONE-TIME MANUAL REPLACEMENT
The installed v1.10.1 updater itself is the component that leaves the visible CMD/findstr window. It cannot be fixed from inside that already-built EXE. For this first move to v1.10.2, do NOT install the new ZIP from v1.10.1's Settings > Update tab.

1. Extract the entire v1.10.2 kit to a new folder.
2. Run BUILD_TEST_EXE.bat and wait for a successful build.
3. This creates dist\CatCB.exe and dist\CatCB_Update_v1.10.2.zip.
4. Close CatCB completely.
5. Make a backup copy of the CatCB.exe you currently use.
6. Copy the NEW dist\CatCB.exe over the OLD CatCB.exe at your current installed path. Use the same path so existing shortcuts keep pointing to CatCB; if Windows still shows the old Chrome icon, unpin the old Chrome shortcut and pin the newly running CatCB.
7. Start the replaced CatCB.exe. It should open as a native CatCB window with the cat icon, without launching a normal Chrome window.

WHAT'S NEW IN v1.10.2
- Native CatCB window using pywebview + Edge WebView2 instead of hosting the app as a Chrome --app window. The taskbar identity and pinned shortcut now belong to CatCB.exe.
- Window starts maximized (normal title bar and taskbar visible; not kiosk fullscreen).
- Responsive layout for high-DPI/compact app viewports, and corrected four-column multi-select row layout.
- Startup shows a useful first preview without pre-checking/selecting a snippet for batch operations.
- Clicking in blank workspace areas or switching navigation clears the multi-selection; clicking actionable controls does not interrupt their action.
- Removed the old “NEW” badge from Report Email Studio.
- Replaced the CMD/tasklist/findstr update installer with a hidden VBScript helper. It checks for the app PID through WMI, waits no more than 120 seconds, logs each step, backs up the old EXE, replaces it, and launches the new version without opening Windows Terminal.
- Build verifies that HTML UI and Python launcher version labels match.

BUILD REQUIREMENTS
- Python launcher (`py`) and internet/package-mirror access for build dependencies.
- The builder installs PyInstaller, pywin32, and pywebview 6.2.1+ in the current user environment, without requesting admin rights.
- Microsoft Edge WebView2 Runtime is required to display the native app window. Most Windows/Office environments have it, but if CatCB shows a WebView2 startup error, ask IT to install/enable the WebView2 Runtime. CatCB deliberately does not silently open normal Chrome as a fallback.
- Corporate endpoint security may block unsigned self-built EXEs; follow company policy.

FUTURE UPDATE PACKAGE
After v1.10.2 has been installed manually once, future release builds create `dist\CatCB_Update_vX.Y.Z.zip`. You can then use Settings > Update to choose that ZIP. The v1.10.2 updater will run its helper hidden and does not use cmd.exe/findstr. Check `%APPDATA%\CatCB\update.log` if a future update does not finish.

DATA
- Settings/snippets: %APPDATA%\CatCB\state.json
- App log: %APPDATA%\CatCB\catcb.log
- Update log: %APPDATA%\CatCB\update.log
- Backups: %APPDATA%\CatCB\Backups
- Email drafts: %USERPROFILE%\Documents\CatCB\EmailDrafts
- Updating replaces the EXE only. It does not overwrite your JSON data/config.
