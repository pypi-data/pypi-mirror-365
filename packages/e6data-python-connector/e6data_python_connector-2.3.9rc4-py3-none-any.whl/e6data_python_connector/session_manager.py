"""
Process-safe session management for handling session invalidation and authentication.

This module provides coordinated session management that ensures proper session
invalidation across all workers during strategy transitions.
"""

import logging
import threading
import time
import weakref
from typing import Optional, Dict, Any, Set
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from .process_safe_manager import get_strategy_manager
from .retry_handler import retry_authentication, get_retry_handler

# Set up logging
_logger = logging.getLogger(__name__)

# Configuration constants
SESSION_CHECK_INTERVAL = 5.0  # Check session validity every 5 seconds
MAX_AUTHENTICATION_RETRIES = 3
AUTHENTICATION_RETRY_DELAY = 0.5  # Start with 500ms delay


@dataclass
class SessionInfo:
    """Information about a connection session."""
    session_id: str
    connection_id: str
    generation: int
    created_time: float
    last_used_time: float
    is_valid: bool = True


class ProcessSafeSessionManager:
    """
    Manages connection sessions across multiple processes.
    
    Provides session invalidation coordination and ensures that all workers
    properly handle session transitions during strategy changes.
    """
    
    def __init__(self):
        self._strategy_manager = get_strategy_manager()
        self._local_sessions: Dict[str, SessionInfo] = {}
        self._session_lock = threading.RLock()
        self._connection_registry: Set[weakref.ref] = set()
        self._registry_lock = threading.Lock()
        self._last_generation_check = 0
        self._authentication_executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="auth-")
        
    def register_connection(self, connection) -> str:
        """
        Register a connection for session management.
        
        Returns:
            A unique connection ID
        """
        connection_id = id(connection)
        
        with self._registry_lock:
            # Clean up dead references
            self._connection_registry = {
                ref for ref in self._connection_registry 
                if ref() is not None
            }
            
            # Add new connection
            weak_ref = weakref.ref(connection, lambda ref: self._unregister_connection_ref(ref))
            self._connection_registry.add(weak_ref)
            
        _logger.debug(f"Registered connection {connection_id}")
        return str(connection_id)
    
    def _unregister_connection_ref(self, weak_ref):
        """Clean up when a connection is garbage collected."""
        with self._registry_lock:
            self._connection_registry.discard(weak_ref)
    
    def create_session(self, connection_id: str, session_id: str) -> bool:
        """
        Create and register a new session.
        
        Args:
            connection_id: Unique connection identifier
            session_id: Session ID from authentication
            
        Returns:
            True if session was created successfully
        """
        if not session_id:
            return False
            
        current_generation = self._strategy_manager.get_session_generation()
        current_time = time.time()
        
        session_info = SessionInfo(
            session_id=session_id,
            connection_id=connection_id,
            generation=current_generation,
            created_time=current_time,
            last_used_time=current_time,
            is_valid=True
        )
        
        with self._session_lock:
            self._local_sessions[connection_id] = session_info
            
        _logger.debug(f"Created session {session_id[:8]}... for connection {connection_id} (gen {current_generation})")
        return True
    
    def get_session(self, connection_id: str) -> Optional[SessionInfo]:
        """
        Get session information for a connection.
        
        Args:
            connection_id: Unique connection identifier
            
        Returns:
            SessionInfo if valid session exists, None otherwise
        """
        with self._session_lock:
            session_info = self._local_sessions.get(connection_id)
            
            if not session_info:
                return None
                
            # Check if session is still valid based on generation
            current_generation = self._strategy_manager.get_session_generation()
            if session_info.generation < current_generation:
                session_info.is_valid = False
                _logger.debug(f"Session {session_info.session_id[:8]}... invalidated due to generation change "
                            f"({session_info.generation} < {current_generation})")
                return None
                
            # Update last used time
            session_info.last_used_time = time.time()
            return session_info
    
    def invalidate_session(self, connection_id: str) -> bool:
        """
        Invalidate a specific session.
        
        Args:
            connection_id: Unique connection identifier
            
        Returns:
            True if session was invalidated
        """
        with self._session_lock:
            session_info = self._local_sessions.get(connection_id)
            if session_info:
                session_info.is_valid = False
                _logger.debug(f"Invalidated session {session_info.session_id[:8]}... for connection {connection_id}")
                return True
            return False
    
    def remove_session(self, connection_id: str) -> bool:
        """
        Remove a session from tracking.
        
        Args:
            connection_id: Unique connection identifier
            
        Returns:
            True if session was removed
        """
        with self._session_lock:
            if connection_id in self._local_sessions:
                session_info = self._local_sessions.pop(connection_id)
                _logger.debug(f"Removed session {session_info.session_id[:8]}... for connection {connection_id}")
                return True
            return False
    
    def check_all_sessions(self) -> Dict[str, bool]:
        """
        Check validity of all tracked sessions.
        
        Returns:
            Dict mapping connection_id to validity status
        """
        current_generation = self._strategy_manager.get_session_generation()
        current_time = time.time()
        
        # Only check if generation changed or enough time passed
        if (current_generation == self._last_generation_check and 
            current_time - getattr(self, '_last_check_time', 0) < SESSION_CHECK_INTERVAL):
            return {}
            
        results = {}
        invalidated_sessions = []
        
        with self._session_lock:
            for connection_id, session_info in self._local_sessions.items():
                # Check generation-based invalidation
                if session_info.generation < current_generation:
                    session_info.is_valid = False
                    invalidated_sessions.append(connection_id)
                    results[connection_id] = False
                else:
                    results[connection_id] = session_info.is_valid
            
            self._last_generation_check = current_generation
            self._last_check_time = current_time
        
        if invalidated_sessions:
            _logger.info(f"Invalidated {len(invalidated_sessions)} sessions due to generation change "
                        f"(new generation: {current_generation})")
            
            # Notify connections about invalidation
            self._notify_connections_about_invalidation(invalidated_sessions)
            
        return results
    
    def _notify_connections_about_invalidation(self, invalidated_connection_ids: list):
        """Notify connections that their sessions have been invalidated."""
        with self._registry_lock:
            active_connections = [ref() for ref in self._connection_registry if ref() is not None]
        
        for connection in active_connections:
            if connection is not None:
                connection_id = str(id(connection))
                if connection_id in invalidated_connection_ids:
                    try:
                        # Set a flag that the connection can check
                        if hasattr(connection, '_session_invalidated_externally'):
                            connection._session_invalidated_externally = True
                    except Exception as e:
                        _logger.warning(f"Failed to notify connection {connection_id} about invalidation: {e}")
    
    def authenticate_with_retry(self, connection, max_retries: int = MAX_AUTHENTICATION_RETRIES) -> Optional[str]:
        """
        Perform authentication with retry logic using robust retry handler.
        
        Args:
            connection: Connection object to authenticate
            max_retries: Maximum number of retry attempts (for backward compatibility)
            
        Returns:
            Session ID if successful, None otherwise
        """
        def auth_operation():
            # Check if we should attempt authentication
            if hasattr(connection, '_should_skip_auth') and connection._should_skip_auth:
                raise Exception("Authentication skipped due to connection flag")
            
            # Attempt authentication
            session_id = self._perform_authentication(connection)
            if session_id:
                connection_id = str(id(connection))
                if self.create_session(connection_id, session_id):
                    _logger.debug("Authentication successful")
                    return session_id
                else:
                    raise Exception("Failed to create session after successful authentication")
            else:
                raise Exception("Authentication returned empty session ID")
        
        try:
            return retry_authentication(auth_operation)
        except Exception as e:
            _logger.error(f"Authentication failed after all retries: {e}")
            return None
    
    def _perform_authentication(self, connection) -> Optional[str]:
        """
        Perform the actual authentication with the connection.
        
        Args:
            connection: Connection object
            
        Returns:
            Session ID if successful, None otherwise
        """
        try:
            # Import here to avoid circular imports
            import grpc
            from grpc._channel import _InactiveRpcError
            from e6data_python_connector.server import e6x_engine_pb2
            from e6data_python_connector.strategy import _get_grpc_header as _get_strategy_header
            
            # Get current strategy
            current_strategy = self._strategy_manager.get_active_strategy()
            
            # If no strategy cached, try both blue and green
            if not current_strategy:
                strategies = ['blue', 'green']
            else:
                strategies = [current_strategy]
            
            for strategy in strategies:
                try:
                    authenticate_request = e6x_engine_pb2.AuthenticateRequest(
                        user=connection._Connection__username,
                        password=connection._Connection__password
                    )
                    
                    metadata = _get_strategy_header(
                        cluster=connection.cluster_name, 
                        strategy=strategy
                    )
                    
                    authenticate_response = connection._client.authenticate(
                        authenticate_request,
                        metadata=metadata
                    )
                    
                    session_id = authenticate_response.sessionId
                    if session_id:
                        # Cache the working strategy
                        self._strategy_manager.set_active_strategy(strategy)
                        
                        # Check for new strategy in response
                        if hasattr(authenticate_response, 'new_strategy') and authenticate_response.new_strategy:
                            new_strategy = authenticate_response.new_strategy.lower()
                            if new_strategy != strategy:
                                self._strategy_manager.set_pending_strategy(new_strategy)
                        
                        return session_id
                        
                except _InactiveRpcError as e:
                    if e.code() == grpc.StatusCode.UNKNOWN and 'status: 456' in e.details():
                        # Wrong strategy, try the next one
                        continue
                    else:
                        # Different error, re-raise
                        raise e
            
            # If we get here, neither strategy worked
            return None
            
        except Exception as e:
            _logger.error(f"Authentication error: {e}")
            raise e
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about session manager state."""
        with self._session_lock:
            session_count = len(self._local_sessions)
            valid_sessions = sum(1 for s in self._local_sessions.values() if s.is_valid)
            
            # Get session age statistics
            current_time = time.time()
            ages = [current_time - s.created_time for s in self._local_sessions.values()]
            avg_age = sum(ages) / len(ages) if ages else 0
            
        with self._registry_lock:
            registered_connections = len([ref for ref in self._connection_registry if ref() is not None])
        
        return {
            'total_sessions': session_count,
            'valid_sessions': valid_sessions,
            'invalid_sessions': session_count - valid_sessions,
            'registered_connections': registered_connections,
            'current_generation': self._strategy_manager.get_session_generation(),
            'last_generation_check': self._last_generation_check,
            'average_session_age': avg_age,
            'last_check_time': getattr(self, '_last_check_time', 0),
            'current_time': time.time()
        }
    
    def cleanup(self):
        """Clean up resources."""
        with self._session_lock:
            self._local_sessions.clear()
        
        with self._registry_lock:
            self._connection_registry.clear()
        
        self._authentication_executor.shutdown(wait=False)


# Global instance
_session_manager = ProcessSafeSessionManager()


def get_session_manager() -> ProcessSafeSessionManager:
    """Get the global session manager instance."""
    return _session_manager