"""
Process-safe strategy and auto-resume manager for high-concurrency environments.

This module provides proper synchronization primitives for managing blue-green deployment
strategies and cluster auto-resume functionality across multiple processes.
"""

import logging
import multiprocessing
import multiprocessing.managers
import threading
import time
import uuid
from typing import Optional, Dict, Any
import hashlib

# Set up logging
_logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_LOCK_TIMEOUT = 30.0  # 30 seconds for high-concurrency environments
STRATEGY_CACHE_TIMEOUT = 300  # 5 minutes
AUTO_RESUME_COOLDOWN = 60  # 1 minute between resume attempts
MAX_RETRY_ATTEMPTS = 3


class ProcessSafeDict(dict):
    """Process-safe dictionary wrapper with built-in locking."""
    
    def __init__(self, manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._manager = manager
        self._lock = manager.Lock()
        
    def safe_get(self, key, default=None, timeout=DEFAULT_LOCK_TIMEOUT):
        """Thread and process-safe get operation."""
        try:
            if self._lock.acquire(timeout=timeout):
                try:
                    return super().get(key, default)
                finally:
                    self._lock.release()
            else:
                _logger.warning(f"Failed to acquire lock for safe_get({key}) within {timeout}s")
                return default
        except Exception as e:
            _logger.error(f"Error in safe_get({key}): {e}")
            return default
    
    def safe_set(self, key, value, timeout=DEFAULT_LOCK_TIMEOUT):
        """Thread and process-safe set operation."""
        try:
            if self._lock.acquire(timeout=timeout):
                try:
                    super().__setitem__(key, value)
                    return True
                finally:
                    self._lock.release()
            else:
                _logger.warning(f"Failed to acquire lock for safe_set({key}) within {timeout}s")
                return False
        except Exception as e:
            _logger.error(f"Error in safe_set({key}): {e}")
            return False
    
    def safe_update(self, updates: Dict[str, Any], timeout=DEFAULT_LOCK_TIMEOUT):
        """Thread and process-safe batch update operation."""
        try:
            if self._lock.acquire(timeout=timeout):
                try:
                    for key, value in updates.items():
                        super().__setitem__(key, value)
                    return True
                finally:
                    self._lock.release()
            else:
                _logger.warning(f"Failed to acquire lock for safe_update within {timeout}s")
                return False
        except Exception as e:
            _logger.error(f"Error in safe_update: {e}")
            return False
    
    def safe_compare_and_swap(self, key, expected_value, new_value, timeout=DEFAULT_LOCK_TIMEOUT):
        """Atomic compare-and-swap operation."""
        try:
            if self._lock.acquire(timeout=timeout):
                try:
                    current_value = super().get(key)
                    if current_value == expected_value:
                        super().__setitem__(key, new_value)
                        return True
                    return False
                finally:
                    self._lock.release()
            else:
                _logger.warning(f"Failed to acquire lock for safe_compare_and_swap({key}) within {timeout}s")
                return False
        except Exception as e:
            _logger.error(f"Error in safe_compare_and_swap({key}): {e}")
            return False


class ProcessSafeStrategyManager:
    """
    Process-safe strategy manager for blue-green deployments.
    
    Handles strategy detection, caching, and transitions across multiple processes
    with proper synchronization and error handling.
    """
    
    def __init__(self):
        self._manager = None
        self._shared_state = None
        self._initialization_lock = threading.Lock()
        self._fallback_state = {
            'active_strategy': None,
            'pending_strategy': None,
            'last_check_time': 0,
            'last_transition_time': 0,
            'query_strategy_map': {},
            'session_generation': 0,  # Increment to invalidate all sessions
            'cluster_resume_state': {}
        }
        self._is_fallback_mode = False
        
    def _initialize_manager(self):
        """Initialize multiprocessing manager with retry logic."""
        if self._shared_state is not None:
            return True
            
        with self._initialization_lock:
            if self._shared_state is not None:
                return True
                
            for attempt in range(MAX_RETRY_ATTEMPTS):
                try:
                    self._manager = multiprocessing.Manager()
                    
                    # Test the manager with a simple operation
                    test_dict = self._manager.dict()
                    test_dict['test'] = 'value'
                    _ = test_dict['test']
                    
                    # Initialize shared state
                    shared_dict = self._manager.dict()
                    self._shared_state = ProcessSafeDict(self._manager, shared_dict)
                    
                    # Initialize with default values
                    initial_state = {
                        'active_strategy': None,
                        'pending_strategy': None,
                        'last_check_time': 0,
                        'last_transition_time': 0,
                        'query_strategy_map': self._manager.dict(),
                        'session_generation': 0,
                        'cluster_resume_state': self._manager.dict()
                    }
                    
                    self._shared_state.safe_update(initial_state)
                    
                    _logger.info("Successfully initialized multiprocessing Manager for strategy management")
                    return True
                    
                except Exception as e:
                    _logger.warning(f"Failed to initialize multiprocessing Manager (attempt {attempt + 1}/{MAX_RETRY_ATTEMPTS}): {e}")
                    if attempt < MAX_RETRY_ATTEMPTS - 1:
                        time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                    
            _logger.error("Failed to initialize multiprocessing Manager after all attempts. Using fallback mode.")
            self._is_fallback_mode = True
            return False
    
    def _get_state(self):
        """Get shared state, initializing if necessary."""
        if self._is_fallback_mode:
            return self._fallback_state
            
        if self._shared_state is None:
            if not self._initialize_manager():
                return self._fallback_state
                
        return self._shared_state
    
    def get_active_strategy(self) -> Optional[str]:
        """Get the currently active deployment strategy."""
        state = self._get_state()
        if self._is_fallback_mode:
            return state.get('active_strategy')
        return state.safe_get('active_strategy')
    
    def set_active_strategy(self, strategy: str) -> bool:
        """Set the active deployment strategy."""
        if not strategy or strategy.lower() not in ['blue', 'green']:
            _logger.warning(f"Invalid strategy value: {strategy}")
            return False
            
        normalized_strategy = strategy.lower()
        current_time = time.time()
        
        state = self._get_state()
        if self._is_fallback_mode:
            old_strategy = state.get('active_strategy')
            state['active_strategy'] = normalized_strategy
            state['last_check_time'] = current_time
            if old_strategy != normalized_strategy:
                state['last_transition_time'] = current_time
            return True
        else:
            updates = {
                'active_strategy': normalized_strategy,
                'last_check_time': current_time
            }
            
            # Only update transition time if strategy actually changed
            current_strategy = state.safe_get('active_strategy')
            if current_strategy != normalized_strategy:
                updates['last_transition_time'] = current_time
                
            return state.safe_update(updates)
    
    def get_pending_strategy(self) -> Optional[str]:
        """Get the pending deployment strategy."""
        state = self._get_state()
        if self._is_fallback_mode:
            return state.get('pending_strategy')
        return state.safe_get('pending_strategy')
    
    def set_pending_strategy(self, strategy: str) -> bool:
        """Set the pending deployment strategy."""
        if not strategy or strategy.lower() not in ['blue', 'green']:
            _logger.warning(f"Invalid pending strategy value: {strategy}")
            return False
            
        normalized_strategy = strategy.lower()
        
        state = self._get_state()
        current_active = self.get_active_strategy()
        
        if normalized_strategy == current_active:
            return True  # No change needed
            
        if self._is_fallback_mode:
            state['pending_strategy'] = normalized_strategy
            return True
        else:
            return state.safe_set('pending_strategy', normalized_strategy)
    
    def apply_pending_strategy(self) -> Optional[str]:
        """
        Apply pending strategy if no active queries are running.
        Returns the new strategy if applied, None otherwise.
        """
        state = self._get_state()
        
        if self._is_fallback_mode:
            pending = state.get('pending_strategy')
            if not pending:
                return None
                
            query_map = state.get('query_strategy_map', {})
            if len(query_map) > 0:
                return None  # Still have active queries
                
            old_strategy = state.get('active_strategy')
            current_time = time.time()
            
            state['active_strategy'] = pending
            state['pending_strategy'] = None
            state['last_check_time'] = current_time
            state['last_transition_time'] = current_time
            state['session_generation'] += 1  # Invalidate all sessions
            
            _logger.info(f"Strategy transition completed: {old_strategy} -> {pending}")
            return pending
        else:
            # Process-safe implementation
            pending = state.safe_get('pending_strategy')
            if not pending:
                return None
                
            query_map = state.safe_get('query_strategy_map', {})
            if isinstance(query_map, dict) and len(query_map) > 0:
                return None  # Still have active queries
                
            # Atomic compare-and-swap to prevent race conditions
            old_strategy = state.safe_get('active_strategy')
            current_time = time.time()
            session_gen = state.safe_get('session_generation', 0)
            
            updates = {
                'active_strategy': pending,
                'pending_strategy': None,
                'last_check_time': current_time,
                'last_transition_time': current_time,
                'session_generation': session_gen + 1
            }
            
            if state.safe_update(updates):
                _logger.info(f"Strategy transition completed: {old_strategy} -> {pending}")
                return pending
            else:
                _logger.warning("Failed to apply pending strategy due to lock contention")
                return None
    
    def invalidate_all_sessions(self) -> bool:
        """Invalidate all existing sessions by incrementing the generation counter."""
        state = self._get_state()
        
        if self._is_fallback_mode:
            state['session_generation'] += 1
            return True
        else:
            current_gen = state.safe_get('session_generation', 0)
            return state.safe_set('session_generation', current_gen + 1)
    
    def get_session_generation(self) -> int:
        """Get current session generation for invalidation checking."""
        state = self._get_state()
        if self._is_fallback_mode:
            return state.get('session_generation', 0)
        return state.safe_get('session_generation', 0)
    
    def register_query_strategy(self, query_id: str, strategy: str) -> bool:
        """Register the strategy used for a specific query."""
        if not query_id or not strategy:
            return False
            
        normalized_strategy = strategy.lower()
        if normalized_strategy not in ['blue', 'green']:
            return False
            
        state = self._get_state()
        
        if self._is_fallback_mode:
            query_map = state.get('query_strategy_map', {})
            query_map[query_id] = normalized_strategy
            return True
        else:
            query_map = state.safe_get('query_strategy_map', {})
            if hasattr(query_map, '__setitem__'):  # Manager dict
                try:
                    query_map[query_id] = normalized_strategy
                    return True
                except Exception as e:
                    _logger.error(f"Failed to register query strategy: {e}")
                    return False
            else:
                # Fallback to regular dict update
                query_map = dict(query_map) if query_map else {}
                query_map[query_id] = normalized_strategy
                return state.safe_set('query_strategy_map', query_map)
    
    def get_query_strategy(self, query_id: str) -> Optional[str]:
        """Get the strategy used for a specific query."""
        if not query_id:
            return self.get_active_strategy()
            
        state = self._get_state()
        
        if self._is_fallback_mode:
            query_map = state.get('query_strategy_map', {})
            return query_map.get(query_id, self.get_active_strategy())
        else:
            query_map = state.safe_get('query_strategy_map', {})
            if hasattr(query_map, 'get'):
                return query_map.get(query_id, self.get_active_strategy())
            else:
                query_dict = dict(query_map) if query_map else {}
                return query_dict.get(query_id, self.get_active_strategy())
    
    def cleanup_query_strategy(self, query_id: str) -> bool:
        """Remove the strategy mapping for a completed query."""
        if not query_id:
            return True
            
        state = self._get_state()
        
        if self._is_fallback_mode:
            query_map = state.get('query_strategy_map', {})
            if query_id in query_map:
                del query_map[query_id]
            return True
        else:
            query_map = state.safe_get('query_strategy_map', {})
            if hasattr(query_map, '__delitem__'):  # Manager dict
                try:
                    if query_id in query_map:
                        del query_map[query_id]
                    return True
                except Exception as e:
                    _logger.error(f"Failed to cleanup query strategy: {e}")
                    return False
            else:
                # Fallback to regular dict update
                query_dict = dict(query_map) if query_map else {}
                if query_id in query_dict:
                    del query_dict[query_id]
                return state.safe_set('query_strategy_map', query_dict)
    
    def clear_strategy_cache(self) -> bool:
        """Clear the strategy cache to force re-detection."""
        state = self._get_state()
        
        if self._is_fallback_mode:
            state['active_strategy'] = None
            state['last_check_time'] = 0
            state['pending_strategy'] = None
            return True
        else:
            updates = {
                'active_strategy': None,
                'last_check_time': 0,
                'pending_strategy': None
            }
            return state.safe_update(updates)
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about current strategy state."""
        state = self._get_state()
        
        if self._is_fallback_mode:
            query_map = state.get('query_strategy_map', {})
            return {
                'active_strategy': state.get('active_strategy'),
                'pending_strategy': state.get('pending_strategy'),
                'last_check_time': state.get('last_check_time', 0),
                'last_transition_time': state.get('last_transition_time', 0),
                'session_generation': state.get('session_generation', 0),
                'query_count': len(query_map),
                'current_time': time.time(),
                'is_fallback_mode': True
            }
        else:
            query_map = state.safe_get('query_strategy_map', {})
            query_count = len(query_map) if query_map else 0
            
            return {
                'active_strategy': state.safe_get('active_strategy'),
                'pending_strategy': state.safe_get('pending_strategy'),
                'last_check_time': state.safe_get('last_check_time', 0),
                'last_transition_time': state.safe_get('last_transition_time', 0),
                'session_generation': state.safe_get('session_generation', 0),
                'query_count': query_count,
                'current_time': time.time(),
                'is_fallback_mode': False
            }


# Global instance
_strategy_manager = ProcessSafeStrategyManager()


def get_strategy_manager() -> ProcessSafeStrategyManager:
    """Get the global strategy manager instance."""
    return _strategy_manager