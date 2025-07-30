"""Bash command security validator for file access restrictions.

This module provides comprehensive validation for bash commands to ensure
agents cannot perform file operations outside their working directory.

Security patterns blocked:
- File writes via redirects (>, >>)
- File writes via commands (echo/cat > file, cp/mv to external paths)
- Directory operations outside working directory (mkdir, rmdir)
- Dangerous command patterns (rm -rf, sudo, etc)
"""

import re
import shlex
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Set
import logging

logger = logging.getLogger(__name__)


class BashSecurityValidator:
    """Validates bash commands for security violations.
    
    WHY: We need to prevent agents from writing outside their working directory
    through bash commands, which bypass the normal tool validation. This class
    parses bash commands and identifies file operations that would violate
    security boundaries.
    
    DESIGN DECISION: We parse commands rather than execute in a sandbox because:
    - Faster validation without subprocess overhead
    - Can provide detailed error messages about violations
    - Prevents any execution of potentially harmful commands
    """
    
    # Commands that can write/modify files
    WRITE_COMMANDS = {
        'echo', 'cat', 'printf', 'tee', 'sed', 'awk', 'perl', 'python',
        'python3', 'node', 'ruby', 'sh', 'bash', 'zsh', 'fish'
    }
    
    # Commands that copy/move files
    FILE_TRANSFER_COMMANDS = {
        'cp', 'mv', 'scp', 'rsync', 'install'
    }
    
    # Commands that create/modify directories
    DIR_COMMANDS = {
        'mkdir', 'rmdir', 'rm'
    }
    
    # Commands that are always dangerous
    DANGEROUS_COMMANDS = {
        'sudo', 'su', 'chmod', 'chown', 'chgrp', 'mkfs', 'dd',
        'format', 'fdisk', 'mount', 'umount'
    }
    
    # Redirect operators that can write files
    REDIRECT_OPERATORS = {'>', '>>', '>&', '&>', '>|'}
    
    def __init__(self, working_dir: Path):
        """Initialize validator with working directory.
        
        Args:
            working_dir: The directory agents are restricted to
        """
        self.working_dir = working_dir.resolve()
        
    def validate_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """Validate a bash command for security violations.
        
        Args:
            command: The bash command to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if command is safe, False if it violates security
            - error_message: Detailed error message if validation fails
        """
        try:
            # Check for dangerous commands first
            danger_check = self._check_dangerous_commands(command)
            if danger_check:
                return False, danger_check
            
            # Check for file redirects
            redirect_check = self._check_redirects(command)
            if redirect_check:
                return False, redirect_check
            
            # Check for file operations in commands
            file_op_check = self._check_file_operations(command)
            if file_op_check:
                return False, file_op_check
            
            # Check for directory operations
            dir_op_check = self._check_directory_operations(command)
            if dir_op_check:
                return False, dir_op_check
            
            # Check for pipe operations that could write files
            pipe_check = self._check_pipe_operations(command)
            if pipe_check:
                return False, pipe_check
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating bash command: {e}")
            # On error, be conservative and block
            return False, f"Command validation error: {str(e)}"
    
    def _check_dangerous_commands(self, command: str) -> Optional[str]:
        """Check for inherently dangerous commands.
        
        Args:
            command: The command to check
            
        Returns:
            Error message if dangerous command found, None otherwise
        """
        # Split by common separators to handle command chains
        parts = re.split(r'[;&|]', command)
        
        for part in parts:
            tokens = part.strip().split()
            if not tokens:
                continue
                
            cmd = tokens[0]
            
            # Check absolute dangerous commands
            if cmd in self.DANGEROUS_COMMANDS:
                return (f"Security Policy: Command '{cmd}' is not allowed.\n"
                       f"This command could compromise system security.")
            
            # Check for sudo/su with any command
            if cmd in ['sudo', 'su'] and len(tokens) > 1:
                return (f"Security Policy: Privileged command execution is not allowed.\n"
                       f"Command '{cmd}' cannot be used to escalate privileges.")
            
            # Check for rm -rf patterns
            if cmd == 'rm' and any(arg in tokens for arg in ['-rf', '-fr', '--force']):
                # Check if targeting root or system directories
                for token in tokens[1:]:
                    if token.startswith('/') and not token.startswith(str(self.working_dir)):
                        return (f"Security Policy: Dangerous rm command detected.\n"
                               f"Cannot remove files outside working directory.")
        
        return None
    
    def _check_redirects(self, command: str) -> Optional[str]:
        """Check for file redirects that write outside working directory.
        
        Args:
            command: The command to check
            
        Returns:
            Error message if unsafe redirect found, None otherwise
        """
        # Pattern to find redirects: > or >> followed by a file path
        # Handles cases like: echo "test" > /etc/passwd
        redirect_pattern = r'(' + '|'.join(re.escape(op) for op in self.REDIRECT_OPERATORS) + r')\s*([\'"]?)([^\s\'"]+)\2'
        
        for match in re.finditer(redirect_pattern, command):
            operator = match.group(1)
            file_path = match.group(3)
            
            # Skip descriptors like >&2
            if file_path.isdigit():
                continue
            
            # Validate the target path
            validation = self._validate_path(file_path)
            if not validation[0]:
                return (f"Security Policy: File redirect outside working directory not allowed.\n"
                       f"Redirect operator '{operator}' targeting: {file_path}\n"
                       f"{validation[1]}")
        
        # Also check for here-documents that might write files
        if '<<' in command:
            # Check if it's followed by a file write
            heredoc_write = re.search(r'<<.*?\|.*?>\s*([^\s]+)', command)
            if heredoc_write:
                file_path = heredoc_write.group(1)
                validation = self._validate_path(file_path)
                if not validation[0]:
                    return (f"Security Policy: Here-document redirect outside working directory.\n"
                           f"Target file: {file_path}")
        
        return None
    
    def _check_file_operations(self, command: str) -> Optional[str]:
        """Check for file operations that write outside working directory.
        
        Args:
            command: The command to check
            
        Returns:
            Error message if unsafe file operation found, None otherwise
        """
        try:
            # Parse command to handle quotes properly
            tokens = shlex.split(command)
        except ValueError:
            # If shlex fails, fall back to simple split
            tokens = command.split()
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Check copy/move commands
            if token in self.FILE_TRANSFER_COMMANDS:
                # These commands typically have source and destination
                # We need to check the destination
                dest_idx = None
                
                if token in ['cp', 'mv', 'install']:
                    # Skip options
                    j = i + 1
                    while j < len(tokens) and tokens[j].startswith('-'):
                        j += 1
                    # Last argument is typically destination
                    if j < len(tokens):
                        dest_idx = len(tokens) - 1
                
                elif token == 'rsync':
                    # rsync can have complex syntax, look for paths
                    for j in range(i + 1, len(tokens)):
                        if not tokens[j].startswith('-') and ':' not in tokens[j]:
                            # Potential local path
                            validation = self._validate_path(tokens[j])
                            if not validation[0]:
                                return (f"Security Policy: {token} operation outside working directory.\n"
                                       f"Target path: {tokens[j]}\n{validation[1]}")
                
                if dest_idx and dest_idx < len(tokens):
                    dest_path = tokens[dest_idx]
                    validation = self._validate_path(dest_path)
                    if not validation[0]:
                        return (f"Security Policy: {token} destination outside working directory.\n"
                               f"Destination: {dest_path}\n{validation[1]}")
            
            # Check for write operations via command substitution
            if token in self.WRITE_COMMANDS and i + 1 < len(tokens):
                # Look for patterns like: echo "data" > file
                for j in range(i + 1, len(tokens)):
                    if tokens[j] in self.REDIRECT_OPERATORS and j + 1 < len(tokens):
                        file_path = tokens[j + 1]
                        validation = self._validate_path(file_path)
                        if not validation[0]:
                            return (f"Security Policy: {token} write outside working directory.\n"
                                   f"Target file: {file_path}\n{validation[1]}")
            
            i += 1
        
        return None
    
    def _check_directory_operations(self, command: str) -> Optional[str]:
        """Check for directory operations outside working directory.
        
        Args:
            command: The command to check
            
        Returns:
            Error message if unsafe directory operation found, None otherwise
        """
        try:
            tokens = shlex.split(command)
        except ValueError:
            tokens = command.split()
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token in self.DIR_COMMANDS:
                # Check all arguments after the command
                for j in range(i + 1, len(tokens)):
                    arg = tokens[j]
                    # Skip options
                    if arg.startswith('-'):
                        continue
                    
                    # Validate the path
                    validation = self._validate_path(arg)
                    if not validation[0]:
                        return (f"Security Policy: {token} operation outside working directory.\n"
                               f"Target path: {arg}\n{validation[1]}")
            
            i += 1
        
        return None
    
    def _check_pipe_operations(self, command: str) -> Optional[str]:
        """Check for pipe operations that could write files.
        
        Args:
            command: The command to check
            
        Returns:
            Error message if unsafe pipe operation found, None otherwise
        """
        # Check for tee command which can write to files
        if 'tee' in command:
            tee_pattern = r'tee\s+(?:-[a-zA-Z]+\s+)*([^\s|]+)'
            for match in re.finditer(tee_pattern, command):
                file_path = match.group(1)
                validation = self._validate_path(file_path)
                if not validation[0]:
                    return (f"Security Policy: tee write outside working directory.\n"
                           f"Target file: {file_path}\n{validation[1]}")
        
        # Check for dd command which can write to files/devices
        if 'dd' in command:
            dd_pattern = r'of=([^\s]+)'
            match = re.search(dd_pattern, command)
            if match:
                file_path = match.group(1)
                validation = self._validate_path(file_path)
                if not validation[0]:
                    return (f"Security Policy: dd write outside working directory.\n"
                           f"Target file: {file_path}\n{validation[1]}")
        
        return None
    
    def _validate_path(self, path_str: str) -> Tuple[bool, str]:
        """Validate a path is within working directory.
        
        Args:
            path_str: The path string to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        # Handle empty or special paths
        if not path_str or path_str in ['-', '/dev/null', '/dev/stdout', '/dev/stderr']:
            return True, ""
        
        # Remove quotes if present
        path_str = path_str.strip('\'"')
        
        # Check for environment variables that typically point outside working directory
        # Common patterns: $HOME, ${HOME}, $USER, ${USER}, etc.
        env_patterns = [
            r'\$HOME', r'\${HOME}', r'~/', 
            r'\$USER', r'\${USER}',
            r'\$TMPDIR', r'\${TMPDIR}',
            r'/tmp/', r'/var/', r'/etc/', r'/usr/', r'/opt/',
            r'/System/', r'/Library/', r'/Applications/',  # macOS
            r'C:\\', r'D:\\',  # Windows
        ]
        
        for pattern in env_patterns:
            if re.search(pattern, path_str, re.IGNORECASE):
                return False, (f"Security Policy: Path '{path_str}' contains environment variable "
                             f"or system path that likely points outside working directory.\n"
                             f"Please use relative paths or absolute paths within '{self.working_dir}'")
        
        try:
            # Convert to Path object
            if path_str.startswith('/'):
                # Absolute path
                path = Path(path_str).resolve()
            else:
                # Relative path - resolve relative to working directory
                path = (self.working_dir / path_str).resolve()
            
            # Check if path is within working directory
            try:
                path.relative_to(self.working_dir)
                return True, ""
            except ValueError:
                # Path is outside working directory
                return False, (f"Path '{path_str}' resolves to '{path}' which is outside "
                             f"the working directory '{self.working_dir}'")
                
        except Exception as e:
            # If we can't resolve the path, be conservative and block
            return False, f"Cannot validate path '{path_str}': {str(e)}"


def create_validator(working_dir: Path) -> BashSecurityValidator:
    """Factory function to create a bash security validator.
    
    Args:
        working_dir: The working directory to restrict operations to
        
    Returns:
        Configured BashSecurityValidator instance
    """
    return BashSecurityValidator(working_dir)