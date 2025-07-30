# autotestmap/autotestmap/core.py

import os
import ast
from pathlib import Path
from typing import List, Dict, Set

# The incorrect import from .utils is now removed.

# Directories to ignore during file discovery
DEFAULT_IGNORE_DIRS = {".venv", "venv", ".git", "__pycache__", "node_modules", "build", "dist"}

def find_py_files(base_dir: Path, ignore_dirs: Set[str] = DEFAULT_IGNORE_DIRS) -> List[Path]:
    """
    This function now correctly lives inside core.py and doesn't need to be imported.
    Recursively find all .py files under a given directory, ignoring specified folders.
    """
    py_files = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                py_files.append(Path(root) / file)
    return py_files

def parse_file_dependencies(filepath: Path) -> Set[str]:
    """
    Parses a Python file to extract the full module paths of its imports.
    """
    imports = set()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(filepath))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Warning: Could not parse {filepath}: {e}")
    return imports

def _map_single_file(src_file: Path, test_files: List[Path], test_dependencies: Dict[Path, Set[str]], test_dir_path: Path) -> Dict[str, List[str]]:
    """Helper function to map one source file against a list of test files."""
    src_module_name = src_file.stem
    related_tests = {"direct": [], "indirect": []}

    for test_file in test_files:
        test_rel_path = os.path.relpath(test_file, test_dir_path)
        imports = test_dependencies.get(test_file, set())

        # 1. Direct mapping based on file naming convention
        if src_module_name in test_file.stem and ("test" in test_file.stem or "spec" in test_file.stem):
            if test_rel_path not in related_tests["direct"]:
                related_tests["direct"].append(test_rel_path)
            continue

        # 2. Indirect mapping based on specific module imports
        is_imported = any(
            f".{src_module_name}" in imp or imp.endswith(src_module_name)
            for imp in imports
        )
        if is_imported:
            if test_rel_path not in related_tests["direct"] and test_rel_path not in related_tests["indirect"]:
                related_tests["indirect"].append(test_rel_path)

    return related_tests

def map_tests_to_sources(src_dir: str, test_dir: str) -> Dict[str, Dict[str, List[str]]]:
    """Maps all source files in a directory to their corresponding test files."""
    source_path = Path(src_dir).resolve()
    test_path = Path(test_dir).resolve()

    src_files = find_py_files(source_path)
    test_files = find_py_files(test_path)
    
    test_dependencies = {tf: parse_file_dependencies(tf) for tf in test_files}
    test_map = {}

    for src_file in src_files:
        src_rel_path = os.path.relpath(src_file, source_path)
        test_map[src_rel_path] = _map_single_file(src_file, test_files, test_dependencies, test_path)
        
    return test_map

def map_tests_to_single_file(src_file: str, test_dir: str) -> Dict[str, Dict[str, List[str]]]:
    """Maps a single source file to its corresponding test files."""
    source_file_path = Path(src_file).resolve()
    test_path = Path(test_dir).resolve()

    if not source_file_path.is_file():
        return {}

    test_files = find_py_files(test_path)
    test_dependencies = {tf: parse_file_dependencies(tf) for tf in test_files}
    test_map = {}

    src_rel_path = source_file_path.name
    test_map[src_rel_path] = _map_single_file(source_file_path, test_files, test_dependencies, test_path)
    
    return test_map