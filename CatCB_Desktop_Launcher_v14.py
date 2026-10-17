from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from datetime import datetime
import base64
import hashlib
import io
import zipfile
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid
import webbrowser
import traceback

APP_NAME = "CatCB"
APP_VERSION = "1.10.3"
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
DATA_DIR = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
STATE_FILE = DATA_DIR / "state.json"
DRAFT_DIR = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Documents" / APP_NAME / "EmailDrafts"
TEMP_ATTACHMENT_DIR = DATA_DIR / "TempAttachments"
PREFERRED_PORT = 43827
MAX_ATTACHMENT_BYTES = 24 * 1024 * 1024
MAX_REQUEST_BYTES = 260_000_000
MAX_UPDATE_PACKAGE_BYTES = 180 * 1024 * 1024
MAX_UPDATE_EXE_BYTES = 200 * 1024 * 1024
UPDATE_STAGING_DIR = DATA_DIR / "UpdateStaging"
PENDING_UPDATES = {}
UPDATE_APPLY_SCHEDULED = False
OL_MAIL_ITEM = 0
OL_MSG = 3
LAST_ACTIVITY = time.monotonic()
STOP_EVENT = threading.Event()


def safe_filename(name, default="attachment"):
    name = Path(str(name or "")).name
    name = re.sub(r'[^A-Za-z0-9 ._()-]+', "_", name).strip(" .")
    return name or default


def log_error(message):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        log_file = DATA_DIR / "catcb.log"
        with log_file.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")
    except Exception:
        pass


def console_info(message):
    try:
        if sys.stdout is not None:
            print(message)
    except Exception:
        pass


def show_error(title, message):
    log_error(f"{title}: {message}")
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, str(message), str(title), 0x10)
            return
        except Exception:
            pass
    print(f"{title}: {message}")


def config_paths():
    return {
        "config_file": str(STATE_FILE),
        "config_dir": str(DATA_DIR),
        "email_drafts_dir": str(DRAFT_DIR),
        "application_file": str(sys.executable if getattr(sys, "frozen", False) else Path(__file__).resolve()),
        "is_frozen": bool(getattr(sys, "frozen", False)),
        "log_file": str(DATA_DIR / "catcb.log"),
    }


def open_local_path(which):
    paths = config_paths()
    if which == "config_folder":
        path = DATA_DIR
    elif which == "config_file":
        path = STATE_FILE
        if not path.exists():
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"snippets": [], "deleted": [], "categories": []}, indent=2), encoding="utf-8")
    elif which == "draft_folder":
        path = DRAFT_DIR
        path.mkdir(parents=True, exist_ok=True)
    elif which == "log_file":
        path = DATA_DIR / "catcb.log"
        if not path.exists():
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            path.write_text("CatCB log\n", encoding="utf-8")
    else:
        raise ValueError("Unknown local path.")
    if os.name == "nt":
        os.startfile(str(path))
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])
    return str(path)


def version_tuple(version):
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(version or "")):
        raise ValueError("The update version must use the format X.Y.Z, for example 1.9.0.")
    return tuple(int(part) for part in str(version).split("."))


def app_info():
    paths = config_paths()
    return {
        "app_id": APP_NAME,
        "app_version": APP_VERSION,
        "is_frozen": bool(getattr(sys, "frozen", False)),
        "application_file": paths["application_file"],
        "config_file": paths["config_file"],
        "config_dir": paths["config_dir"],
    }


def check_install_writable(exe_path):
    try:
        exe_path = Path(exe_path)
        if not exe_path.is_file():
            return False, "The running EXE path could not be found."
        probe = exe_path.parent / f".catcb_write_test_{uuid.uuid4().hex}.tmp"
        probe.write_text("CatCB update permission test", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True, ""
    except Exception as exc:
        return False, ("CatCB cannot write to its current installation folder. Move the EXE to a folder "
                       "your Windows user owns (for example a folder under %LOCALAPPDATA%) and try again. "
                       f"Details: {exc}")


def inspect_update_package(data):
    filename = Path(str(data.get("filename", "CatCB_Update.zip"))).name
    if not filename.lower().endswith(".zip"):
        raise ValueError("Select a CatCB update .zip package, not a source-code ZIP or a plain EXE.")
    encoded = str(data.get("content_base64", ""))
    if not encoded:
        raise ValueError("The selected update file is empty.")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise ValueError("The selected file could not be decoded as an update package.") from exc
    if len(raw) > MAX_UPDATE_PACKAGE_BYTES:
        raise ValueError("Update package exceeds the 180 MB limit.")

    try:
        with zipfile.ZipFile(io.BytesIO(raw), "r") as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ValueError("Update ZIP contains duplicate file names.")
            required = {"CatCB.exe", "update_manifest.json"}
            if not required.issubset(set(names)):
                raise ValueError("This ZIP is not a CatCB update package. It must contain CatCB.exe and update_manifest.json at the root.")
            manifest_info = archive.getinfo("update_manifest.json")
            exe_info = archive.getinfo("CatCB.exe")
            if manifest_info.file_size > 128 * 1024:
                raise ValueError("Update manifest is unexpectedly large.")
            if exe_info.file_size <= 0 or exe_info.file_size > MAX_UPDATE_EXE_BYTES:
                raise ValueError("The CatCB.exe payload is empty or exceeds the 200 MB limit.")
            manifest = json.loads(archive.read(manifest_info).decode("utf-8-sig"))
            exe_bytes = archive.read(exe_info)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"The update ZIP could not be read: {exc}") from exc

    if manifest.get("app_id") != APP_NAME:
        raise ValueError("This update package is not for CatCB.")
    version = str(manifest.get("version", ""))
    if version_tuple(version) <= version_tuple(APP_VERSION):
        raise ValueError(f"The selected package is v{version}; this app is v{APP_VERSION}. Choose a newer version.")
    expected_hash = str(manifest.get("sha256", "")).strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
        raise ValueError("The update manifest does not contain a valid SHA-256 hash.")
    actual_hash = hashlib.sha256(exe_bytes).hexdigest()
    if actual_hash != expected_hash:
        raise ValueError("SHA-256 verification failed. The file may be damaged or does not match its manifest.")

    version_dir = UPDATE_STAGING_DIR / version
    version_dir.mkdir(parents=True, exist_ok=True)
    staged_exe = version_dir / "CatCB.new.exe"
    staged_exe.write_bytes(exe_bytes)
    token = uuid.uuid4().hex
    can_install = bool(getattr(sys, "frozen", False))
    install_reason = ""
    if can_install:
        writable, reason = check_install_writable(Path(sys.executable).resolve())
        can_install = writable
        if not writable:
            install_reason = reason
    else:
        install_reason = "This instance is running from Python/source, not a compiled CatCB.exe. Build and open CatCB.exe, then select this update ZIP there."
    pending = {
        "token": token,
        "version": version,
        "staged_exe": str(staged_exe),
        "sha256": actual_hash,
        "exe_size": len(exe_bytes),
        "release_notes": str(manifest.get("release_notes", ""))[:8000],
        "can_install": can_install,
        "install_reason": install_reason,
    }
    PENDING_UPDATES[token] = pending
    return {k: v for k, v in pending.items() if k != "staged_exe"} | {
        "current_version": APP_VERSION,
        "sha256_verified": True,
    }


def vb_quote(value):
    """Quote a path safely for a VBScript string literal."""
    return '"' + str(value).replace('"', '""') + '"'


def make_update_batch(pending):
    """Start a hidden, bounded VBScript updater; never open cmd.exe/tasklist/findstr."""
    if not getattr(sys, "frozen", False):
        raise RuntimeError("Install updates from the compiled CatCB.exe, not from the Python source launcher.")
    target = Path(sys.executable).resolve()
    writable, reason = check_install_writable(target)
    if not writable:
        raise PermissionError(reason)
    staged = Path(pending["staged_exe"]).resolve()
    if not staged.is_file():
        raise FileNotFoundError("The verified staged update executable is missing. Select the update ZIP again.")
    if hashlib.sha256(staged.read_bytes()).hexdigest() != pending["sha256"]:
        raise RuntimeError("The staged update hash no longer matches the verified package.")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = DATA_DIR / "Backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / f"CatCB_backup_v{APP_VERSION}_{stamp}.exe"
    log_file = DATA_DIR / "update.log"
    helper_path = UPDATE_STAGING_DIR / f"apply_{uuid.uuid4().hex}.vbs"
    helper_path.parent.mkdir(parents=True, exist_ok=True)
    pid = os.getpid()
    temp_exe = str(target) + ".update.tmp"

    # Direct VBScript file/process operations keep the installer completely separate
    # from Windows Terminal. WMI polling is bounded to 120 seconds and every action is logged.
    lines = [
        'Option Explicit',
        'Dim fso, shell, wmi, processes, waiting, oldExe, newExe, backupExe, tempExe, logFile, appPid',
        'Set fso = CreateObject("Scripting.FileSystemObject")',
        'Set shell = CreateObject("WScript.Shell")',
        f'oldExe = {vb_quote(target)}',
        f'newExe = {vb_quote(staged)}',
        f'backupExe = {vb_quote(backup)}',
        f'tempExe = {vb_quote(temp_exe)}',
        f'logFile = {vb_quote(log_file)}',
        f'appPid = {pid}',
        'Sub LogLine(message)',
        '  On Error Resume Next',
        '  Dim fs, outFile',
        '  Set fs = CreateObject("Scripting.FileSystemObject")',
        '  Set outFile = fs.OpenTextFile(logFile, 8, True)',
        '  outFile.WriteLine Now & " " & message',
        '  outFile.Close',
        '  On Error GoTo 0',
        'End Sub',
        'Sub FailUpdate(message, code)',
        '  LogLine "UPDATE FAILED: " & message',
        '  On Error Resume Next',
        '  If fso.FileExists(backupExe) And Not fso.FileExists(oldExe) Then fso.CopyFile backupExe, oldExe, True',
        '  shell.Popup "CatCB could not complete the update." & vbCrLf & message & vbCrLf & "Log: " & logFile, 8, "CatCB Update", 48',
        '  WScript.Quit code',
        'End Sub',
        'LogLine "Update helper started. Target=" & oldExe & "; staged=" & newExe & "; pid=" & appPid',
        'On Error Resume Next',
        r'Set wmi = GetObject("winmgmts:\\.\root\cimv2")',
        'If Err.Number <> 0 Then Call FailUpdate("Could not query Windows process status: " & Err.Description, 2)',
        'On Error GoTo 0',
        'waiting = 0',
        'Do',
        '  On Error Resume Next',
        '  Err.Clear',
        '  Set processes = wmi.ExecQuery("SELECT ProcessId FROM Win32_Process WHERE ProcessId = " & appPid)',
        '  If Err.Number <> 0 Then Call FailUpdate("Process check failed: " & Err.Description, 3)',
        '  On Error GoTo 0',
        '  If processes.Count = 0 Then Exit Do',
        '  WScript.Sleep 500',
        '  waiting = waiting + 1',
        '  If waiting >= 240 Then Call FailUpdate("CatCB did not close within 120 seconds. Close it and try again.", 4)',
        'Loop',
        'LogLine "CatCB process exited; preparing safe replacement."',
        'If Not fso.FileExists(newExe) Then Call FailUpdate("Verified staged executable was not found.", 5)',
        'On Error Resume Next',
        'Err.Clear',
        'fso.CopyFile oldExe, backupExe, True',
        'If Err.Number <> 0 Then Call FailUpdate("Could not create backup: " & Err.Description, 6)',
        'Err.Clear',
        'fso.CopyFile newExe, tempExe, True',
        'If Err.Number <> 0 Then Call FailUpdate("Could not stage replacement: " & Err.Description, 7)',
        'Err.Clear',
        'fso.DeleteFile oldExe, True',
        'If Err.Number <> 0 Then Call FailUpdate("Could not remove the old executable: " & Err.Description, 8)',
        'Err.Clear',
        'fso.MoveFile tempExe, oldExe',
        'If Err.Number <> 0 Then Call FailUpdate("Could not put the new executable in place: " & Err.Description, 9)',
        'Err.Clear',
        'fso.DeleteFile newExe, True',
        'LogLine "UPDATE SUCCESS. Restarting CatCB."',
        'On Error GoTo 0',
        'shell.Run Chr(34) & oldExe & Chr(34), 1, False',
        'WScript.Sleep 1000',
        'On Error Resume Next',
        'fso.DeleteFile WScript.ScriptFullName, True',
        'On Error GoTo 0',
    ]
    helper_path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")

    if os.name != "nt":
        raise OSError("The update installer can only replace a Windows EXE.")
    wscript = Path(os.environ.get("WINDIR", r"C:\Windows")) / "System32" / "wscript.exe"
    if not wscript.is_file():
        raise FileNotFoundError("Windows Script Host (wscript.exe) was not found. The old EXE was not changed.")
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    subprocess.Popen(
        [str(wscript), "//B", "//Nologo", str(helper_path)],
        cwd=str(helper_path.parent), creationflags=flags,
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        close_fds=True,
    )
    return {"target": str(target), "backup": str(backup), "log": str(log_file), "helper": str(helper_path)}


def close_catcb_app_window():
    if os.name != "nt":
        return
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        WM_CLOSE = 0x0010
        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def enum_proc(hwnd, _):
            if not user32.IsWindowVisible(hwnd):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, len(buf))
            title = buf.value.casefold()
            if "catcb" in title and "personal it snippet manager" in title:
                user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
                return False
            return True
        user32.EnumWindows(enum_proc, 0)
    except Exception as exc:
        log_error("Could not close CatCB app window for update: " + str(exc))


def request_update_shutdown():
    def stop_after_window_close():
        time.sleep(0.7)
        close_catcb_app_window()
        STOP_EVENT.set()
    threading.Thread(target=stop_after_window_close, daemon=True).start()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(RESOURCE_DIR), **kwargs)

    def log_message(self, fmt, *args):
        pass

    def touch_activity(self):
        global LAST_ACTIVITY
        LAST_ACTIVITY = time.monotonic()

    def send_json(self, status, payload):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        self.touch_activity()
        if self.path == "/api/ping":
            self.send_json(200, {"alive": True})
            return
        if self.path == "/api/app-info":
            self.send_json(200, app_info())
            return
        if self.path == "/api/state":
            try:
                DATA_DIR.mkdir(parents=True, exist_ok=True)
                data = json.loads(STATE_FILE.read_text(encoding="utf-8")) if STATE_FILE.exists() else {}
                self.send_json(200, data)
            except Exception as exc:
                log_error(traceback.format_exc())
                self.send_json(500, {"error": str(exc)})
            return
        if self.path == "/api/paths":
            self.send_json(200, config_paths())
            return
        if self.path == "/api/outlook/accounts":
            try:
                self.send_json(200, {"accounts": outlook_accounts()})
            except Exception as exc:
                self.send_json(503, {"error": friendly_outlook_error(exc)})
            return
        if self.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        self.touch_activity()
        if self.path not in ("/api/state", "/api/email/create", "/api/open-path", "/api/update/inspect", "/api/update/apply", "/api/update/shutdown"):
            self.send_json(404, {"error": "Not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > MAX_REQUEST_BYTES:
                self.send_json(413, {"error": "Request is too large for the local CatCB service."})
                return
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception as exc:
            self.send_json(400, {"error": f"Invalid request: {exc}"})
            return

        if self.path == "/api/state":
            try:
                DATA_DIR.mkdir(parents=True, exist_ok=True)
                tmp = STATE_FILE.with_suffix(".tmp")
                tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                tmp.replace(STATE_FILE)
                self.send_json(200, {"saved": True})
            except Exception as exc:
                log_error(traceback.format_exc())
                self.send_json(500, {"error": str(exc)})
            return

        if self.path == "/api/open-path":
            try:
                opened = open_local_path(str(data.get("which", "")))
                self.send_json(200, {"opened": True, "path": opened})
            except Exception as exc:
                log_error(traceback.format_exc())
                self.send_json(500, {"error": str(exc)})
            return

        if self.path == "/api/update/inspect":
            try:
                result = inspect_update_package(data)
                self.send_json(200, result)
            except Exception as exc:
                log_error("Update package inspection failed: " + traceback.format_exc())
                self.send_json(400, {"error": str(exc)})
            return

        if self.path == "/api/update/apply":
            try:
                token = str(data.get("token", ""))
                pending = PENDING_UPDATES.get(token)
                if not pending:
                    raise ValueError("This update check has expired. Select the update ZIP again.")
                if not pending.get("can_install"):
                    raise PermissionError(pending.get("install_reason") or "This instance cannot install updates.")
                details = make_update_batch(pending)
                self.send_json(200, {"prepared": True, **details})
            except Exception as exc:
                log_error("Update preparation failed: " + traceback.format_exc())
                self.send_json(400, {"error": str(exc)})
            return

        if self.path == "/api/update/shutdown":
            try:
                token = str(data.get("token", ""))
                if token not in PENDING_UPDATES:
                    raise ValueError("Update token not found. Please select the ZIP again.")
                request_update_shutdown()
                self.send_json(200, {"shutting_down": True})
            except Exception as exc:
                self.send_json(400, {"error": str(exc)})
            return

        if self.path == "/api/email/create":
            try:
                result = create_outlook_draft(data)
                self.send_json(200, result)
            except Exception as exc:
                log_error(traceback.format_exc())
                self.send_json(503, {"error": friendly_outlook_error(exc)})
            return


def friendly_outlook_error(exc):
    return (
        "Outlook integration failed. Make sure Outlook Classic is installed and configured, "
        "and pywin32 is available in CatCB's Python environment. If this is an EXE build, "
        "check %APPDATA%\\CatCB\\catcb.log. CatCB never sends messages automatically. "
        f"Details: {exc}"
    )


def outlook_accounts():
    import pythoncom
    import win32com.client
    pythoncom.CoInitialize()
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        accounts = []
        for account in namespace.Accounts:
            try:
                name = str(account.DisplayName or "")
            except Exception:
                name = ""
            try:
                email = str(account.SmtpAddress or "")
            except Exception:
                email = ""
            if name or email:
                accounts.append({"name": name, "email": email})
        return accounts
    finally:
        pythoncom.CoUninitialize()


def create_outlook_draft(data):
    import pythoncom
    import win32com.client

    to = str(data.get("to", "")).strip()
    cc = str(data.get("cc", "")).strip()
    bcc = str(data.get("bcc", "")).strip()
    from_address = str(data.get("from_address", "")).strip()
    subject = str(data.get("subject", "")).strip() or "Message from CatCB"
    body = str(data.get("body", ""))
    save_msg = bool(data.get("save_msg", False))
    filename = str(data.get("filename", "")).strip() or subject
    attachments = data.get("attachments", [])
    if not isinstance(attachments, list):
        raise ValueError("Attachments must be a list.")

    decoded_attachments = []
    total_bytes = 0
    for item in attachments:
        if not isinstance(item, dict):
            continue
        name = safe_filename(item.get("name", "report"), "report")
        encoded = str(item.get("content_base64", ""))
        if not encoded:
            continue
        try:
            raw = base64.b64decode(encoded, validate=True)
        except Exception:
            raise ValueError(f"Attachment {name} is not valid base64 data.")
        total_bytes += len(raw)
        if len(raw) > MAX_ATTACHMENT_BYTES:
            raise ValueError(f"Attachment {name} is larger than 24 MB.")
        if total_bytes > MAX_ATTACHMENT_BYTES:
            raise ValueError("The combined attachment size exceeds 24 MB.")
        decoded_attachments.append((name, raw))

    temp_paths = []
    temp_batch_dir = TEMP_ATTACHMENT_DIR / uuid.uuid4().hex
    pythoncom.CoInitialize()
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        mail = outlook.CreateItem(OL_MAIL_ITEM)
        mail.To = to
        mail.CC = cc
        mail.BCC = bcc
        mail.Subject = subject
        mail.Body = body

        if from_address:
            matched = None
            try:
                for account in namespace.Accounts:
                    try:
                        account_email = str(account.SmtpAddress or "").strip().lower()
                        account_name = str(account.DisplayName or "").strip().lower()
                    except Exception:
                        account_email, account_name = "", ""
                    if from_address.lower() in (account_email, account_name):
                        matched = account
                        break
            except Exception:
                matched = None
            if matched is not None:
                try:
                    mail.SendUsingAccount = matched
                except Exception:
                    mail.SentOnBehalfOfName = from_address
            else:
                # Outlook/Exchange validates whether the signed-in user may send on behalf of this mailbox.
                mail.SentOnBehalfOfName = from_address

        if decoded_attachments:
            temp_batch_dir.mkdir(parents=True, exist_ok=True)
            for name, raw in decoded_attachments:
                temp_path = temp_batch_dir / name
                temp_path.write_bytes(raw)
                temp_paths.append(temp_path)
                mail.Attachments.Add(str(temp_path))

        saved_path = None
        if save_msg:
            DRAFT_DIR.mkdir(parents=True, exist_ok=True)
            safe = safe_filename(filename, "CatCB_Draft")
            if not safe.lower().endswith(".msg"):
                safe += ".msg"
            destination = DRAFT_DIR / safe
            if destination.exists():
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                destination = DRAFT_DIR / f"{destination.stem}_{stamp}.msg"
            mail.SaveAs(str(destination), OL_MSG)
            saved_path = str(destination)

        # Display only: no .Send() call is made anywhere.
        mail.Display(False)
        return {"opened": True, "path": saved_path, "saved_msg": saved_path,
                "attachment_count": len(decoded_attachments)}
    finally:
        # Attachments have been imported into the Outlook item; temporary copies can be removed.
        for temp_path in temp_paths:
            try:
                temp_path.unlink(missing_ok=True)
            except Exception:
                pass
        try:
            if temp_batch_dir.exists():
                shutil.rmtree(temp_batch_dir, ignore_errors=True)
        except Exception:
            pass
        pythoncom.CoUninitialize()


def find_app_browser():
    env = os.environ
    roots = [
        Path(env.get("PROGRAMFILES", r"C:\Program Files")) / "Google/Chrome/Application/chrome.exe",
        Path(env.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")) / "Google/Chrome/Application/chrome.exe",
        Path(env.get("LOCALAPPDATA", str(Path.home()))) / "Google/Chrome/Application/chrome.exe",
        Path(env.get("PROGRAMFILES", r"C:\Program Files")) / "Microsoft/Edge/Application/msedge.exe",
        Path(env.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")) / "Microsoft/Edge/Application/msedge.exe",
        Path(env.get("LOCALAPPDATA", str(Path.home()))) / "Microsoft/Edge/Application/msedge.exe",
    ]
    for item in roots:
        if item.exists():
            return str(item)
    return None


def force_maximize_catcb_window(timeout_seconds=12):
    """Wait for the browser app window and maximize it using the Windows window manager."""
    if os.name != "nt":
        return False
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        SW_MAXIMIZE = 3
        deadline = time.monotonic() + timeout_seconds
        found = {"hwnd": None}

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def enum_windows_proc(hwnd, _lparam):
            if not user32.IsWindowVisible(hwnd):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, len(buffer))
            title = buffer.value.casefold()
            if "catcb" in title:
                found["hwnd"] = hwnd
                return False
            return True

        while time.monotonic() < deadline and found["hwnd"] is None:
            user32.EnumWindows(enum_windows_proc, 0)
            if found["hwnd"] is None:
                time.sleep(0.2)

        hwnd = found["hwnd"]
        if hwnd:
            user32.ShowWindow(hwnd, SW_MAXIMIZE)
            try:
                user32.SetForegroundWindow(hwnd)
            except Exception:
                pass
            return True
    except Exception as exc:
        log_error("Could not force-maximize CatCB window: " + str(exc))
    return False


def force_fullscreen_catcb_window(timeout_seconds=15):
    """Force the CatCB browser window to cover the primary monitor without frame/taskbar."""
    if os.name != "nt":
        return False
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        SW_SHOW = 5
        SWP_FRAMECHANGED = 0x0020
        SWP_SHOWWINDOW = 0x0040
        SWP_NOOWNERZORDER = 0x0200
        HWND_TOPMOST = -1
        GWL_STYLE = -16
        GWL_EXSTYLE = -20
        WS_CAPTION = 0x00C00000
        WS_THICKFRAME = 0x00040000
        WS_MINIMIZEBOX = 0x00020000
        WS_MAXIMIZEBOX = 0x00010000
        WS_SYSMENU = 0x00080000
        WS_POPUP = 0x80000000
        WS_EX_APPWINDOW = 0x00040000
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        deadline = time.monotonic() + timeout_seconds
        found = {"hwnd": None}

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def enum_windows_proc(hwnd, _lparam):
            if not user32.IsWindowVisible(hwnd):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, len(buffer))
            if "catcb" in buffer.value.casefold():
                found["hwnd"] = hwnd
                return False
            return True

        while time.monotonic() < deadline and found["hwnd"] is None:
            user32.EnumWindows(enum_windows_proc, 0)
            if found["hwnd"] is None:
                time.sleep(0.2)

        hwnd = found["hwnd"]
        if not hwnd:
            return False

        # Set pointer-safe signatures for 32/64-bit Windows.
        get_long = user32.GetWindowLongPtrW
        set_long = user32.SetWindowLongPtrW
        get_long.argtypes = [wintypes.HWND, ctypes.c_int]
        get_long.restype = ctypes.c_ssize_t
        set_long.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]
        set_long.restype = ctypes.c_ssize_t

        style = get_long(hwnd, GWL_STYLE)
        style = style & ~(WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU)
        style |= WS_POPUP
        set_long(hwnd, GWL_STYLE, style)

        ex_style = get_long(hwnd, GWL_EXSTYLE)
        ex_style |= WS_EX_APPWINDOW
        set_long(hwnd, GWL_EXSTYLE, ex_style)

        user32.ShowWindow(hwnd, SW_SHOW)
        user32.SetWindowPos(
            hwnd, HWND_TOPMOST, 0, 0, width, height,
            SWP_FRAMECHANGED | SWP_SHOWWINDOW | SWP_NOOWNERZORDER
        )
        try:
            user32.SetForegroundWindow(hwnd)
        except Exception:
            pass
        return True
    except Exception as exc:
        log_error("Could not force fullscreen CatCB window: " + str(exc))
        return False


def set_windows_app_identity():
    """Give Windows a stable CatCB AppUserModelID for the taskbar and pinned shortcut."""
    if os.name != "nt":
        return
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Bejlint.CatCB")
    except Exception as exc:
        log_error("Could not set Windows AppUserModelID: " + str(exc))


def main():
    required = ["index.html", "CatCB_Space_v14.jpg", "CatCB_Mascot_v14.png", "CatCB_Mascot_v14.ico"]
    missing = [name for name in required if not (RESOURCE_DIR / name).exists()]
    if missing:
        raise FileNotFoundError("CatCB resource files missing: " + ", ".join(missing))
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    set_windows_app_identity()
    webview_profile = DATA_DIR / "WebView2UserData"
    webview_profile.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("WEBVIEW2_USER_DATA_FOLDER", str(webview_profile))

    try:
        server = ThreadingHTTPServer(("127.0.0.1", PREFERRED_PORT), Handler)
    except OSError:
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    threading.Thread(target=server.serve_forever, daemon=True).start()
    time.sleep(0.2)

    try:
        import webview
        # pywebview creates a real CatCB window hosted by this EXE; the taskbar icon/name
        # therefore belong to CatCB, not Chrome. WebView2 Runtime must be available on Windows.
        webview.create_window(
            "CatCB — Personal IT Snippet Manager",
            url=url,
            width=1500,
            height=950,
            min_size=(760, 580),
            maximized=True,
            resizable=True,
            background_color="#070c14",
            text_select=True,
        )
        webview.start(gui="edgechromium", debug=False)
    except Exception as exc:
        log_error("Native WebView startup failed: " + traceback.format_exc())
        show_error(
            "CatCB could not open its native window",
            "CatCB now uses its own Windows window and taskbar icon. This requires the Microsoft Edge WebView2 Runtime.\n\n"
            "Ask IT to install/enable the WebView2 Runtime if it is missing. CatCB has not opened Chrome as a fallback, so the taskbar shortcut will not unexpectedly launch a normal browser.\n\n"
            f"Details: {exc}",
        )
    finally:
        STOP_EVENT.set()
        try:
            server.shutdown()
            server.server_close()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        show_error("CatCB startup error", f"CatCB could not start.\n\n{exc}\n\nDetails were written to %APPDATA%\\CatCB\\catcb.log.")
