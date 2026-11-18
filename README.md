# 🧹 Sweeper

> The lightweight, zero-dependency folder organizer with an aesthetic terminal UI, media intelligence engine, smart duplicate pruning, background watch mode, storage heatmaps, desktop stashing, and instant 1-click undo.

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

- **Intuitive Categorization:** Automatically organizes loose files into clean directories (`Documents`, `Images`, `Media`, `Archives`, `Code & Projects`, `Programs & Apps`).
- **🎬 Media Intelligence Engine:**
  - **Video vs. Audio Split:** Automatically routes videos to `Media/Videos/` and audio tracks to `Media/Audio & Music/`.
  - **Movies & Shows Detection:** Automatically recognizes release tags (`1080p`, `720p`, `4K`, `2160p`, `WEB-DL`, `HDR`, `x265`, `S01E02`) ➜ `Media/Videos/Movies & Shows/`.
  - **Tutorials & Courses:** Routes coding courses, masterclasses, and lectures ➜ `Media/Videos/Tutorials & Courses/`.
  - **Screen Recordings & Clips:** Detects OBS, Zoom, Loom, and screen captures ➜ `Media/Videos/Screen Recordings/`.
  - **Songs vs. Podcasts:** Separates music tracks (`Media/Audio & Music/Songs/`) from speech & podcasts (`Media/Audio & Music/Podcasts & Voice/`).
  - **🧲 Subtitle Companion Pairing:** Pairs `.srt`, `.vtt`, `.sub` files with their matching video files so subtitles are never orphaned.
- **🧠 Smart Semantic Sub-Tags:** Automatically detects file context and creates neat subfolders:
  - `invoice_may.pdf` ➜ `Documents/Invoices & Receipts/`
  - `resume_sovon.docx` ➜ `Documents/Resumes & CVs/`
  - `screenshot_12.png` ➜ `Images/Screenshots/`
  - `wallpaper_4k.jpg` ➜ `Images/Wallpapers/`
- **📊 Storage Heatmap & Space Hogs (`--heatmap`):** Beautiful ASCII distribution bar charts showing space allocation by category and listing your Top 10 Largest Space Hogs with Media Intelligence breakdown.
- **🔍 Content-Hash De-duplication (`--find-duplicates`):** Detects 100% byte-for-byte identical files even when their filenames are completely different.
- **💼 Presentation / Meeting Stash (`--stash` & `--unstash`):** Need to share your screen or give a presentation? Sweeper sweeps your messy desktop into a neat `Stash/` folder in 0.1s. Run `sweeper --unstash` to put everything back after the call!
- **👁️ Background Watch Mode (`--watch`):** Keeps your Downloads folder clean permanently. Sweeper monitors in the background and auto-sorts new downloads as soon as they complete.
- **🖱️ Windows Right-Click Integration (`--install-context-menu`):** Adds a "🧹 Sweep with Sweeper" option when right-clicking any folder in Windows File Explorer.
- **📅 Date-Based Sub-folders (`--by-date`):** Automatically organizes files into year-month subdirectories (e.g. `Images/2026-11/`).
- **⚙️ Custom Config & Ignore Rules (`.sweeper.json`):** Add custom categories, file extensions, and custom ignore lists.
- **100% Safe (Recycle Bin / Trash):** Never permanently erases files. All cleaned items are moved to your operating system's native Recycle Bin or Trash.
- **Instant Undo (`--undo`):** Records an atomic transaction log for every sweep. Run `sweeper --undo` to restore every moved item back to its original location.
- **Zero External Dependencies:** Built entirely with Python's standard library. Starts up in milliseconds and uses less than 15 MB of RAM.

---

## 🚀 CLI Commands & Flags

| Command / Flag | Description |
| :--- | :--- |
| `sweeper` | Launch the interactive menu on your Downloads folder |
| `sweeper <path>` | Target any custom folder (e.g., `sweeper "C:\Users\sovon\Desktop"`) |
| `sweeper --heatmap` | **Storage Heatmap:** Display ASCII space breakdown and Top 10 Space Hogs |
| `sweeper --find-duplicates` | **Hash De-duplication:** Find identical files with different names |
| `sweeper --stash` | **Desktop Stash:** Clean all loose desktop files for presentations |
| `sweeper --unstash` | Restore files from the most recent Stash folder |
| `sweeper --watch` | **Watch Mode:** Run in background and auto-sweep completed downloads |
| `sweeper --by-date` | Group files into Year-Month subfolders (`Images/2026-11/`) |
| `sweeper --install-context-menu` | Add "🧹 Sweep with Sweeper" to Windows Explorer right-click menu |
| `sweeper --uninstall-context-menu` | Remove Sweeper from Windows Explorer right-click menu |
| `sweeper --init-config` | Generate a `.sweeper.json` template in the target folder |
| `sweeper --dry-run` | Preview all actions without modifying or moving any files |
| `sweeper --undo` | Reverse the previous sweep and return files to their original spots |
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
      "exts": [".blend", ".obj", ".stl", ".fbx"],
      "dir_keywords": ["model", "3d", "render"]
    }
  }
}
```

---

## 🧪 Testing

Sweeper includes an automated test suite covering classification, duplicate clustering, content-hash matching, media companion pairing, presentation stash, date sub-sorting, and atomic undo:

```bash
python -m unittest discover -s tests
```

---

## 📄 License

Distributed under the MIT License.
