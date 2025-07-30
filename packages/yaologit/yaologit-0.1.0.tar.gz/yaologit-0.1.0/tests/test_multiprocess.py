"""
Tests for YaoLogit multiprocessing functionality
"""

import os
import tempfile
import shutil
import multiprocessing
import time
from pathlib import Path
import pytest

from yaologit import get_logger, YaoLogit, YaoLogitConfig


def worker_process(worker_id, log_dir, num_messages):
    """Worker function for multiprocessing tests"""
    logger = get_logger(name="mp_test", log_dir=log_dir, verbose=False)
    
    for i in range(num_messages):
        logger.info(f"Worker {worker_id} - Message {i}")
        time.sleep(0.01)  # Small delay to allow interleaving


class TestMultiprocessing:
    """Test cases for multiprocessing functionality"""
    
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
    
    def test_multiple_processes_same_logger(self):
        """Test that multiple processes can use the same logger"""
        # Initialize logger in main process
        main_logger = get_logger(name="mp_test", log_dir=self.temp_dir, verbose=False)
        main_logger.info("Main process started")
        
        # Create worker processes
        num_workers = 3
        num_messages = 5
        processes = []
        
        for i in range(num_workers):
            p = multiprocessing.Process(
                target=worker_process,
                args=(i, self.temp_dir, num_messages)
            )
            p.start()
            processes.append(p)
        
        # Wait for all processes to complete
        for p in processes:
            p.join()
        
        main_logger.info("Main process finished")
        
        # Verify that log files exist
        log_dir = Path(self.temp_dir)
        assert (log_dir / "INFO").exists()
        
        # Check that log file contains messages from all processes
        log_files = list((log_dir / "INFO").glob("*.log"))
        assert len(log_files) > 0
        
        # Read log content and verify messages from different workers
        log_content = log_files[0].read_text()
        for i in range(num_workers):
            assert f"Worker {i}" in log_content
    
    def test_subprocess_inherits_configuration(self):
        """Test that subprocesses inherit logger configuration"""
        # Configure logger with specific settings
        config = YaoLogitConfig(
            name="inherit_test",
            log_dir=self.temp_dir,
            rotation="50 MB",
            retention="5 days",
            verbose=False
        )
        YaoLogit.configure(config)
        
        def subprocess_func():
            # Subprocess should be able to get the same logger
            logger = get_logger(name="inherit_test")
            logger.info("Subprocess message")
        
        # Create and run subprocess
        p = multiprocessing.Process(target=subprocess_func)
        p.start()
        p.join()
        
        # Verify log was created
        log_dir = Path(self.temp_dir)
        assert (log_dir / "INFO").exists()
    
    def test_concurrent_logging(self):
        """Test concurrent logging from multiple processes"""
        num_processes = 5
        messages_per_process = 10
        
        def concurrent_worker(worker_id):
            logger = get_logger(name="concurrent_test", log_dir=self.temp_dir, verbose=False)
            for i in range(messages_per_process):
                logger.info(f"Process {worker_id} - Log {i}")
                # No sleep to maximize concurrency
        
        # Initialize logger in main process
        main_logger = get_logger(name="concurrent_test", log_dir=self.temp_dir, verbose=False)
        
        # Create and start all processes at once
        processes = []
        for i in range(num_processes):
            p = multiprocessing.Process(target=concurrent_worker, args=(i,))
            p.start()
            processes.append(p)
        
        # Wait for completion
        for p in processes:
            p.join()
        
        # Verify all messages were logged
        log_dir = Path(self.temp_dir)
        log_files = list((log_dir / "INFO").glob("*.log"))
        assert len(log_files) > 0
        
        log_content = log_files[0].read_text()
        
        # Count messages from each process
        for i in range(num_processes):
            process_messages = log_content.count(f"Process {i}")
            assert process_messages == messages_per_process
    
    @pytest.mark.skipif(os.name == 'nt', reason="Fork not available on Windows")
    def test_fork_vs_spawn(self):
        """Test logger behavior with different process start methods"""
        # This test is skipped on Windows as fork is not available
        
        # Test with fork (Unix default)
        ctx = multiprocessing.get_context('fork')
        
        def fork_worker():
            logger = get_logger(name="fork_test", log_dir=self.temp_dir, verbose=False)
            logger.info("Fork worker message")
        
        logger = get_logger(name="fork_test", log_dir=self.temp_dir, verbose=False)
        logger.info("Main process before fork")
        
        p = ctx.Process(target=fork_worker)
        p.start()
        p.join()
        
        # Verify logs exist
        log_dir = Path(self.temp_dir)
        assert (log_dir / "INFO").exists()