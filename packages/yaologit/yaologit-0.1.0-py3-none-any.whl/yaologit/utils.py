"""
Utility functions for YaoLogit
"""

import os
import sys
import platform
import tempfile
import hashlib
from pathlib import Path
from typing import Optional
import json


def get_lock_file_path(name: str) -> Path:
    """
    Get the path for the lock file used to ensure single logger instance
    
    Args:
        name: Logger name
    
    Returns:
        Path to the lock file
    """
    # Use system temp directory for lock files
    temp_dir = Path(tempfile.gettempdir())
    
    # Create a unique lock file name based on the logger name and current working directory
    # This allows different projects to have their own logger instances
    cwd_hash = hashlib.md5(os.getcwd().encode()).hexdigest()[:8]
    lock_file_name = f"yaologit_{name}_{cwd_hash}.lock"
    
    return temp_dir / lock_file_name


def get_config_file_path(name: str) -> Path:
    """
    Get the path for the configuration file used to share config between processes
    
    Args:
        name: Logger name
    
    Returns:
        Path to the config file
    """
    temp_dir = Path(tempfile.gettempdir())
    cwd_hash = hashlib.md5(os.getcwd().encode()).hexdigest()[:8]
    config_file_name = f"yaologit_{name}_{cwd_hash}.json"
    
    return temp_dir / config_file_name


def acquire_lock(lock_file: Path, timeout: int = 5) -> Optional['FileLock']:
    """
    Acquire a file lock to ensure single logger instance
    
    Args:
        lock_file: Path to the lock file
        timeout: Timeout in seconds
    
    Returns:
        FileLock object if successful, None otherwise
    """
    try:
        import filelock
        lock = filelock.FileLock(str(lock_file), timeout=timeout)
        lock.acquire(timeout=timeout)
        return lock
    except ImportError:
        # If filelock is not available, use a simple file-based lock
        return SimpleLock(lock_file)
    except Exception:
        return None


class SimpleLock:
    """Simple file-based lock for when filelock is not available"""
    
    def __init__(self, lock_file: Path):
        self.lock_file = lock_file
        self.acquired = False
    
    def acquire(self, timeout: int = 5) -> bool:
        """Try to acquire the lock"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Try to create the lock file exclusively
                fd = os.open(str(self.lock_file), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.close(fd)
                self.acquired = True
                return True
            except OSError:
                # Lock file already exists, wait and retry
                time.sleep(0.1)
        
        return False
    
    def release(self):
        """Release the lock"""
        if self.acquired and self.lock_file.exists():
            try:
                self.lock_file.unlink()
                self.acquired = False
            except Exception:
                pass
    
    def __enter__(self):
        if not self.acquired:
            self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


def is_main_process() -> bool:
    """
    Check if this is the main process (not a subprocess)
    
    Returns:
        True if this is the main process
    """
    # Check if we're in a multiprocessing child process
    if hasattr(sys, '_base_executable'):
        # In a frozen application
        return True
    
    # Check multiprocessing
    try:
        import multiprocessing
        if multiprocessing.current_process().name != 'MainProcess':
            return False
    except Exception:
        pass
    
    return True


def save_config_to_file(config_file: Path, config: dict):
    """Save configuration to a file for sharing between processes"""
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass


def load_config_from_file(config_file: Path) -> Optional[dict]:
    """Load configuration from a file"""
    try:
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return None


def get_platform_info() -> dict:
    """Get platform information for debugging"""
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "pid": os.getpid(),
        "cwd": os.getcwd(),
    }


def cleanup_old_files(directory: Path, pattern: str, days: int = 7):
    """
    Clean up old files in a directory
    
    Args:
        directory: Directory to clean
        pattern: File pattern to match
        days: Files older than this many days will be deleted
    """
    import time
    from glob import glob
    
    if not directory.exists():
        return
    
    current_time = time.time()
    cutoff_time = current_time - (days * 24 * 60 * 60)
    
    for file_path in directory.glob(pattern):
        if file_path.is_file():
            file_mtime = file_path.stat().st_mtime
            if file_mtime < cutoff_time:
                try:
                    file_path.unlink()
                except Exception:
                    pass