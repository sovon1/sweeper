import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from sweeper import Sweeper, DEFAULT_CATEGORIES

class TestSweeper(unittest.TestCase):
    def setUp(self):
        # Create an isolated temporary directory
        self.test_dir = Path(tempfile.mkdtemp(prefix="sweeper_test_"))
        self.sweeper = Sweeper(self.test_dir)

    def tearDown(self):
        # Cleanup temporary directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_classification(self):
        """Test file classification into intuitive categories."""
        cases = {
            "report.pdf": "Documents",
            "thesis.docx": "Documents",
            "data.csv": "Documents",
            "photo.png": "Images",
            "avatar.jpg": "Images",
            "track.mp3": "Media",
            "recording.mp4": "Media",
            "backup.zip": "Archives",
            "archive.tar.gz": "Archives",
            "index.html": "Code & Projects",
            "script.py": "Code & Projects",
            "setup.exe": "Programs & Apps",
            "installer.apk": "Programs & Apps",
            "random.xyz": "Other"
        }
        for filename, expected_cat in cases.items():
            path = self.test_dir / filename
            path.touch()
            cat = self.sweeper.classify(path)
            self.assertEqual(cat, expected_cat, f"Failed for {filename}: expected {expected_cat}, got {cat}")

    def test_duplicate_cluster_detection(self):
        """Test detection of browser duplicate numbering: Designer.png vs Designer (1).png."""
        orig = self.test_dir / "Designer.png"
        orig.write_text("original content")
        dup1 = self.test_dir / "Designer (1).png"
        dup1.write_text("dup 1")
        dup2 = self.test_dir / "Designer (2).png"
        dup2.write_text("dup 2")

        clutter, _ = self.sweeper.scan_clutter()
        clutter_names = {c["path"].name for c in clutter}
        self.assertIn("Designer (1).png", clutter_names)
        self.assertIn("Designer (2).png", clutter_names)
        self.assertNotIn("Designer.png", clutter_names)  # Original must be kept!

    def test_organize_and_undo(self):
        """Test full organization and 1-second instant Undo restoration."""
        f1 = self.test_dir / "document.pdf"
        f1.write_text("pdf content")
        f2 = self.test_dir / "image.png"
        f2.write_text("png content")
        f3 = self.test_dir / "code.py"
        f3.write_text("python content")

        # Execute organization
        res = self.sweeper.execute(clean_clutter=False, organize=True)
        self.assertEqual(res["moved_count"], 3)

        # Verify they moved into category folders
        self.assertTrue((self.test_dir / "Documents" / "document.pdf").exists())
        self.assertTrue((self.test_dir / "Images" / "image.png").exists())
        self.assertTrue((self.test_dir / "Code & Projects" / "code.py").exists())
        self.assertFalse(f1.exists())

        # Now test UNDO!
        count, msg = self.sweeper.undo()
        self.assertEqual(count, 3)

        # Verify all files are restored to original location!
        self.assertTrue(f1.exists())
        self.assertTrue(f2.exists())
        self.assertTrue(f3.exists())
        # Empty category directories should be cleaned up
        self.assertFalse((self.test_dir / "Documents").exists())

    def test_collision_handling(self):
        """Verify that target collision renames safely without overwriting."""
        doc_dir = self.test_dir / "Documents"
        doc_dir.mkdir()
        (doc_dir / "notes.txt").write_text("existing content")

        # Create loose file with same name
        loose = self.test_dir / "notes.txt"
        loose.write_text("new content")

        res = self.sweeper.execute(clean_clutter=False, organize=True)
        self.assertEqual(res["moved_count"], 1)

        # Existing should be preserved
        self.assertEqual((doc_dir / "notes.txt").read_text(), "existing content")
        # New file should be renamed safely to notes_1.txt
        self.assertTrue((doc_dir / "notes_1.txt").exists())
        self.assertEqual((doc_dir / "notes_1.txt").read_text(), "new content")

if __name__ == "__main__":
    unittest.main()
