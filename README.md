# 🧹 Sweeper

> The lightweight, zero-dependency folder organizer with a friendly CLI interface, smart duplicate detection, and instant 1-click undo.

---

## ⚡ Instant Run (Zero Setup)

Run Sweeper instantly in your terminal without manual cloning or configuration:

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/sovon1/sweeper/main/run.ps1 | iex
```

### macOS & Linux
```bash
curl -fsSL https://raw.githubusercontent.com/sovon1/sweeper/main/run.sh | bash
```

### Python Package
```bash
pip install sweeper-cli
sweeper
```
Or run directly via Astral `uv`:
```bash
uvx sweeper-cli
```

---

## ✨ Features

- **Categorization:** Automatically sorts hundreds or thousands of loose files into clean, intuitive directories (`Documents`, `Images`, `Media`, `Archives`, `Code & Projects`, `Programs & Apps`).
- **Smart Duplicate Pruning:** Recognizes repeated download patterns (e.g. `file (1).png`, `file (2).png`) and safely recycles older duplicates while preserving the newest original.
- **Installer Cleanup:** Identifies leftover setup files (`.exe`, `.msi`, `.apk`) that are already installed.
- **100% Safe (Recycle Bin / Trash):** Never permanently erases your data. All cleaned items are moved to your operating system's native Recycle Bin or Trash.
- **Instant Undo (`--undo`):** Records an atomic transaction log for every sweep. Run `sweeper --undo` to restore every moved item back to its original position.
- **Collision Protection:** Automatically renames conflicting files with an incremental suffix (`_1`, `_2`) so no file is ever overwritten.
- **Zero External Dependencies:** Built entirely with Python's standard library. Starts up in milliseconds and uses less than 15 MB of RAM.

---

## 🚀 Usage

### Interactive Mode
By default, running `sweeper` targets your `Downloads` directory and displays an interactive menu:

```bash
python sweeper.py
```

### Specify a Custom Folder
Clean any messy folder, such as your Desktop:
```bash
python sweeper.py "C:\Users\sovon\Desktop\MyMessyFolder"
```

### Command-Line Flags

| Flag | Description |
| :--- | :--- |
| `--dry-run` | Preview all actions without modifying or moving any files |
| `--undo` | Reverse the previous sweep and return files to their original spots |
| `--organize-only` | Sort loose files into category folders without pruning clutter |
| `--clean-only` | Prune duplicates and installers without sorting folders |
| `-y, --yes` | Run non-interactively without confirmation prompts |
| `-v, --version` | Display version information |

---

## 🛡️ Safety Guarantees

1. **System File Protection:** System files such as `desktop.ini`, `.DS_Store`, `thumbs.db`, and `.git` are strictly protected and never touched.
2. **Transaction Ledger:** Every operation is saved locally in `.sweeper_history.json`.
3. **No Overwrites:** If a file with the same name exists in the target category, Sweeper appends an incrementing counter (`report_1.pdf`) to protect existing data.

---

## 🧪 Testing

Sweeper includes an automated test suite covering classification, duplicate clustering, safe collision handling, and atomic undo:

```bash
python -m unittest tests/test_sweeper.py
```

---

## 📄 License

Distributed under the MIT License.
