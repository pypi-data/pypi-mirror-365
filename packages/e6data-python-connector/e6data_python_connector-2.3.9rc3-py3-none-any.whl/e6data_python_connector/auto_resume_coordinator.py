"""
Auto-resume coordinator for process-safe cluster resume operations.

This module provides coordinated cluster resume functionality that prevents
multiple processes from attempting to resume the same cluster simultaneously.
"""

import logging
import multiprocessing
import threading
import time
import hashlib
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from .process_safe_manager import get_strategy_manager, DEFAULT_LOCK_TIMEOUT

# Set up logging
_logger = logging.getLogger(__name__)

# Configuration constants
AUTO_RESUME_COOLDOWN = 60  # 1 minute between resume attempts per cluster
MAX_RESUME_ATTEMPTS = 3
RESUME_LOCK_TIMEOUT = 30.0  # 30 seconds
RESUME_STATUS_TIMEOUT = 600  # 10 minutes maximum wait for resume


@dataclass
class ResumeAttempt:
    """Information about a cluster resume attempt."""
    cluster_id: str
    timestamp: float
    worker_id: str
    attempt_count: int
    status: str  # 'in_progress', 'completed', 'failed'
    result: Optional[bool] = None


class ProcessSafeResumeCoordinator:
    """
    Coordinates cluster resume operations across multiple processes.
    
    Ensures that only one process attempts to resume a cluster at a time,
    and provides proper coordination and status tracking.
    """
    
    def __init__(self):
        self._manager = None
        self._shared_state = None
        self._initialization_lock = threading.Lock()
        self._fallback_state = {
            'active_resumes': {},  # cluster_id -> ResumeAttempt
            'resume_history': {},  # cluster_id -> list of attempts
            'global_lock_holder': None,
            'last_cleanup': 0
        }
        self._is_fallback_mode = False
        self._worker_id = self._generate_worker_id()
        
    def _generate_worker_id(self) -> str:
        """Generate a unique worker ID for this process."""
        import os
        pid = os.getpid()
        tid = threading.get_ident()
        timestamp = time.time()
        hash_input = f"{pid}_{tid}_{timestamp}".encode()
        return hashlib.md5(hash_input).hexdigest()[:8]
    
    def _initialize_manager(self):
        """Initialize multiprocessing manager with retry logic."""
        if self._shared_state is not None:
            return True
            
        with self._initialization_lock:
            if self._shared_state is not None:
                return True
                
            try:
                # Try to reuse the strategy manager's multiprocessing manager
                strategy_manager = get_strategy_manager()
                if hasattr(strategy_manager, '_manager') and strategy_manager._manager:
                    self._manager = strategy_manager._manager
                else:
                    self._manager = multiprocessing.Manager()
                
                # Initialize shared state
                self._shared_state = self._manager.dict()
                self._shared_state['active_resumes'] = self._manager.dict()
                self._shared_state['resume_history'] = self._manager.dict()
                self._shared_state['global_lock'] = self._manager.Lock()
                self._shared_state['last_cleanup'] = 0
                
                _logger.info("Successfully initialized auto-resume coordinator")
                return True
                
            except Exception as e:
                _logger.error(f"Failed to initialize auto-resume coordinator: {e}")
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
    
    def _cleanup_old_attempts(self, state):
        """Clean up old resume attempts to prevent memory leaks."""
        current_time = time.time()
        last_cleanup = state.get('last_cleanup', 0)
        
        # Only cleanup every 5 minutes
        if current_time - last_cleanup < 300:
            return
            
        try:
            if self._is_fallback_mode:
                # Clean up old active resumes
                active_resumes = state.get('active_resumes', {})
                expired_keys = []
                for cluster_id, attempt_data in active_resumes.items():
                    if current_time - attempt_data['timestamp'] > RESUME_STATUS_TIMEOUT:
                        expired_keys.append(cluster_id)
                
                for key in expired_keys:
                    del active_resumes[key]
                    
                # Clean up old history entries (keep last 10 per cluster)
                resume_history = state.get('resume_history', {})
                for cluster_id, attempts in resume_history.items():
                    if len(attempts) > 10:
                        attempts[:] = attempts[-10:]
                        
                state['last_cleanup'] = current_time
                
            else:
                # Process-safe cleanup
                active_resumes = state.get('active_resumes', {})
                if hasattr(active_resumes, 'items'):
                    expired_keys = []
                    for cluster_id, attempt_data in active_resumes.items():
                        if current_time - attempt_data.get('timestamp', 0) > RESUME_STATUS_TIMEOUT:
                            expired_keys.append(cluster_id)
                    
                    for key in expired_keys:
                        try:
                            del active_resumes[key]
                        except KeyError:
                            pass  # Already cleaned up by another process
                
                state['last_cleanup'] = current_time
                
        except Exception as e:
            _logger.warning(f"Error during cleanup: {e}")
    
    def _get_cluster_key(self, host: str, port: int, cluster_name: str) -> str:
        """Generate a unique key for a cluster."""
        return f"{host}:{port}:{cluster_name}"
    
    def should_attempt_resume(self, host: str, port: int, cluster_name: str) -> Tuple[bool, Optional[str]]:
        """
        Check if this worker should attempt to resume the cluster.
        
        Returns:
            Tuple of (should_resume, reason)
        """
        cluster_key = self._get_cluster_key(host, port, cluster_name)
        current_time = time.time()
        state = self._get_state()
        
        # Cleanup old attempts
        self._cleanup_old_attempts(state)
        
        if self._is_fallback_mode:
            active_resumes = state.get('active_resumes', {})
            
            # Check if there's an active resume for this cluster
            if cluster_key in active_resumes:
                attempt = active_resumes[cluster_key]
                if current_time - attempt['timestamp'] < RESUME_STATUS_TIMEOUT:
                    if attempt['status'] == 'in_progress':
                        return False, f"Resume already in progress by worker {attempt['worker_id']}"
                    elif attempt['status'] == 'completed' and attempt.get('result'):
                        if current_time - attempt['timestamp'] < AUTO_RESUME_COOLDOWN:
                            return False, "Cluster recently resumed successfully"
                
            # Check resume history for cooldown
            resume_history = state.get('resume_history', {})
            if cluster_key in resume_history:
                recent_attempts = [
                    att for att in resume_history[cluster_key]
                    if current_time - att['timestamp'] < AUTO_RESUME_COOLDOWN
                ]
                if recent_attempts:
                    last_attempt = max(recent_attempts, key=lambda x: x['timestamp'])
                    if last_attempt['status'] == 'completed' and last_attempt.get('result'):
                        return False, "Cluster recently resumed (from history)"
                    elif len(recent_attempts) >= MAX_RESUME_ATTEMPTS:
                        return False, f"Too many recent resume attempts ({len(recent_attempts)})"
            
            return True, "No recent resume activity"
            
        else:
            # Process-safe implementation
            try:
                global_lock = state.get('global_lock')
                if global_lock and global_lock.acquire(timeout=5.0):
                    try:
                        active_resumes = state.get('active_resumes', {})
                        
                        # Check if there's an active resume for this cluster
                        if cluster_key in active_resumes:
                            attempt_data = active_resumes[cluster_key]
                            if current_time - attempt_data.get('timestamp', 0) < RESUME_STATUS_TIMEOUT:
                                if attempt_data.get('status') == 'in_progress':
                                    return False, f"Resume already in progress by worker {attempt_data.get('worker_id')}"
                                elif (attempt_data.get('status') == 'completed' and 
                                      attempt_data.get('result') and
                                      current_time - attempt_data.get('timestamp', 0) < AUTO_RESUME_COOLDOWN):
                                    return False, "Cluster recently resumed successfully"
                        
                        return True, "No active resume in progress"
                        
                    finally:
                        global_lock.release()
                else:
                    _logger.warning("Failed to acquire global lock for resume check")
                    return False, "Lock contention - skip resume attempt"
                    
            except Exception as e:
                _logger.error(f"Error checking resume eligibility: {e}")
                return False, f"Error during check: {e}"
    
    def start_resume_attempt(self, host: str, port: int, cluster_name: str) -> bool:
        """
        Register the start of a resume attempt.
        
        Returns:
            True if this worker should proceed with resume, False otherwise
        """
        cluster_key = self._get_cluster_key(host, port, cluster_name)
        current_time = time.time()
        state = self._get_state()
        
        attempt = {
            'cluster_id': cluster_key,
            'timestamp': current_time,
            'worker_id': self._worker_id,
            'attempt_count': 1,
            'status': 'in_progress',
            'result': None
        }
        
        if self._is_fallback_mode:
            active_resumes = state.get('active_resumes', {})
            
            # Double-check that no one else started while we were deciding
            if cluster_key in active_resumes:
                existing = active_resumes[cluster_key]
                if (existing['status'] == 'in_progress' and 
                    current_time - existing['timestamp'] < RESUME_STATUS_TIMEOUT):
                    return False
            
            # Register our attempt
            active_resumes[cluster_key] = attempt
            _logger.info(f"Worker {self._worker_id} starting resume for cluster {cluster_key}")
            return True
            
        else:
            try:
                global_lock = state.get('global_lock')
                if global_lock and global_lock.acquire(timeout=RESUME_LOCK_TIMEOUT):
                    try:
                        active_resumes = state.get('active_resumes', {})
                        
                        # Double-check that no one else started while we were waiting
                        if cluster_key in active_resumes:
                            existing = active_resumes[cluster_key]
                            if (existing.get('status') == 'in_progress' and 
                                current_time - existing.get('timestamp', 0) < RESUME_STATUS_TIMEOUT):
                                return False
                        
                        # Register our attempt
                        active_resumes[cluster_key] = attempt
                        _logger.info(f"Worker {self._worker_id} starting resume for cluster {cluster_key}")
                        return True
                        
                    finally:
                        global_lock.release()
                else:
                    _logger.warning(f"Failed to acquire resume lock for {cluster_key} within {RESUME_LOCK_TIMEOUT}s")
                    return False
                    
            except Exception as e:
                _logger.error(f"Error starting resume attempt: {e}")
                return False
    
    def complete_resume_attempt(self, host: str, port: int, cluster_name: str, 
                              success: bool, error_message: Optional[str] = None):
        """
        Mark a resume attempt as completed.
        
        Args:
            host: Cluster host
            port: Cluster port  
            cluster_name: Cluster name
            success: Whether the resume was successful
            error_message: Error message if failed
        """
        cluster_key = self._get_cluster_key(host, port, cluster_name)
        current_time = time.time()
        state = self._get_state()
        
        if self._is_fallback_mode:
            active_resumes = state.get('active_resumes', {})
            
            if cluster_key in active_resumes:
                attempt = active_resumes[cluster_key]
                if attempt['worker_id'] == self._worker_id:
                    attempt['status'] = 'completed' if success else 'failed'
                    attempt['result'] = success
                    attempt['completion_time'] = current_time
                    if error_message:
                        attempt['error'] = error_message
                    
                    # Add to history
                    resume_history = state.get('resume_history', {})
                    if cluster_key not in resume_history:
                        resume_history[cluster_key] = []
                    resume_history[cluster_key].append(dict(attempt))
                    
                    _logger.info(f"Worker {self._worker_id} completed resume for {cluster_key}: {'success' if success else 'failed'}")
            
        else:
            try:
                global_lock = state.get('global_lock')
                if global_lock and global_lock.acquire(timeout=10.0):
                    try:
                        active_resumes = state.get('active_resumes', {})
                        
                        if cluster_key in active_resumes:
                            attempt_data = active_resumes[cluster_key]
                            if attempt_data.get('worker_id') == self._worker_id:
                                # Update the attempt
                                attempt_data['status'] = 'completed' if success else 'failed'
                                attempt_data['result'] = success
                                attempt_data['completion_time'] = current_time
                                if error_message:
                                    attempt_data['error'] = error_message
                                
                                active_resumes[cluster_key] = attempt_data
                                
                                _logger.info(f"Worker {self._worker_id} completed resume for {cluster_key}: {'success' if success else 'failed'}")
                        
                    finally:
                        global_lock.release()
                        
            except Exception as e:
                _logger.error(f"Error completing resume attempt: {e}")
    
    def get_resume_status(self, host: str, port: int, cluster_name: str) -> Optional[Dict[str, Any]]:
        """Get the current resume status for a cluster."""
        cluster_key = self._get_cluster_key(host, port, cluster_name)
        state = self._get_state()
        
        if self._is_fallback_mode:
            active_resumes = state.get('active_resumes', {})
            return active_resumes.get(cluster_key)
        else:
            try:
                global_lock = state.get('global_lock')
                if global_lock and global_lock.acquire(timeout=5.0):
                    try:
                        active_resumes = state.get('active_resumes', {})
                        return active_resumes.get(cluster_key)
                    finally:
                        global_lock.release()
            except Exception as e:
                _logger.error(f"Error getting resume status: {e}")
                return None
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about resume coordinator state."""
        state = self._get_state()
        current_time = time.time()
        
        if self._is_fallback_mode:
            active_resumes = state.get('active_resumes', {})
            resume_history = state.get('resume_history', {})
            
            return {
                'worker_id': self._worker_id,
                'is_fallback_mode': True,
                'active_resume_count': len(active_resumes),
                'total_clusters_in_history': len(resume_history),
                'current_time': current_time,
                'last_cleanup': state.get('last_cleanup', 0)
            }
        else:
            try:
                global_lock = state.get('global_lock')
                if global_lock and global_lock.acquire(timeout=2.0):
                    try:
                        active_resumes = state.get('active_resumes', {})
                        return {
                            'worker_id': self._worker_id,
                            'is_fallback_mode': False,
                            'active_resume_count': len(active_resumes) if active_resumes else 0,
                            'current_time': current_time,
                            'last_cleanup': state.get('last_cleanup', 0)
                        }
                    finally:
                        global_lock.release()
                else:
                    return {
                        'worker_id': self._worker_id,
                        'is_fallback_mode': False,
                        'error': 'Failed to acquire lock for debug info',
                        'current_time': current_time
                    }
            except Exception as e:
                return {
                    'worker_id': self._worker_id,
                    'is_fallback_mode': False,
                    'error': str(e),
                    'current_time': current_time
                }


# Global instance
_resume_coordinator = ProcessSafeResumeCoordinator()


def get_resume_coordinator() -> ProcessSafeResumeCoordinator:
    """Get the global resume coordinator instance."""
    return _resume_coordinator