# autotestmap/autotestmap/utils.py

from pathlib import Path
from typing import Dict

def find_common_dirs() -> Dict[str, str]:
    """
    Automatically detect common names for source and test directories
    by searching ONLY in the current working directory.
    
    This is the most predictable behavior for users.
    """
    found_dirs = {}
    current_dir = Path('.') # Represents the directory where the user runs the command

    # Common names for source directories
    src_candidates = ['src', 'app', 'main']
    # Common names for test directories
    test_candidates = ['tests', 'test', 'spec']

    # Look for a source directory in the current path
    for candidate in src_candidates:
        if (current_dir / candidate).is_dir():
            found_dirs['src'] = candidate
            break # Stop after finding the first match

    # Look for a test directory in the current path
    for candidate in test_candidates:
        if (current_dir / candidate).is_dir():
            found_dirs['tests'] = candidate
            break # Stop after finding the first match
            
    return found_dirs