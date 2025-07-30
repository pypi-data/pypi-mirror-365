"""
e6data Python Connector - Enhanced with Process-Safe Auto-Resume

A DB-API 2.0 compliant database connector for the e6data distributed SQL Engine
with robust process-safe synchronization for high-concurrency environments.
"""

# Version info
__version__ = "1.0.0-process-safe"
__author__ = "e6data Team"

# Core connection interface
from e6data_python_connector.e6data_grpc import Connection, Cursor

# Process-safe components (optional imports for advanced use cases)
try:
    from .process_safe_manager import get_strategy_manager
    from .auto_resume_coordinator import get_resume_coordinator  
    from .session_manager import get_session_manager
    from .retry_handler import RetryHandler, RetryConfig
    
    # Mark as available
    __has_process_safe_features__ = True
    
except ImportError as e:
    # Graceful degradation if components are missing
    __has_process_safe_features__ = False
    import warnings
    warnings.warn(f"Process-safe features not available: {e}", ImportWarning)

# Public API
__all__ = ['Connection', 'Cursor']

# Add process-safe components to public API if available
if __has_process_safe_features__:
    __all__.extend([
        'get_strategy_manager',
        'get_resume_coordinator', 
        'get_session_manager',
        'RetryHandler',
        'RetryConfig'
    ])
