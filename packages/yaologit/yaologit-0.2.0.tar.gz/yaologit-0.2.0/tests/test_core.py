"""
Tests for YaoLogit core functionality
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest

from yaologit import YaoLogit, get_logger, YaoLogitConfig
from yaologit.exceptions import LoggerNotInitializedError, ConfigurationError


class TestYaoLogit:
    """Test cases for YaoLogit core functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test"""
        # Reset YaoLogit before each test
        YaoLogit.reset()
        
        # Create temporary directory for logs
        self.temp_dir = tempfile.mkdtemp()
        yield
        
        # Cleanup
        YaoLogit.reset()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_singleton_pattern(self):
        """Test that YaoLogit follows singleton pattern"""
        config = YaoLogitConfig(name="test", log_dir=self.temp_dir)
        
        # First initialization
        instance1 = YaoLogit.configure(config)
        
        # Second attempt should return the same instance
        instance2 = YaoLogit.configure(config)
        
        assert instance1 is instance2
    
    def test_basic_logging(self):
        """Test basic logging functionality"""
        logger = get_logger(name="test", log_dir=self.temp_dir, verbose=False)
        
        # Log some messages
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        
        # Check that log files were created
        log_dir = Path(self.temp_dir)
        assert (log_dir / "INFO").exists()
        assert (log_dir / "WARNING").exists()
        assert (log_dir / "ERROR").exists()
    
    def test_configuration_from_dict(self):
        """Test configuration from dictionary"""
        config_dict = {
            "name": "test_app",
            "log_dir": self.temp_dir,
            "verbose": False,
            "rotation": "10 MB",
            "retention": "3 days",
            "levels": ["INFO", "ERROR"]
        }
        
        config = YaoLogitConfig.from_dict(config_dict)
        assert config.name == "test_app"
        assert str(config.log_dir) == str(Path(self.temp_dir).resolve())
        assert config.rotation == "10 MB"
        assert config.retention == "3 days"
        assert config.levels == ["INFO", "ERROR"]
    
    def test_logger_not_initialized_error(self):
        """Test that accessing logger before initialization raises error"""
        with pytest.raises(LoggerNotInitializedError):
            YaoLogit.get_logger()
    
    def test_invalid_log_level(self):
        """Test that invalid log level raises error"""
        with pytest.raises(ValueError):
            YaoLogitConfig(
                name="test",
                log_dir=self.temp_dir,
                levels=["INFO", "INVALID_LEVEL"]
            )
    
    def test_logger_context_manager(self):
        """Test logger context manager"""
        logger = get_logger(name="test", log_dir=self.temp_dir, verbose=False)
        
        with YaoLogit.session("test_session", user_id=123) as session_logger:
            session_logger.info("Session message")
        
        # Context should be automatically cleaned up after exiting
        logger.info("Regular message after session")
    
    def test_logger_bind(self):
        """Test logger bind functionality"""
        logger = get_logger(name="test", log_dir=self.temp_dir, verbose=False)
        
        # Bind context data
        user_logger = YaoLogit.bind(user_id=456, action="login")
        user_logger.info("User action")
    
    def test_environment_configuration(self, monkeypatch):
        """Test configuration from environment variables"""
        # Set environment variables
        monkeypatch.setenv("YAOLOGIT_NAME", "env_test")
        monkeypatch.setenv("YAOLOGIT_LOG_DIR", self.temp_dir)
        monkeypatch.setenv("YAOLOGIT_VERBOSE", "false")
        monkeypatch.setenv("YAOLOGIT_LEVELS", "INFO,WARNING,ERROR")
        monkeypatch.setenv("YAOLOGIT_ROTATION", "5 days")
        
        # Load config from environment
        config = YaoLogitConfig.from_env()
        
        assert config.name == "env_test"
        assert str(config.log_dir) == str(Path(self.temp_dir).resolve())
        assert config.verbose is False
        assert config.levels == ["INFO", "WARNING", "ERROR"]
        assert config.rotation == "5 days"
    
    def test_get_logger_convenience_function(self):
        """Test the get_logger convenience function"""
        # Test with minimal parameters
        logger1 = get_logger(name="test1", log_dir=self.temp_dir)
        assert logger1 is not None
        
        # Test that calling again returns the same logger
        logger2 = get_logger(name="test1", log_dir=self.temp_dir)
        assert logger1 is logger2
    
    def test_log_file_creation(self):
        """Test that log files are created correctly"""
        config = YaoLogitConfig(
            name="test",
            log_dir=self.temp_dir,
            levels=["INFO", "ERROR"],
            separate_by_level=True,
            verbose=False
        )
        
        YaoLogit.configure(config)
        logger = YaoLogit.get_logger()
        
        # Log messages
        logger.info("Info message")
        logger.error("Error message")
        
        # Check directories were created
        log_dir = Path(self.temp_dir)
        assert (log_dir / "INFO").is_dir()
        assert (log_dir / "ERROR").is_dir()
    
    def test_single_file_mode(self):
        """Test logging to a single file instead of separate files"""
        config = YaoLogitConfig(
            name="test",
            log_dir=self.temp_dir,
            separate_by_level=False,
            verbose=False
        )
        
        YaoLogit.configure(config)
        logger = YaoLogit.get_logger()
        
        # Log messages at different levels
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Check that only one log file was created (not separate directories)
        log_dir = Path(self.temp_dir)
        log_files = list(log_dir.glob("*.log"))
        assert len(log_files) >= 1
        
        # Should not have level-specific directories
        assert not (log_dir / "INFO").exists()
        assert not (log_dir / "WARNING").exists()
        assert not (log_dir / "ERROR").exists()