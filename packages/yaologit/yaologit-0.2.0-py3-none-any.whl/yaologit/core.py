"""
Core implementation of YaoLogit - A process-safe logger based on loguru
"""

import os
import sys
import threading
import atexit
import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import contextmanager

from loguru import logger

from .config import YaoLogitConfig
from .exceptions import (
    YaoLogitError,
    ConfigurationError,
    LockError,
    LoggerNotInitializedError
)
from .utils import (
    get_lock_file_path,
    get_config_file_path,
    acquire_lock,
    save_config_to_file,
    load_config_from_file,
    is_main_process,
    cleanup_old_files
)


class YaoLogitMeta(type):
    """Metaclass for thread-safe singleton implementation"""
    
    _instances = {}
    _lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class YaoLogit(metaclass=YaoLogitMeta):
    """
    Process-safe singleton logger implementation based on loguru.
    
    Ensures only one logger instance exists across all processes and subprocesses.
    """
    
    _initialized = False
    _config: Optional[YaoLogitConfig] = None
    _process_lock = None
    _lock_file: Optional[Path] = None
    _config_file: Optional[Path] = None
    _thread_lock = threading.Lock()
    
    def __init__(self):
        """Initialize the logger instance"""
        if not self._initialized:
            raise LoggerNotInitializedError(
                "YaoLogit must be initialized with configure() before use"
            )
    
    @classmethod
    def configure(cls, config: Optional[YaoLogitConfig] = None, **kwargs) -> 'YaoLogit':
        """
        Configure and initialize the logger.
        
        Args:
            config: YaoLogitConfig instance or None to use defaults
            **kwargs: Additional keyword arguments to override config
        
        Returns:
            YaoLogit instance
        
        Raises:
            ConfigurationError: If configuration is invalid
            LockError: If unable to acquire process lock
        """
        with cls._thread_lock:
            # If already initialized, return existing instance
            if cls._initialized:
                return cls._instances.get(cls, cls())
            
            # Create config if not provided
            if config is None:
                # Try to load from environment first
                config = YaoLogitConfig.from_env()
            
            # Override with any kwargs
            if kwargs:
                config_dict = config.to_dict()
                config_dict.update(kwargs)
                config = YaoLogitConfig.from_dict(config_dict)
            
            # Get lock and config file paths
            cls._lock_file = get_lock_file_path(config.name)
            cls._config_file = get_config_file_path(config.name)
            
            # Try to acquire process lock
            cls._process_lock = acquire_lock(cls._lock_file)
            if cls._process_lock is None:
                # Check if we can load existing config
                existing_config = load_config_from_file(cls._config_file)
                if existing_config:
                    config = YaoLogitConfig.from_dict(existing_config)
                else:
                    raise LockError(
                        f"Unable to acquire lock for logger '{config.name}'. "
                        "Another process may be initializing the logger."
                    )
            else:
                # We have the lock, save our config
                save_config_to_file(cls._config_file, config.to_dict())
            
            # Store config
            cls._config = config
            
            # Configure loguru
            cls._setup_loguru(config)
            
            # Mark as initialized
            cls._initialized = True
            
            # Register cleanup
            atexit.register(cls._cleanup)
            
            # Create and return instance
            if cls not in cls._instances:
                cls._instances[cls] = object.__new__(cls)
            
            return cls._instances[cls]
    
    @classmethod
    def _setup_loguru(cls, config: YaoLogitConfig):
        """Set up loguru with the given configuration"""
        # Remove default handler
        logger.remove()
        
        # Add console handler if enabled
        if config.console_output and config.verbose:
            logger.add(
                sys.stderr,
                level=config.console_level,
                format=config.format,
                backtrace=config.backtrace,
                diagnose=config.diagnose,
                enqueue=config.enqueue,
            )
        
        # Get current date for log file names
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Add file handlers
        if config.separate_by_level:
            # Create separate file for each level
            for level in config.levels:
                log_file = config.log_dir / level / f"{level}_{config.name}_{today}.log"
                
                logger.add(
                    str(log_file),
                    level=level,
                    format=config.format,
                    encoding=config.encoding,
                    backtrace=config.backtrace,
                    diagnose=config.diagnose,
                    enqueue=config.enqueue,
                    rotation=config.rotation,
                    retention=config.retention,
                    compression=config.compression,
                    filter=lambda record, level=level: record["level"].name == level,
                )
        else:
            # Single file for all levels
            log_file = config.log_dir / f"{config.name}_{today}.log"
            
            logger.add(
                str(log_file),
                level="TRACE",  # Capture all levels
                format=config.format,
                encoding=config.encoding,
                backtrace=config.backtrace,
                diagnose=config.diagnose,
                enqueue=config.enqueue,
                rotation=config.rotation,
                retention=config.retention,
                compression=config.compression,
            )
        
        # Bind logger context
        from loguru import logger as loguru_logger
        loguru_logger = loguru_logger.bind(process_id=os.getpid())
        
        # Clean up old log files periodically
        if config.retention:
            try:
                # Extract days from retention string (e.g., "7 days" -> 7)
                days = int(config.retention.split()[0])
                cleanup_old_files(config.log_dir, "*.log", days)
            except Exception:
                pass
    
    @classmethod
    def get_logger(cls):
        """
        Get the logger instance.
        
        Returns:
            loguru.Logger instance
        
        Raises:
            LoggerNotInitializedError: If logger not initialized
        """
        if not cls._initialized:
            raise LoggerNotInitializedError(
                "YaoLogit must be initialized with configure() before use"
            )
        return logger
    
    @classmethod
    def _cleanup(cls):
        """Cleanup resources on exit"""
        if cls._process_lock:
            try:
                cls._process_lock.release()
            except Exception:
                pass
        
        if cls._lock_file and cls._lock_file.exists():
            try:
                cls._lock_file.unlink()
            except Exception:
                pass
        
        if cls._config_file and cls._config_file.exists():
            try:
                cls._config_file.unlink()
            except Exception:
                pass
    
    @classmethod
    def reset(cls):
        """Reset the logger (mainly for testing)"""
        with cls._thread_lock:
            cls._cleanup()
            cls._initialized = False
            cls._config = None
            cls._process_lock = None
            cls._lock_file = None
            cls._config_file = None
            if cls in YaoLogitMeta._instances:
                del YaoLogitMeta._instances[cls]
            logger.remove()
    
    @classmethod
    @contextmanager
    def session(cls, name: str, **kwargs):
        """
        Context manager for temporary logger session with specific context.
        
        Args:
            name: Session name
            **kwargs: Additional context to bind
        
        Yields:
            Contextualized logger
        """
        if not cls._initialized:
            raise LoggerNotInitializedError(
                "YaoLogit must be initialized with configure() before use"
            )
        
        # Create contextualized logger
        session_logger = logger.bind(session=name, **kwargs)
        
        try:
            yield session_logger
        finally:
            # Context automatically cleaned up when exiting
            pass
    
    @classmethod
    def bind(cls, **kwargs):
        """
        Bind context data to the logger.
        
        Args:
            **kwargs: Context data to bind
        
        Returns:
            Contextualized logger
        """
        if not cls._initialized:
            raise LoggerNotInitializedError(
                "YaoLogit must be initialized with configure() before use"
            )
        return logger.bind(**kwargs)
    
    @classmethod
    def configure_handler(cls, handler_config: Dict[str, Any]):
        """
        Add a custom handler to the logger.
        
        Args:
            handler_config: Handler configuration dictionary
        """
        if not cls._initialized:
            raise LoggerNotInitializedError(
                "YaoLogit must be initialized with configure() before use"
            )
        logger.add(**handler_config)
    
    # Proxy common logger methods
    def __getattr__(self, name):
        """Proxy attribute access to the logger instance"""
        if not self._initialized:
            raise LoggerNotInitializedError(
                "YaoLogit must be initialized with configure() before use"
            )
        return getattr(logger, name)


def get_logger(name: Optional[str] = None,
               log_dir: Optional[str] = None,
               verbose: bool = True,
               **kwargs) -> logger:
    """
    Convenience function to get a logger instance.

    This function initializes YaoLogit if not already initialized and returns
    the logger instance. It supports automatic configuration propagation
    to child processes using the main process ID.

    Args:
        name: Logger name (default: "yaologit").
        log_dir: Log directory (default: "./logs").
        verbose: Whether to enable console output (default: True).
        **kwargs: Additional configuration options.

    Returns:
        loguru.Logger instance.
    """
    main_pid_from_env = os.getenv("YAOLOGIT_MAIN_PID")
    config_dict = {}
    is_child_process = main_pid_from_env is not None

    # If in a child process, load config from the shared file based on main PID.
    if is_child_process:
        config_file_path = os.path.join(tempfile.gettempdir(), f"yaologit_config_{main_pid_from_env}.json")
        if os.path.exists(config_file_path):
            try:
                with open(config_file_path, 'r') as f:
                    config_dict = json.load(f)
            except (IOError, json.JSONDecodeError):
                pass  # Fallback to default if file is invalid

    # Update config with any explicitly passed arguments.
    # This allows the main process to set config, or a child to override it.
    if name is not None:
        config_dict['name'] = name
    if log_dir is not None:
        config_dict['log_dir'] = log_dir
    config_dict['verbose'] = verbose
    config_dict.update(kwargs)

    # If in the main process and providing config for the first time, save it for children.
    if is_main_process() and not is_child_process and (name or log_dir or kwargs):
        try:
            main_pid = os.getpid()
            config_file_path = os.path.join(tempfile.gettempdir(), f"yaologit_config_{main_pid}.json")

            with open(config_file_path, 'w') as f:
                json.dump(config_dict, f)

            os.environ["YAOLOGIT_MAIN_PID"] = str(main_pid)

            def _cleanup_config_file(path=config_file_path):
                if path and os.path.exists(path):
                    try:
                        os.unlink(path)
                    except OSError:
                        pass
            atexit.register(_cleanup_config_file)

        except IOError:
            # If we can't write the config file, logging will still work for the main process.
            pass

    # Configure the logger if it's not initialized or if the config has changed.
    current_config = YaoLogit._config.to_dict() if YaoLogit._config else {}
    if not YaoLogit._initialized or current_config != config_dict:
        YaoLogit.configure(**config_dict)

    return YaoLogit.get_logger()