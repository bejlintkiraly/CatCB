from __future__ import annotations

import os
import hashlib
import json
import re
import zipfile
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG = ROOT / "CatCB_build.log"
EXE_PATH = ROOT / "dist" / "CatCB.exe"
UPDATE_PACKAGE_PATH = None
REQUIRED = [
    "CatCB_Desktop_Launcher_v14.py",
    "index.html",
    "CatCB_Space_v14.jpg",
    "CatCB_Mascot_v14.png",
    "CatCB_Mascot_v14.ico",
]
PYINSTALLER_MIN = "6.22.3"

def write_log(text: str) -> None:
    line = text.rstrip("\n")
    print(line, flush=True)
    try:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass

def run_stream(args: list[str], heading: str) -> int:
    write_log("")
    write_log("=" * 72)
    write_log(heading)
    write_log("COMMAND: " + subprocess.list2cmdline(args))
    write_log("=" * 72)
    try:
        proc = subprocess.Popen(
            args,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            bufsize=1,
            env=os.environ.copy(),
        )
    except OSError as exc:
        write_log(f"Could not start command: {exc}")
        return 9009

    assert proc.stdout is not None
    for line in proc.stdout:
        print(line, end="", flush=True)
        try:
            with LOG.open("a", encoding="utf-8") as f:
                f.write(line)
        except OSError:
            pass
    return proc.wait()

def main() -> int:
    try:
        LOG.write_text(
            "CatCB Windows test EXE build log\n"
            f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Python: {sys.executable}\n"
            f"Source folder: {ROOT}\n",
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"Warning: couldn't create build log: {exc}", flush=True)

    write_log("")
    write_log("  CatCB v1.10.3 — EXE BUILDER")
    write_log("  No administrator rights are requested by this builder.")
    write_log("")

    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    if missing:
        write_log("ERROR: Required CatCB files are missing next to this builder:")
        for name in missing:
            write_log("  - " + name)
        write_log("")
        write_log("Fix: extract the COMPLETE CatCB ZIP into one folder, then put/run this builder in that folder.")
        return 2

    write_log("Python executable: " + sys.executable)
    write_log("Python version: " + sys.version.replace("\n", " "))
    write_log("Build folder: " + str(ROOT))
    write_log("Build log: " + str(LOG))
    source_text = (ROOT / "CatCB_Desktop_Launcher_v14.py").read_text(encoding="utf-8")
    html_text = (ROOT / "index.html").read_text(encoding="utf-8")
    backend_match = re.search(r'^APP_VERSION = "([0-9]+\.[0-9]+\.[0-9]+)"$', source_text, re.M)
    ui_match = re.search(r'const UI_APP_VERSION="([0-9]+\.[0-9]+\.[0-9]+)"', html_text)
    if not backend_match or not ui_match or backend_match.group(1) != ui_match.group(1):
        write_log("ERROR: UI and launcher version labels don't match.")
        write_log("Launcher version: " + (backend_match.group(1) if backend_match else "not found"))
        write_log("UI version: " + (ui_match.group(1) if ui_match else "not found"))
        write_log("Do not build a mixed-version package; send this log for correction.")
        return 4
    release_version = backend_match.group(1)
    write_log("Release version: " + release_version)

    rc = run_stream(
        [sys.executable, "-m", "pip", "install", "--user", "--upgrade",
         f"pyinstaller>={PYINSTALLER_MIN}", "pywin32", "pywebview>=6.2.1"],
        "[1/3] Installing build dependencies (network access may be required)"
    )
    if rc != 0:
        write_log("")
        write_log(f"ERROR: dependency installation failed with exit code {rc}.")
        write_log("Check corporate proxy/package mirror or whether pip installs are allowed.")
        return rc

    rc = run_stream(
        [sys.executable, "-m", "PyInstaller", "--version"],
        "[2/3] Verifying PyInstaller"
    )
    if rc != 0:
        write_log("ERROR: PyInstaller could not be launched.")
        return rc

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--onefile", "--windowed",
        "--name", "CatCB",
        "--icon", "CatCB_Mascot_v14.ico",
        "--add-data", "index.html;.",
        "--add-data", "CatCB_Space_v14.jpg;.",
        "--add-data", "CatCB_Mascot_v14.png;.",
        "--add-data", "CatCB_Mascot_v14.ico;.",
        "--hidden-import", "pythoncom",
        "--hidden-import", "pywintypes",
        "--hidden-import", "win32timezone",
        "--hidden-import", "win32com",
        "--hidden-import", "win32com.client",
        "--collect-submodules", "win32com",
        "--collect-all", "webview",
        "--collect-all", "pythonnet",
        "--collect-all", "clr_loader",
        "--hidden-import", "clr",
        "--hidden-import", "System",
        "--hidden-import", "webview.platforms.edgechromium",
        "--hidden-import", "webview.platforms.winforms",
        "CatCB_Desktop_Launcher_v14.py",
    ]
    rc = run_stream(cmd, "[3/3] Building CatCB.exe (this can take a few minutes)")
    if rc != 0:
        write_log("")
        write_log(f"ERROR: PyInstaller failed with exit code {rc}.")
        write_log("Send CatCB_build.log so the error can be diagnosed.")
        return rc

    if not EXE_PATH.is_file():
        write_log("")
        write_log("ERROR: PyInstaller returned success but the EXE wasn't found at:")
        write_log("  " + str(EXE_PATH))
        return 3

    try:
        exe_hash = hashlib.sha256()
        with EXE_PATH.open("rb") as exe_file:
            for chunk in iter(lambda: exe_file.read(1024 * 1024), b""):
                exe_hash.update(chunk)
        release_notes = ("CatCB v" + release_version
            + "\n- Fixed startup defaults: starter snippets appear on first launch only and stay deleted after the user removes them"
            + "\n- Saved empty snippet lists are now treated as intentional; storage connection errors no longer invent starter snippets"
            + "\n- Native CatCB window with its own taskbar icon (pywebview + WebView2), not a Chrome app window"
            + "\n- Maximized normal window with title bar and Windows taskbar visible"
            + "\n- Fixed responsive/high-DPI multi-select list layout and its four-column grid"
            + "\n- Startup no longer pre-selects the first snippet for batch actions; clicking elsewhere clears batch selection"
            + "\n- Removed the Report Email Studio NEW badge"
            + "\n- Replaced CMD/tasklist/findstr updater with hidden VBScript, WMI process polling, backup, rollback and timeout"
            + "\n- UI and launcher versions are checked during build; user data stays in the separate JSON config")
        manifest = {
            "app_id": "CatCB",
            "version": release_version,
            "executable": "CatCB.exe",
            "sha256": exe_hash.hexdigest(),
            "release_notes": release_notes,
        }
        update_package = ROOT / "dist" / f"CatCB_Update_v{release_version}.zip"
        with zipfile.ZipFile(update_package, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.write(EXE_PATH, arcname="CatCB.exe")
            archive.writestr("update_manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        write_log("Update package: " + str(update_package))
        write_log("Update package manifest includes the SHA-256 hash of this exact EXE.")
    except Exception as exc:
        write_log("ERROR: EXE built, but update ZIP generation failed: " + str(exc))
        return 5

    write_log("")
    write_log("=" * 72)
    write_log("BUILD COMPLETE")
    write_log("EXE: " + str(EXE_PATH))
    write_log("Update ZIP: " + str(update_package))
    write_log("Config: %APPDATA%\\CatCB\\state.json")
    write_log("MSG drafts: %USERPROFILE%\\Documents\\CatCB\\EmailDrafts")
    write_log("If corporate endpoint security blocks the unsigned test EXE, use the Python launcher or ask IT for approval.")
    write_log("=" * 72)
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        print("")
        if exit_code == 0:
            print("Success. CatCB.exe and CatCB_Update_vX.Y.Z.zip are in the dist folder.", flush=True)
        else:
            print(f"Build stopped with exit code {exit_code}. Log: {LOG}", flush=True)
        input("Press Enter to close this window...")
        raise SystemExit(exit_code)
    except KeyboardInterrupt:
        print("\nBuild interrupted by user.", flush=True)
        input("Press Enter to close this window...")
        raise SystemExit(130)
