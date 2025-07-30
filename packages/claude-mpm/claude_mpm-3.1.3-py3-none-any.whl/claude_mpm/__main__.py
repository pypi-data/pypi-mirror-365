"""
Main entry point for claude-mpm package.

WHY: This module enables running claude-mpm as a Python module via `python -m claude_mpm`.
It's the standard Python pattern for making packages executable.

DESIGN DECISION: We only import and call the main function from the CLI module,
keeping this file minimal and focused on its single responsibility.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to ensure proper imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import main function from the new CLI module structure
from claude_mpm.cli import main

# Restore user's working directory if preserved by bash wrapper
# WHY: The bash wrapper preserves the user's launch directory in CLAUDE_MPM_USER_PWD
# to maintain proper file access permissions and security boundaries.
# Python imports work via PYTHONPATH, so we can safely restore the original directory.
if __name__ == "__main__":
    user_pwd = os.environ.get('CLAUDE_MPM_USER_PWD')
    if user_pwd and os.path.exists(user_pwd):
        try:
            os.chdir(user_pwd)
            # Only log if debug is enabled
            if os.environ.get('CLAUDE_MPM_DEBUG') == '1':
                print(f"[INFO] Restored working directory to: {user_pwd}")
        except Exception as e:
            # If we can't change to user directory, continue but log warning
            if os.environ.get('CLAUDE_MPM_DEBUG') == '1':
                print(f"[WARNING] Could not restore working directory to {user_pwd}: {e}")
    
    sys.exit(main())