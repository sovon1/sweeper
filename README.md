# 🧹 Sweeper

> The lightweight, zero-dependency folder organizer with a friendly terminal UI, smart duplicate pruning, background watch mode, and instant 1-click undo.

---

## ⚡ Instant Run (Zero Setup)

Run Sweeper directly in your terminal without manual cloning or configuration:

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/sovon1/sweeper/main/run.ps1 | iex
```

### macOS & Linux
```bash
curl -fsSL https://raw.githubusercontent.com/sovon1/sweeper/main/run.sh | bash
```

### Python Package (pip / uv)
```bash
pip install sweeper-cli
sweeper
```
Or run directly with Astral `uv`:
```bash
uvx sweeper-cli
```

---

## ✨ Features

- **Intuitive Categorization:** Automatically organizes hundreds or thousands of loose files into clean directories (`Documents`, `Images`, `Media`, `Archives`, `Code & Projects`, `Programs & Apps`).
- **👁️ Background Watch Mode (`--watch`):** Keeps your Downloads folder clean permanently. Sweeper monitors in the background and auto-sorts new downloads as soon as they complete.
- **🖱️ Windows Right-Click Integration (`--install-context-menu`):** Adds a "🧹 Sweep with Sweeper" option when right-clicking any folder in Windows File Explorer.
- **📅 Date-Based Sub-folders (`--by-date`):** Automatically organizes files into year-month subdirectories (e.g. `Images/2026-11/`).
- **⚙️ Custom Config & Ignore Rules (`.sweeper.json`):** Add custom categories, file extensions, and custom ignore lists.
- **Smart Duplicate Pruning:** Recognizes repeated download patterns (e.g. `Designer (1).png`, `Designer (2).png`) and safely recycles older duplicates while preserving the newest original.
- **Installer Cleanup:** Identifies leftover setup files (`.exe`, `.msi`, `.apk`) that are already installed.
- **100% Safe (Recycle Bin / Trash):** Never permanently erases files. All cleaned items are moved to your operating system's native Recycle Bin or Trash.
- **Instant Undo (`--undo`):** Records an atomic transaction log for every sweep. Run `sweeper --undo` to restore every moved item back to its original location.
- **Zero External Dependencies:** Built entirely with Python's standard library. Starts up in milliseconds and uses less than 15 MB of RAM.

---

## 🚀 CLI Commands & Flags

| Command / Flag | Description |
| :--- | :--- |
| `sweeper` | Launch the interactive menu on your Downloads folder |
| `sweeper <path>` | Target any custom folder (e.g., `sweeper "C:\Users\sovon\Desktop"`) |
| `sweeper --watch` | **Watch Mode:** Run in the background and auto-sweep completed downloads |
| `sweeper --by-date` | Group files into Year-Month subfolders (`Images/2026-11/`) |
| `sweeper --install-context-menu` | Add "🧹 Sweep with Sweeper" to Windows Explorer right-click menu |
| `sweeper --uninstall-context-menu` | Remove Sweeper from Windows Explorer right-click menu |
| `sweeper --init-config` | Generate a `.sweeper.json` template in the target folder |
| `sweeper --dry-run` | Preview all actions without modifying or moving any files |
| `sweeper --undo` | Reverse the previous sweep and return files to their original spots |
| `sweeper --organize-only` | Sort loose files into category folders without pruning clutter |
| `sweeper --clean-only` | Prune duplicates and installers without sorting folders |
| `-y, --yes` | Run non-interactively without confirmation prompts |

---

## ⚙️ Custom Configuration (`.sweeper.json`)

Generate a template by running:
```bash
sweeper --init-config
```

Example `.sweeper.json`:
```json
{
  "by_date": false,
  "ignore": ["node_modules", "Important_*", "*.keep"],
  "custom_categories": {
    "Books & Comics": {
      "icon": "📚",
      "exts": [".epub", ".mobi", ".azw3", ".cbr"],
      "dir_keywords": ["book", "comic"]
    },
    "Design & 3D": {
      "icon": "🎨",
      "exts": [".blend", ".obj", ".stl", ".fbx", ".fig"],
      "dir_keywords": ["model", "3d", "render"]
    }
  }
}
```

---

## 🛡️ Safety Guarantees

1. **Explicit Confirmation:** Always prompts `Are you sure? [y/N]` before modifying files in interactive mode.
2. **System File & Shortcut Protection:** System files (`desktop.ini`, `.DS_Store`, `.git`) and desktop shortcuts (`.lnk`, `.url`) are never moved.
3. **No Overwrites:** If a file with the same name exists in the target category, Sweeper appends an incrementing counter (`notes_1.txt`) to protect existing data.

---

## 🧪 Testing

Sweeper includes an automated test suite covering classification, duplicate clustering, date sub-sorting, custom config loading, and atomic undo:

```bash
python -m unittest discover -s tests
```

---

## 📄 License

Distributed under the MIT License.
