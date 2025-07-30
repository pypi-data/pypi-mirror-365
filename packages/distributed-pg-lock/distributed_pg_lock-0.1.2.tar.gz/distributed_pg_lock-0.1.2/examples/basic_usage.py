"""
Basic Usage of Distributed Lock Manager
--------------------------------------
Demonstrates core functionality with context managers and explicit locking.
"""

import logging
import os
from time import sleep
from distributed_pg_lock import DistributedLockManager, db

# Configure package-level logging
logger = logging.getLogger(__name__)

def configure_logging():
    """Centralized logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def initialize_db():
    """Initialize database connection"""
    # Get your database URL (from environment, config, etc.)
    db_url = os.getenv("DB_URL", "postgresql://user:pass@localhost/mydb")
    
    # Explicit initialization
    db.initialize(db_url=db_url)
    db.create_tables()

def critical_operation_1(lock_manager):
    """Context manager pattern (recommended)"""
    lock = lock_manager.get_lock("report_generation")
    with lock:
        if lock.is_acquired:
            logger.info("Lock acquired - working")
            sleep(2)

def critical_operation_2(lock_manager):
    """Explicit acquire/release pattern"""
    lock = lock_manager.get_lock("data_migration")
    if lock.acquire():
        try:
            logger.info("Lock acquired - working")
            sleep(3)
        finally:
            lock.release()

def demonstrate_heartbeats(lock_manager):
    """Shows heartbeat maintenance"""
    lock = lock_manager.get_lock("batch_processing")
    with lock:
        if lock.is_acquired:
            for i in range(12):
                logger.info(f"Processing batch {i+1}")
                sleep(10)

def run_examples():
    """Execute all basic examples"""
    configure_logging()
    initialize_db()
    
    # Create lock manager AFTER database initialization
    lock_manager = DistributedLockManager(
        lock_timeout_minutes=1,
        owner_id="app-server-1"
    )
    
    logger.info("Running basic examples")
    critical_operation_1(lock_manager)
    critical_operation_2(lock_manager)
    demonstrate_heartbeats(lock_manager)
    logger.info("Basic examples completed")

if __name__ == "__main__":
    run_examples()