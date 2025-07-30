"""
Storage plugin for YAAPP framework.
Provides unified data persistence capabilities with multiple backends.
"""

from .plugin import (
    Storage,
    StorageManager,
    MemoryStorage,
    FileStorage,
    SQLiteStorage,
    create_memory_storage_manager,
    create_file_storage_manager,
    create_sqlite_storage_manager,
    create_hybrid_storage_manager,
    create_git_storage_manager
)

# Try to import Git storage
try:
    from .git import GitStorage
    __all__ = [
        "Storage", "StorageManager", "GitStorage",
        "MemoryStorage", "FileStorage", "SQLiteStorage",
        "create_memory_storage_manager", "create_file_storage_manager",
        "create_sqlite_storage_manager", "create_hybrid_storage_manager",
        "create_git_storage_manager"
    ]
except ImportError:
    # Git storage not available
    GitStorage = None
    __all__ = [
        "Storage", "StorageManager",
        "MemoryStorage", "FileStorage", "SQLiteStorage",
        "create_memory_storage_manager", "create_file_storage_manager",
        "create_sqlite_storage_manager", "create_hybrid_storage_manager",
        "create_git_storage_manager"
    ]