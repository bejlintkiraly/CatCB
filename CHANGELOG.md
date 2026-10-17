# Changelog

## v1.10.2
- Added a native CatCB window using pywebview/WebView2 so Windows presents CatCB as its own app rather than Chrome.
- Starts as a normal maximized window with the Windows taskbar visible.
- Fixed multi-select row layout and responsive sizing.
- Avoided pre-checking a snippet for batch actions on startup.
- Clears multi-selection when clicking blank workspace or changing navigation.
- Removed the Report Email Studio “NEW” badge.
- Reworked the update helper to run hidden, use a timeout, write an update log, and back up the old executable before replacement.
- Keeps local user configuration separate from program updates.
- Sanitized repository defaults: no hard-coded work recipients; report email fields start blank and the sample subject/body use generic IT-operations wording.

## Earlier history

The in-app About tab contains the summarized feature history for v1.0–v1.10.2.
