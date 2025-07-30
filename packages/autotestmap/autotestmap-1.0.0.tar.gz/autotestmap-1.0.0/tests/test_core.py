# autotestmap/tests/test_core.py

import unittest
from pathlib import Path
import os
import tempfile
import shutil

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from autotestmap.core import find_py_files, parse_file_dependencies, map_tests_to_sources

class TestCoreLogic(unittest.TestCase):

    def setUp(self):
        """Create a temporary directory with a mock project structure."""
        self.test_dir = tempfile.mkdtemp()
        self.src_root = Path(self.test_dir)
        self.src_path = self.src_root / "src" 
        self.tests_path = Path(self.test_dir) / "tests"
        self.src_path.mkdir()
        self.tests_path.mkdir()

        (self.src_path / "user.py").write_text("class User:\n    pass")
        (self.src_path / "utils.py").write_text("def helper():\n    return 1")
        (self.src_path / "untouchable.py").write_text("# No tests for me")
        
        (Path(self.test_dir) / ".venv").mkdir()
        (Path(self.test_dir) / ".venv" / "ignored.py").touch()

        (self.tests_path / "test_user.py").write_text("from src.user import User\n\nclass TestUser: ...")
        (self.tests_path / "test_features.py").write_text("from src.utils import helper\n\nclass TestFeatures: ...")
        (self.tests_path / "user_spec.py").write_text("from src.user import User\n\n# Another test for user")

    def tearDown(self):
        """Remove the temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_find_py_files(self):
        """Should find all Python files and ignore specified directories."""
        all_files = find_py_files(Path(self.test_dir))
        filenames = {f.name for f in all_files}
        self.assertIn("user.py", filenames)
        self.assertIn("test_features.py", filenames)
        self.assertNotIn("ignored.py", filenames)

    def test_parse_file_dependencies(self):
        """Should correctly identify imported modules."""
        imports = parse_file_dependencies(self.tests_path / "test_user.py")
        self.assertIn("src.user", imports)

    def test_map_tests_to_sources(self):
        """Should correctly map tests to source files."""
        result = map_tests_to_sources(str(self.src_path), str(self.tests_path))
        
        user_rel_path = "user.py"
        utils_rel_path = "utils.py"
        untouchable_rel_path = "untouchable.py"

        # Check user.py -> direct matches by name
        self.assertIn(user_rel_path, result)
        self.assertIn("test_user.py", result[user_rel_path]["direct"])
        self.assertIn("user_spec.py", result[user_rel_path]["direct"])
        self.assertEqual(len(result[user_rel_path]["indirect"]), 0) # No indirect-only links

        # Check utils.py -> it only has an INDIRECT match via import
        self.assertIn(utils_rel_path, result)
        self.assertEqual(len(result[utils_rel_path]["direct"]), 0) # No direct name match
        self.assertIn("test_features.py", result[utils_rel_path]["indirect"]) # Is an indirect match

        # Check untouchable.py -> has no matches
        self.assertIn(untouchable_rel_path, result)
        self.assertEqual(len(result[untouchable_rel_path]["direct"]), 0)
        self.assertEqual(len(result[untouchable_rel_path]["indirect"]), 0)


if __name__ == '__main__':
    unittest.main()