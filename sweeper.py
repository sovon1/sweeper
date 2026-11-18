#!/usr/bin/env python3
"""
🧹 SWEEPER — The intelligent, zero-dependency, aesthetic folder organizer.
Organizes messy folders (like Downloads or Desktop) into clean, intuitive categories
and gently prunes redundant duplicate downloads and dead installers to your Recycle Bin/Trash.
Includes instant 1-click Undo.

Author: Sovon & Community
License: MIT
"""

import sys
import os
import re
import json
import time
import shutil
import platform
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Any

__version__ = "1.0.0"

# ==============================================================================
# Terminal Styling & Colors (Cross-Platform TrueColor / ANSI)
# ==============================================================================

def enable_windows_ansi():
    """Enable virtual terminal processing and UTF-8 encoding on Windows."""
    try:
        if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    if platform.system() == "Windows":
        try:
            import ctypes
            from ctypes import wintypes
            kernel32 = ctypes.windll.kernel32
            STD_OUTPUT_HANDLE = -11
            handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
            mode = wintypes.DWORD()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass

enable_windows_ansi()

class Style:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    ITALIC  = "\033[3m"
    UNDER   = "\033[4m"

    # Aesthetic Pastel Palette
    CYAN    = "\033[38;2;56;189;248m"    # Pastel Sky Blue
    BLUE    = "\033[38;2;96;165;250m"    # Soft Blue
    PINK    = "\033[38;2;244;114;182m"   # Rose Pink
    GREEN   = "\033[38;2;52;211;153m"    # Mint / Emerald
    YELLOW  = "\033[38;2;251;191;36m"    # Warm Amber
    PURPLE  = "\033[38;2;167;139;250m"   # Lavender
    GRAY    = "\033[38;2;156;163;175m"   # Slate Gray
    WHITE   = "\033[38;2;243;244;246m"   # Crisp White
    BG_DARK = "\033[48;2;30;41;59m"

def banner():
    art = f"""
{Style.CYAN}{Style.BOLD}   ____                                   
  / ___|_      _____  ___ _ __   ___ _ __ 
  \\___ \\ \\ /\\ / / _ \\/ _ \\ '_ \\ / _ \\ '__|
   ___) \\ V  V /  __/  __/ |_) |  __/ |   
  |____/ \\_/\\_/ \\___|\\___| .__/ \\___|_|   
                         |_|   {Style.PINK}v{__version__} ✨{Style.RESET}
  {Style.GRAY}The intelligent, zero-dependency folder organizer{Style.RESET}
"""
    return art

# ==============================================================================
# Category Mapping & Rules
# ==============================================================================

DEFAULT_CATEGORIES = {
    "Documents": {
        "icon": "📄",
        "exts": {
            ".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls",
            ".csv", ".txt", ".epub", ".mobi", ".rtf", ".odt", ".ics",
            ".tex", ".pages", ".numbers", ".key"
        },
        "dir_keywords": ["exportblock", "research", "paper", "lecture", "notes", "ch8", "study"]
    },
    "Images": {
        "icon": "🖼️ ",
        "exts": {
            ".png", ".jpg", ".jpeg", ".webp", ".gif", ".heic",
            ".svg", ".ico", ".bmp", ".tiff", ".psd", ".ai", ".raw"
        },
        "dir_keywords": ["logo", "images", "photos", "wallpapers", "screenshots"]
    },
    "Media": {
        "icon": "🎬",
        "exts": {
            ".mp4", ".mkv", ".mov", ".webm", ".avi", ".wmv",
            ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".opus", ".aac"
        },
        "dir_keywords": ["youtube", "video", "music", "audio", "podcast", "screen-recordings"]
    },
    "Archives": {
        "icon": "📦",
        "exts": {
            ".zip", ".rar", ".7z", ".tar", ".gz", ".tgz", ".iso", ".bz2", ".xz", ".7zip"
        },
        "dir_keywords": []
    },
    "Code & Projects": {
        "icon": "💻",
        "exts": {
            ".html", ".css", ".js", ".jsx", ".ts", ".tsx", ".json",
            ".py", ".sql", ".md", ".yaml", ".yml", ".sh", ".bash",
            ".patch", ".jar", ".pem", ".b64", ".c", ".cpp", ".h",
            ".java", ".rs", ".go", ".php", ".rb", ".toml", ".env"
        },
        "dir_keywords": ["workspace", "notes-", "curriculum", "website", "project", "repo"]
    },
    "Programs & Apps": {
        "icon": "⚡",
        "exts": {
            ".exe", ".msi", ".apk", ".dmg", ".appx", ".msix", ".pkg", ".deb", ".rpm"
        },
        "dir_keywords": ["setup", "install", "kangal", "pro-edition"]
    }
}

PROTECTED_NAMES = {
    "desktop.ini", ".ds_store", "thumbs.db", ".git", ".gitignore",
    ".sweeper_history.json", ".sweeper.json", "sweeper.py", "run.ps1", "run.sh"
}

PROTECTED_EXTS = {".lnk", ".url"}

# ==============================================================================
# Configuration & Custom Rules (.sweeper.json)
# ==============================================================================

def load_config(target_dir: Path) -> Dict[str, Any]:
    """Load optional user configuration from target folder or home directory."""
    local_cfg = target_dir / ".sweeper.json"
    global_cfg = Path.home() / ".sweeper.json"
    cfg_path = local_cfg if local_cfg.exists() else (global_cfg if global_cfg.exists() else None)
    if not cfg_path:
        return {}
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to parse {cfg_path}: {e}")
        return {}

def init_config(target_dir: Path) -> Path:
    """Generate a clean, documented .sweeper.json configuration template."""
    cfg_path = target_dir / ".sweeper.json"
    sample = {
        "$schema": "https://raw.githubusercontent.com/sovon1/sweeper/main/schema.json",
        "by_date": False,
        "ignore": ["node_modules", "vendor", "*.tmp"],
        "custom_categories": {
            "Books & Comics": {
                "icon": "📚",
                "exts": [".epub", ".mobi", ".azw3", ".cbr", ".cbz"],
                "dir_keywords": ["book", "comic", "manga"]
            },
            "Design & 3D": {
                "icon": "🎨",
                "exts": [".blend", ".obj", ".stl", ".fbx", ".fig", ".sketch"],
                "dir_keywords": ["model", "3d", "render", "design"]
            }
        }
    }
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(sample, f, indent=2)
    return cfg_path

# ==============================================================================
# Windows Context Menu Integration (Right-Click "Sweep with Sweeper")
# ==============================================================================

def manage_context_menu(install: bool = True) -> Tuple[bool, str]:
    """Add or remove 'Sweep with Sweeper' in Windows File Explorer right-click menu."""
    if platform.system() != "Windows":
        return False, "Context menu integration is only available on Windows."
    try:
        import winreg
        script_path = str(Path(__file__).resolve())
        python_exe = sys.executable
        # Command lines for clicking a directory vs clicking directory background
        cmd_dir = f'"{python_exe}" "{script_path}" "%1"'
        cmd_bg = f'"{python_exe}" "{script_path}" "%V"'

        key_specs = [
            (winreg.HKEY_CURRENT_USER, r"Software\Classes\Directory\shell\Sweeper", cmd_dir),
            (winreg.HKEY_CURRENT_USER, r"Software\Classes\Directory\Background\shell\Sweeper", cmd_bg)
        ]

        if install:
            for root_h, sub_path, cmd in key_specs:
                with winreg.CreateKey(root_h, sub_path) as key:
                    winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "🧹 Sweep with Sweeper")
                    winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, "shell32.dll,31")
                with winreg.CreateKey(root_h, sub_path + r"\command") as key:
                    winreg.SetValueEx(key, "", 0, winreg.REG_SZ, cmd)
            return True, "Successfully added '🧹 Sweep with Sweeper' to your right-click context menu!"
        else:
            for root_h, sub_path, _ in key_specs:
                try:
                    winreg.DeleteKey(root_h, sub_path + r"\command")
                    winreg.DeleteKey(root_h, sub_path)
                except FileNotFoundError:
                    pass
            return True, "Removed Sweeper from the right-click context menu."
    except Exception as e:
        return False, f"Failed to modify context menu registry: {e}"

# ==============================================================================
# OS Native Trash / Recycle Bin (Cross-Platform)
# ==============================================================================

def send_to_trash(path: Path) -> bool:
    """Send file or folder to OS Recycle Bin (Windows) or Trash (macOS/Linux)."""
    system = platform.system()
    
    if system == "Windows":
        try:
            import ctypes
            from ctypes import wintypes
            class SHFILEOPSTRUCT(ctypes.Structure):
                _fields_ = [
                    ("hwnd", wintypes.HWND),
                    ("wFunc", wintypes.UINT),
                    ("pFrom", wintypes.LPCWSTR),
                    ("pTo", wintypes.LPCWSTR),
                    ("fFlags", wintypes.WORD),
                    ("fAnyOperationsAborted", wintypes.BOOL),
                    ("hNameMappings", wintypes.LPVOID),
                    ("lpszProgressTitle", wintypes.LPCWSTR),
                ]

            FO_DELETE = 3
            FOF_ALLOWUNDO = 0x0040
            FOF_NOCONFIRMATION = 0x0010
            FOF_SILENT = 0x0004
            FOF_NOERRORUI = 0x0400

            path_str = str(path.resolve()) + "\0\0"
            fileop = SHFILEOPSTRUCT()
            fileop.hwnd = None
            fileop.wFunc = FO_DELETE
            fileop.pFrom = path_str
            fileop.pTo = None
            fileop.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT | FOF_NOERRORUI
            fileop.fAnyOperationsAborted = False

            ret = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(fileop))
            return ret == 0 and not fileop.fAnyOperationsAborted
        except Exception:
            return False

    elif system == "Darwin":  # macOS
        try:
            import subprocess
            cmd = f'tell application "Finder" to delete POSIX file "{str(path.resolve())}"'
            ret = subprocess.run(["osascript", "-e", cmd], capture_output=True)
            return ret.returncode == 0
        except Exception:
            return False

    else:  # Linux
        try:
            import subprocess
            ret = subprocess.run(["gio", "trash", str(path)], capture_output=True)
            if ret.returncode == 0:
                return True
        except Exception:
            pass
        # Fallback XDG trash
        try:
            home = Path.home()
            trash_files = home / ".local" / "share" / "Trash" / "files"
            trash_files.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(trash_files / path.name))
            return True
        except Exception:
            return False

# ==============================================================================
# Core Scanning & Analysis Engine
# ==============================================================================

class Sweeper:
    def __init__(self, target_dir: Path):
        self.set_target(target_dir)

    def set_target(self, target_dir: Path):
        """Set or change the target folder and reset cached stats."""
        self.target_dir = target_dir.resolve()
        self.history_file = self.target_dir / ".sweeper_history.json"
        
        # Load user configuration
        self.config = load_config(self.target_dir)
        self.categories = dict(DEFAULT_CATEGORIES)
        
        # Merge custom categories from .sweeper.json
        custom_cats = self.config.get("custom_categories", {})
        for cname, cdata in custom_cats.items():
            self.categories[cname] = {
                "icon": cdata.get("icon", "📁"),
                "exts": set(ext.lower() for ext in cdata.get("exts", [])),
                "dir_keywords": [kw.lower() for kw in cdata.get("dir_keywords", [])]
            }
            
        self.user_ignore = set(x.lower() for x in self.config.get("ignore", []))
        self.category_names = set(self.categories.keys()) | {"Other"}
        self._size_cache = {}

    def is_protected(self, path: Path) -> bool:
        """Check if an item is protected from moves or cleaning."""
        name = path.name.lower()
        if name in PROTECTED_NAMES:
            return True
        if path.suffix.lower() in PROTECTED_EXTS:
            return True
        if name in {c.lower() for c in self.category_names}:
            return True
        if name.startswith(".sweeper"):
            return True
        for ign in self.user_ignore:
            if ign.startswith("*") and name.endswith(ign[1:]):
                return True
            if ign == name:
                return True
        return False

    def get_size(self, path: Path) -> int:
        """Fast size calculation with caching (avoids freezing on deep project trees)."""
        path_str = str(path)
        if path_str in self._size_cache:
            return self._size_cache[path_str]

        try:
            if path.is_file():
                sz = path.stat().st_size
                self._size_cache[path_str] = sz
                return sz

            # Fast non-blocking directory size check
            total = 0
            count = 0
            for entry in os.scandir(path):
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size
                    count += 1
                    if count > 250:  # Fast preview without freezing UI
                        break
                except (PermissionError, FileNotFoundError):
                    pass
            self._size_cache[path_str] = total
            return total
        except (PermissionError, FileNotFoundError):
            return 0

    def classify(self, path: Path) -> str:
        """Classify a file or folder into an intuitive category."""
        name_lower = path.name.lower()

        if path.is_dir():
            for cat, data in self.categories.items():
                if any(kw in name_lower for kw in data["dir_keywords"]):
                    return cat
            return "Other"

        ext = path.suffix.lower()
        for cat, data in self.categories.items():
            if ext in data["exts"]:
                return cat

        return "Other"

    def scan_clutter(self) -> Tuple[List[Dict[str, Any]], int]:
        """
        Identify high-confidence junk, dead installers, and redundant duplicates:
        1. Repeated numbered downloads: e.g. Designer (1..100).png, keeping 1 latest copy.
        2. Software installers (.exe, .msi, .apk) that can be re-downloaded.
        3. Redundant archives where an extracted folder with the same name already exists.
        4. Webpage companion resource folders ending in `_files`.
        5. Empty folders and .torrent metadata files.
        """
        clutter_items = []
        total_clutter_bytes = 0

        # Normalization for repeat downloads
        def normalize_name(name: str):
            stem = Path(name).stem
            ext = Path(name).suffix.lower()
            prev = ""
            curr = stem
            while prev != curr:
                prev = curr
                curr = re.sub(r"\s*\(\d+\)$", "", curr)
                curr = re.sub(r"\s*-\s*Copy(\s*\(\d+\))?$", "", curr, flags=re.I)
            return curr.strip().lower(), ext

        clusters = defaultdict(list)
        dup_regex = re.compile(r"(\s*\(\d+\)|\s*-\s*Copy(\s*\(\d+\))?)$", re.I)

        for item in self.target_dir.iterdir():
            if self.is_protected(item):
                continue

            # A. Empty Folders
            if item.is_dir():
                try:
                    if not any(item.iterdir()):
                        clutter_items.append({
                            "path": item,
                            "type": "Empty Folder",
                            "size": 0,
                            "reason": "Empty directory"
                        })
                        continue
                except Exception:
                    pass

                # B. Web Page companion folders (_files)
                if item.name.endswith("_files"):
                    sz = self.get_size(item)
                    clutter_items.append({
                        "path": item,
                        "type": "Web Resource Dump",
                        "size": sz,
                        "reason": "Browser-saved webpage dump folder"
                    })
                    total_clutter_bytes += sz
                    continue

            # C. Torrent files
            if item.is_file() and item.suffix.lower() == ".torrent":
                sz = item.stat().st_size
                clutter_items.append({
                    "path": item,
                    "type": "Torrent Metadata",
                    "size": sz,
                    "reason": "Torrent file"
                })
                total_clutter_bytes += sz
                continue

            # D. Software Installers (.exe, .msi, .apk)
            if item.is_file() and item.suffix.lower() in {".exe", ".msi", ".apk"}:
                sz = item.stat().st_size
                clutter_items.append({
                    "path": item,
                    "type": "Software Installer",
                    "size": sz,
                    "reason": "One-time setup / installer file"
                })
                total_clutter_bytes += sz
                continue

            # E. Redundant Archives (folder with exact same stem exists)
            if item.is_file() and item.suffix.lower() in {".zip", ".rar", ".7z", ".tar"}:
                folder = self.target_dir / item.stem
                if folder.exists() and folder.is_dir():
                    sz = item.stat().st_size
                    clutter_items.append({
                        "path": item,
                        "type": "Redundant Archive",
                        "size": sz,
                        "reason": f"Extracted folder '{item.stem}/' already exists"
                    })
                    total_clutter_bytes += sz
                    continue

            # Group candidates for repeat download clustering
            if item.is_file():
                base, ext = normalize_name(item.name)
                clusters[(base, ext)].append(item)

        # F. Process Duplicate Clusters
        for (base, ext), files in clusters.items():
            if len(files) > 1:
                unmarked = [f for f in files if not dup_regex.search(f.stem)]
                marked = [f for f in files if dup_regex.search(f.stem)]

                # If we have an original, keep it and recycle marked
                if unmarked and marked:
                    for m in marked:
                        sz = m.stat().st_size
                        clutter_items.append({
                            "path": m,
                            "type": "Duplicate Download",
                            "size": sz,
                            "reason": f"Duplicate copy (original '{unmarked[0].name}' kept)"
                        })
                        total_clutter_bytes += sz
                elif len(marked) > 1:
                    # All have numbers (e.g. Designer (1..100)): keep newest, recycle older
                    sorted_marked = sorted(marked, key=lambda x: x.stat().st_mtime, reverse=True)
                    for m in sorted_marked[1:]:
                        sz = m.stat().st_size
                        clutter_items.append({
                            "path": m,
                            "type": "Duplicate Download",
                            "size": sz,
                            "reason": f"Older copy (newest '{sorted_marked[0].name}' kept)"
                        })
                        total_clutter_bytes += sz

        return clutter_items, total_clutter_bytes

    def plan_organization(self, exclude_paths: Optional[set] = None) -> Dict[str, List[Path]]:
        """Plan moves for files and directories into categories."""
        if exclude_paths is None:
            exclude_paths = set()

        categorized = defaultdict(list)
        for item in self.target_dir.iterdir():
            if self.is_protected(item) or item in exclude_paths:
                continue
            cat = self.classify(item)
            categorized[cat].append(item)

        return categorized

    def get_safe_destination(self, dest_dir: Path, item_name: str) -> Path:
        """Guarantee collision-free target by appending _1, _2 if needed."""
        dest_path = dest_dir / item_name
        if not dest_path.exists():
            return dest_path

        stem = Path(item_name).stem
        suffix = Path(item_name).suffix
        counter = 1
        while True:
            candidate = dest_dir / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def execute(self, clean_clutter: bool = True, organize: bool = True, dry_run: bool = False, by_date: Optional[bool] = None, progress_callback: Optional[Any] = None) -> Dict[str, Any]:
        """Execute the sweep operation with full transaction logging."""
        if by_date is None:
            by_date = self.config.get("by_date", False)

        clutter_items = []
        clutter_bytes = 0
        clutter_paths = set()

        if clean_clutter:
            clutter_items, clutter_bytes = self.scan_clutter()
            clutter_paths = {c["path"] for c in clutter_items}

        org_plan = {}
        if organize:
            org_plan = self.plan_organization(exclude_paths=clutter_paths)

        if dry_run:
            return {
                "dry_run": True,
                "clutter_count": len(clutter_items),
                "clutter_bytes": clutter_bytes,
                "organized_counts": {k: len(v) for k, v in org_plan.items()}
            }

        total_ops = (len(clutter_items) if clean_clutter else 0) + (sum(len(v) for v in org_plan.values()) if organize else 0)
        current_op = 0

        transaction = {
            "timestamp": time.time(),
            "time_str": time.strftime("%Y-%m-%d %H:%M:%S"),
            "target_dir": str(self.target_dir),
            "operations": []
        }

        # 1. Clean Clutter (Recycle Bin / Trash)
        recycled_count = 0
        recycled_bytes = 0
        for c in clutter_items:
            path = c["path"]
            sz = c["size"]
            current_op += 1
            if progress_callback:
                progress_callback(current_op, total_ops, f"Recycling {path.name}")
            try:
                if send_to_trash(path):
                    recycled_count += 1
                    recycled_bytes += sz
                    transaction["operations"].append({
                        "type": "trash",
                        "path": str(path),
                        "size": sz
                    })
            except Exception:
                pass

        # 2. Organize Remaining Items
        moved_count = 0
        moved_bytes = 0
        for cat, items in org_plan.items():
            cat_dir = self.target_dir / cat
            cat_dir.mkdir(exist_ok=True)

            for item in items:
                current_op += 1
                if progress_callback:
                    progress_callback(current_op, total_ops, f"Sorting {item.name}")
                try:
                    target_parent = cat_dir
                    if by_date and item.is_file():
                        try:
                            ym = time.strftime("%Y-%m", time.localtime(item.stat().st_mtime))
                            target_parent = cat_dir / ym
                            target_parent.mkdir(parents=True, exist_ok=True)
                        except Exception:
                            pass

                    final_dest = self.get_safe_destination(target_parent, item.name)
                    sz = self.get_size(item)
                    shutil.move(str(item), str(final_dest))
                    moved_count += 1
                    moved_bytes += sz
                    transaction["operations"].append({
                        "type": "move",
                        "from": str(item),
                        "to": str(final_dest),
                        "size": sz
                    })
                except Exception:
                    pass

        # Save transaction history for undo
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []

        history.append(transaction)
        # Keep last 10 transactions
        history = history[-10:]

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

        return {
            "dry_run": False,
            "recycled_count": recycled_count,
            "recycled_bytes": recycled_bytes,
            "moved_count": moved_count,
            "moved_bytes": moved_bytes,
            "categories": {k: len(v) for k, v in org_plan.items()}
        }

    def undo(self) -> Tuple[int, str]:
        """Undo the last sweep transaction, restoring every file to its exact spot."""
        if not self.history_file.exists():
            return 0, "No sweeper transaction history found in this directory."

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception as e:
            return 0, f"Error reading history: {e}"

        if not history:
            return 0, "No transactions available to undo."

        last_tx = history.pop()
        operations = last_tx.get("operations", [])
        restored_count = 0

        # Reverse operations (moves in reverse)
        for op in reversed(operations):
            if op["type"] == "move":
                src = Path(op["to"])
                dest = Path(op["from"])
                if src.exists():
                    try:
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(src), str(dest))
                        restored_count += 1
                    except Exception:
                        pass

        # Clean empty category folders if left behind
        for cat in self.category_names:
            cat_dir = self.target_dir / cat
            if cat_dir.exists() and cat_dir.is_dir():
                try:
                    if not any(cat_dir.iterdir()):
                        cat_dir.rmdir()
                except Exception:
                    pass

        # Update history file
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

        trash_note = ""
        trash_ops = [op for op in operations if op["type"] == "trash"]
        if trash_ops:
            trash_note = f" (Note: {len(trash_ops)} items in Recycle Bin can be restored directly from your OS Recycle Bin)."

        return restored_count, f"Successfully restored {restored_count} moved items to their original locations.{trash_note}"

# ==============================================================================
# Interactive Terminal UI
# ==============================================================================

def format_bytes(b: int) -> str:
    if b < 1024:
        return f"{b} B"
    elif b < 1024 * 1024:
        return f"{b / 1024:.1f} KB"
    elif b < 1024 * 1024 * 1024:
        return f"{b / (1024*1024):.1f} MB"
    else:
        return f"{b / (1024*1024*1024):.2f} GB"

def scan_with_feedback(sweeper: Sweeper) -> Tuple[List[Path], int]:
    """Live animated scanning with visible progress across folder items."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    target = sweeper.target_dir
    try:
        entries = [f for f in target.iterdir() if not sweeper.is_protected(f)]
    except Exception as e:
        print(f" {Style.YELLOW}Error accessing directory: {e}{Style.RESET}")
        return [], 0

    total_items = len(entries)
    if total_items == 0:
        return [], 0

    for i, item in enumerate(entries):
        frame = frames[i % len(frames)]
        short_name = (item.name[:25] + "...") if len(item.name) > 28 else item.name
        sys.stdout.write(f"\r {Style.PINK}{frame}{Style.RESET} {Style.CYAN}Analyzing item {i+1}/{total_items}:{Style.RESET} {Style.GRAY}{short_name:<30}{Style.RESET}")
        sys.stdout.flush()
        sweeper.get_size(item)
        if total_items < 100:
            time.sleep(0.005)

    sys.stdout.write("\r" + " " * 65 + "\r")
    sys.stdout.flush()
    total_size = sum(sweeper.get_size(f) for f in entries)
    return entries, total_size

def render_progress_bar(current: int, total: int, item_name: str = "", width: int = 24):
    """Smooth animated progress bar with current item preview."""
    pct = (current / total) if total > 0 else 1.0
    filled = int(width * pct)
    bar = f"{Style.CYAN}{'█' * filled}{Style.DIM}{'░' * (width - filled)}{Style.RESET}"
    pct_str = f"{int(pct * 100)}%"
    name_truncated = (item_name[:22] + "...") if len(item_name) > 25 else item_name
    sys.stdout.write(f"\r {Style.PINK}🧹 Sweeping{Style.RESET} [{bar}] {pct_str:>4} ({current}/{total}) {Style.GRAY}{name_truncated:<25}{Style.RESET}")
    sys.stdout.flush()
    time.sleep(0.01)

def render_interactive(sweeper: Sweeper):
    while True:
        print(banner())
        target = sweeper.target_dir
        print(f" {Style.BOLD}📂 Target Folder:{Style.RESET} {Style.CYAN}{target}{Style.RESET}\n")

        # Live scanning feedback
        items, total_size = scan_with_feedback(sweeper)

        print(f" {Style.BOLD}📊 Current Status:{Style.RESET}")
        print(f"   • Total loose items: {Style.BOLD}{len(items)}{Style.RESET}")
        print(f"   • Total folder size: {Style.BOLD}{format_bytes(total_size)}{Style.RESET}\n")

        # Clutter scan
        clutter_items, clutter_bytes = sweeper.scan_clutter()
        clutter_paths = {c["path"] for c in clutter_items}
        plan = sweeper.plan_organization(exclude_paths=clutter_paths)

        # Breakdown display
        print(f" {Style.BOLD}{Style.PINK}🧹 Clutter & Duplicates Detected:{Style.RESET}")
        if clutter_items:
            by_type = defaultdict(lambda: {"count": 0, "size": 0})
            for c in clutter_items:
                by_type[c["type"]]["count"] += 1
                by_type[c["type"]]["size"] += c["size"]
            for t, data in by_type.items():
                print(f"   {Style.YELLOW}•{Style.RESET} {t:<22}: {Style.BOLD}{data['count']:>3}{Style.RESET} items ({format_bytes(data['size'])})")
            print(f"   {Style.GREEN}➜ Total reclaimable:{Style.RESET} {Style.BOLD}{format_bytes(clutter_bytes)}{Style.RESET} (safely sent to OS Recycle Bin)\n")
        else:
            print(f"   {Style.GRAY}No redundant clutter or duplicate iterations found.{Style.RESET}\n")

        print(f" {Style.BOLD}{Style.CYAN}📁 Categorization Plan:{Style.RESET}")
        if plan:
            for cat, file_list in sorted(plan.items(), key=lambda x: len(x[1]), reverse=True):
                icon = DEFAULT_CATEGORIES.get(cat, {}).get("icon", "📁")
                cat_sz = sum(sweeper.get_size(f) for f in file_list)
                print(f"   {icon} {cat:<18}: {Style.BOLD}{len(file_list):>3}{Style.RESET} items ({format_bytes(cat_sz)})")
        else:
            print(f"   {Style.GRAY}No unorganized loose files found.{Style.RESET}")
        print()

        print(f"{Style.DIM}─────────────────────────────────────────────────────────────{Style.RESET}")
        print(f" {Style.BOLD}Choose an action:{Style.RESET}")
        print(f"  {Style.GREEN}[1]{Style.RESET} {Style.BOLD}Clean Clutter & Organize{Style.RESET} {Style.PINK}(Recommended){Style.RESET}")
        print(f"  {Style.CYAN}[2]{Style.RESET} Organize Only (Keep all files, sort into categories)")
        print(f"  {Style.YELLOW}[3]{Style.RESET} Clean Clutter Only (Send duplicates & installers to Recycle Bin)")
        print(f"  {Style.PURPLE}[4]{Style.RESET} Dry Run Preview (Simulate without touching anything)")
        print(f"  {Style.GRAY}[5]{Style.RESET} Undo Last Sweep")
        print(f"  {Style.BLUE}[c]{Style.RESET} {Style.BOLD}Change Target Folder{Style.RESET} (Type or paste any path)")
        print(f"  {Style.GRAY}[q]{Style.RESET} Quit\n")

        try:
            choice = input(f" {Style.BOLD}{Style.CYAN}sweeper ❯{Style.RESET} ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            sys.exit(0)

        if choice in {"c", "change", "cd"}:
            print(f"\n {Style.CYAN}📂 Enter or paste target folder path:{Style.RESET}")
            try:
                raw_path = input(f" {Style.BOLD}path ❯{Style.RESET} ").strip().strip('"').strip("'")
            except (KeyboardInterrupt, EOFError):
                break
            if raw_path:
                new_p = Path(raw_path).expanduser()
                if new_p.exists() and new_p.is_dir():
                    sweeper.set_target(new_p)
                    print(f"\n {Style.GREEN}✓ Switched target folder to: {sweeper.target_dir}{Style.RESET}")
                    time.sleep(0.6)
                else:
                    print(f"\n {Style.YELLOW}Folder not found: {raw_path}{Style.RESET}")
                    time.sleep(1.0)
            continue
        elif choice in {"1", "clean", "organize"}:
            confirm_and_run(sweeper, clean=True, organize=True, desc="clean clutter and organize loose files")
            break
        elif choice == "2":
            confirm_and_run(sweeper, clean=False, organize=True, desc="organize loose files into categories")
            break
        elif choice == "3":
            confirm_and_run(sweeper, clean=True, organize=False, desc="send duplicates and installers to the Recycle Bin")
            break
        elif choice == "4":
            res = sweeper.execute(clean_clutter=True, organize=True, dry_run=True)
            print(f"\n{Style.PURPLE}✨ Dry Run Completed!{Style.RESET}")
            print(f"   Would recycle: {res['clutter_count']} items ({format_bytes(res['clutter_bytes'])})")
            print(f"   Would organize into {len(res['organized_counts'])} category folders.\n")
            input(f" {Style.DIM}Press Enter to return to menu...{Style.RESET}")
            continue
        elif choice == "5":
            count, msg = sweeper.undo()
            print(f"\n{Style.GREEN}↺ {msg}{Style.RESET}\n")
            input(f" {Style.DIM}Press Enter to return to menu...{Style.RESET}")
            continue
        elif choice in {"q", "quit", "exit"}:
            print(f" {Style.GRAY}Bye! Keep it clean. 🧹✨{Style.RESET}")
            break
        else:
            print(f" {Style.GRAY}Please choose 1-5, 'c' to change folder, or 'q' to quit.{Style.RESET}\n")
            time.sleep(0.8)
            continue

def confirm_and_run(sweeper: Sweeper, clean: bool, organize: bool, desc: str):
    """Prompt for explicit confirmation before executing modifications."""
    print(f"\n {Style.YELLOW}⚠️  Are you sure you want to {desc}?{Style.RESET} [y/N]: ", end="", flush=True)
    try:
        ans = input().strip().lower()
    except (KeyboardInterrupt, EOFError):
        print(f"\n {Style.GRAY}✋ Cancelled.{Style.RESET}")
        return

    if ans in {"y", "yes"}:
        run_sweep(sweeper, clean=clean, organize=organize)
    else:
        print(f"\n {Style.GRAY}✋ Sweeper cancelled. No files were modified.{Style.RESET}\n")

def run_sweep(sweeper: Sweeper, clean: bool, organize: bool):
    start_t = time.time()
    
    def on_progress(curr, total, name):
        render_progress_bar(curr, total, name)

    res = sweeper.execute(clean_clutter=clean, organize=organize, dry_run=False, progress_callback=on_progress)
    elapsed = time.time() - start_t

    # Clean the progress line and play finish animation
    sys.stdout.write("\r" + " " * 75 + "\r")
    sys.stdout.flush()

    sparkles = ["✨", "🌟", "🎉", "🧹", "✨"]
    for s in sparkles:
        sys.stdout.write(f"\r {Style.GREEN}{Style.BOLD}{s} Sweeping complete!{Style.RESET} ({elapsed:.2f}s)   ")
        sys.stdout.flush()
        time.sleep(0.04)
    print("\n")

    if clean:
        print(f"   🗑️  {Style.BOLD}Recycled:{Style.RESET} {res['recycled_count']} items ({Style.GREEN}{format_bytes(res['recycled_bytes'])} freed{Style.RESET})")
    if organize:
        print(f"   📁 {Style.BOLD}Organized:{Style.RESET} {res['moved_count']} items into {len(res['categories'])} folders")

    print(f"\n {Style.DIM}Safety note: All moves can be reversed anytime with: {Style.CYAN}sweeper --undo{Style.RESET}\n")

# ==============================================================================
# CLI Entrypoint
# ==============================================================================

def watch_folder(sweeper: Sweeper, by_date: bool = False):
    """Background Watch Mode: quietly auto-sweeps completed downloads."""
    print(banner())
    print(f" {Style.GREEN}👁️  WATCH MODE ACTIVE{Style.RESET} on {Style.CYAN}{sweeper.target_dir}{Style.RESET}")
    print(f" {Style.GRAY}Sweeper is quietly monitoring for completed downloads in the background.{Style.RESET}")
    print(f" {Style.DIM}Press Ctrl+C anytime to stop.{Style.RESET}\n")

    temp_exts = {".crdownload", ".tmp", ".part", ".download", ".opdownload"}
    last_sizes = {}

    try:
        while True:
            time.sleep(2.0)
            try:
                for entry in list(sweeper.target_dir.iterdir()):
                    if sweeper.is_protected(entry):
                        continue
                    if entry.is_dir() and entry.name in sweeper.category_names:
                        continue
                    if entry.suffix.lower() in temp_exts:
                        continue

                    try:
                        current_size = entry.stat().st_size
                        mtime = entry.stat().st_mtime
                    except Exception:
                        continue

                    entry_str = str(entry)
                    if entry_str not in last_sizes:
                        last_sizes[entry_str] = (current_size, time.time())
                        continue

                    prev_size, first_seen = last_sizes[entry_str]
                    # File must be stable (size unchanged) for at least 2 seconds (download completed)
                    if current_size == prev_size and (time.time() - first_seen) >= 2.0:
                        cat = sweeper.classify(entry)
                        target_parent = sweeper.target_dir / cat
                        if by_date and entry.is_file():
                            try:
                                ym = time.strftime("%Y-%m", time.localtime(mtime))
                                target_parent = target_parent / ym
                            except Exception:
                                pass

                        target_parent.mkdir(parents=True, exist_ok=True)
                        final_dest = sweeper.get_safe_destination(target_parent, entry.name)
                        shutil.move(str(entry), str(final_dest))

                        timestamp = time.strftime("%H:%M:%S")
                        icon = sweeper.categories.get(cat, {}).get("icon", "📁")
                        print(f" [{Style.DIM}{timestamp}{Style.RESET}] {icon} Auto-swept: {Style.BOLD}{entry.name}{Style.RESET} ➜ {cat}/")
                        del last_sizes[entry_str]
                    else:
                        last_sizes[entry_str] = (current_size, first_seen)
            except Exception:
                pass
    except KeyboardInterrupt:
        print(f"\n\n {Style.GRAY}Stopped watch mode.{Style.RESET}\n")

def main():
    parser = argparse.ArgumentParser(
        description="🧹 SWEEPER — The intelligent, zero-dependency folder organizer.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("path", nargs="?", default=None, help="Target folder to sweep (defaults to Downloads)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without moving any files")
    parser.add_argument("--undo", action="store_true", help="Undo the last sweep in the target folder")
    parser.add_argument("--clean-only", action="store_true", help="Only prune junk & duplicate iterations")
    parser.add_argument("--organize-only", action="store_true", help="Only categorize files without pruning")
    parser.add_argument("--watch", action="store_true", help="Run in background watch mode to auto-sweep new downloads")
    parser.add_argument("--by-date", action="store_true", help="Organize files into year-month subfolders (e.g. Images/2026-11/)")
    parser.add_argument("--init-config", action="store_true", help="Generate a .sweeper.json configuration template")
    parser.add_argument("--install-context-menu", action="store_true", help="Add 'Sweep with Sweeper' to Windows right-click menu")
    parser.add_argument("--uninstall-context-menu", action="store_true", help="Remove 'Sweep with Sweeper' from Windows right-click menu")
    parser.add_argument("-y", "--yes", action="store_true", help="Non-interactive mode (auto confirm)")
    parser.add_argument("-v", "--version", action="version", version=f"sweeper {__version__}")

    args = parser.parse_args()

    # Context menu install / uninstall
    if args.install_context_menu:
        ok, msg = manage_context_menu(install=True)
        color = Style.GREEN if ok else Style.YELLOW
        print(f"{color}{msg}{Style.RESET}")
        sys.exit(0 if ok else 1)

    if args.uninstall_context_menu:
        ok, msg = manage_context_menu(install=False)
        color = Style.GREEN if ok else Style.YELLOW
        print(f"{color}{msg}{Style.RESET}")
        sys.exit(0 if ok else 1)

    # Determine target directory
    if args.path:
        target_dir = Path(args.path)
    else:
        target_dir = Path.home() / "Downloads"

    # Init config template
    if args.init_config:
        cfg = init_config(target_dir)
        print(f"{Style.GREEN}✓ Created configuration file at:{Style.RESET} {cfg}")
        sys.exit(0)

    if not target_dir.exists():
        print(f"{Style.YELLOW}Error: Folder '{target_dir}' does not exist.{Style.RESET}")
        sys.exit(1)

    sweeper = Sweeper(target_dir)

    # Watch Mode
    if args.watch:
        watch_folder(sweeper, by_date=args.by_date)
        sys.exit(0)

    # Handle Undo
    if args.undo:
        count, msg = sweeper.undo()
        print(f"{Style.GREEN}↺ {msg}{Style.RESET}")
        sys.exit(0)

    # Non-interactive CLI flags
    if args.dry_run or args.yes or args.clean_only or args.organize_only:
        clean = not args.organize_only
        org = not args.clean_only
        res = sweeper.execute(clean_clutter=clean, organize=org, dry_run=args.dry_run, by_date=args.by_date)
        if args.dry_run:
            print(f"Dry run complete. Clutter: {res['clutter_count']} items ({format_bytes(res['clutter_bytes'])}).")
        else:
            print(f"Swept: {res.get('recycled_count', 0)} recycled, {res.get('moved_count', 0)} organized.")
        sys.exit(0)

    # Default to Interactive UI
    render_interactive(sweeper)

if __name__ == "__main__":
    main()
