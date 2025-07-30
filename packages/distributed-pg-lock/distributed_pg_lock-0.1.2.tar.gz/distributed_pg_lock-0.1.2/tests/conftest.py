import pytest
import os
from distributed_pg_lock import db, DistributedLockManager

TEST_DB_URL = "postgresql://postgres:surendra@localhost:5432/distributed_pg_lock_pip_db"

@pytest.fixture(scope="session", autouse=True)
def global_db_setup():
    """Global DB setup/teardown for all tests"""
    # Initialize only once per test session
    if not hasattr(db, '_instance') or db._instance is None:
        db.initialize(db_url=TEST_DB_URL)
    db.create_tables()
    yield
    db.drop_tables()
    db.reset()

@pytest.fixture
def lock_manager():
    """Fixture providing a lock manager instance"""
    return DistributedLockManager(lock_timeout_minutes=0.1)

@pytest.fixture
def test_db_url():
    return TEST_DB_URL