# tests/test_lazy_initialization.py
import os
import pytest
from distributed_pg_lock import db, DistributedLockManager

def test_lazy_initialization_without_env(monkeypatch):
    """Test that DB operations fail without initialization or env var"""
    monkeypatch.delenv("DB_URL", raising=False)
    db.reset()
    
    with pytest.raises(RuntimeError) as excinfo:
        with db.session():
            pass
    
    assert "Database not initialized" in str(excinfo.value)

@pytest.mark.parametrize("init_method", ["env_var", "explicit"])
def test_lazy_initialization_works(monkeypatch, init_method, test_db_url):
    """Test initialization works through both methods"""
    db.reset()
    
    if init_method == "env_var":
        monkeypatch.setenv("DB_URL", test_db_url)
    else:
        db.initialize(db_url=test_db_url)
    
    # Verify DB operations work
    lock_manager = DistributedLockManager(lock_timeout_minutes=0.1)
    lock = lock_manager.get_lock("test_resource")
    
    assert lock.acquire()
    lock.release()