# yaapp - Yet Another Python Package
# A library bridging FastAPI and CLI interfaces

from .app import Yaapp
from .execution_strategy import (
    execution_hint,
    direct_execution,
    thread_execution, 
    process_execution,
    auto_execution,
    ExecutionStrategy
)

__version__ = "0.1.0"
__all__ = [
    "Yaapp",
    "execution_hint",
    "direct_execution", 
    "thread_execution",
    "process_execution",
    "auto_execution",
    "ExecutionStrategy"
]
