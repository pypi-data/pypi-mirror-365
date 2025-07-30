import logging
import sys

# Set up library-specific logger
_logger = logging.getLogger("distributed_pg_lock")
_logger.setLevel(logging.INFO)

# Add default handler if none exists
if not _logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    _logger.addHandler(handler)

# Export public API
from .db import db
from .distributed_lock import DistributedLockManager, DistributedLock
from .exceptions import LockAcquisitionError, LockReleaseError

__all__ = [
    'db',
    'DistributedLockManager',
    'DistributedLock',
    'LockAcquisitionError',
    'LockReleaseError',
    'DistributedLockModel'
]