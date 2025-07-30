# autotestmap/autotestmap/cli.py

import argparse
import json
import os
from .core import map_tests_to_sources, map_tests_to_single_file
from .utils import find_common_dirs

def print_results(result: dict, verbose: bool):
    """Prints the mapping results in a human-readable format."""
    if not result:
        print("No source files or mappings found.")
        return

    found_any_tests = False
    for src, tests in result.items():
        direct_tests = tests.get("direct", [])
        indirect_tests = tests.get("indirect", [])

        if direct_tests or indirect_tests:
            found_any_tests = True
            print(f"✅ {src}")
            if direct_tests:
                print(f"  🔗 Direct → {', '.join(direct_tests)}")
            if indirect_tests:
                print(f"  🔎 Indirect → {', '.join(indirect_tests)}")
        elif verbose:
            print(f"⚠️ {src} → No tests found")

    if not found_any_tests and not verbose:
        print("No test relationships found. Try running with -v to see all source files.")

def main():
    """Main entry point for the autotestmap command-line tool."""
    parser = argparse.ArgumentParser(
        description="""
        Automatically map Python source files to their corresponding test files.
        Accepts 0, 1, or 2 arguments.
        - 0 args: Auto-discover 'src' and 'tests' directories.
        - 1 arg:  Map a single source file against an auto-discovered 'tests' directory.
        - 2 args: Map a source directory against a specified test directory.
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        'paths',
        nargs='*', # Accept 0 or more positional arguments
        help="[<source_file | source_dir> <test_dir>]"
    )
    parser.add_argument(
        "--json", 
        action="store_true", 
        help="Output the test map in JSON format."
    )
    parser.add_argument(
        "--verbose", 
        "-v",
        action="store_true", 
        help="Show all files, including those with no tests found."
    )

    args = parser.parse_args()
    result = {}
    
    num_paths = len(args.paths)
    auto_dirs = find_common_dirs()

    if num_paths == 0:
        # Mode 1: Auto-discovery for both directories
        print("🔍 Mode: Auto-discovery")
        src_dir = auto_dirs.get("src")
        test_dir = auto_dirs.get("tests")
        if not src_dir or not test_dir:
            print("Error: Could not automatically determine source or test directory.")
            print("Please specify them manually: autotestmap <source_dir> <test_dir>")
            return
        result = map_tests_to_sources(src_dir, test_dir)

    elif num_paths == 1:
        # Mode 2: Single source file mapping
        print("🔍 Mode: Single file mapping")
        source_file = args.paths[0]
        test_dir = auto_dirs.get("tests")
        if not os.path.isfile(source_file):
            print(f"Error: The provided path '{source_file}' is not a valid file.")
            return
        if not test_dir:
            print("Error: Could not automatically determine the test directory.")
            print("Please run this command from a directory containing a 'tests' folder.")
            return
        result = map_tests_to_single_file(source_file, test_dir)

    elif num_paths == 2:
        # Mode 3: User-specified directories
        print("🔍 Mode: User-specified directories")
        src_dir, test_dir = args.paths
        if not os.path.isdir(src_dir) or not os.path.isdir(test_dir):
            print(f"Error: One or both provided paths are not valid directories.")
            return
        result = map_tests_to_sources(src_dir, test_dir)

    else:
        parser.print_help()
        return

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_results(result, args.verbose)

if __name__ == "__main__":
    main()