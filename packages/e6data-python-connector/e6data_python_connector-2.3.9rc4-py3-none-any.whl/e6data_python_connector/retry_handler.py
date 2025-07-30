"""
Robust error handling and retry logic for high-concurrency environments.

This module provides comprehensive retry mechanisms for gRPC operations,
authentication failures, and cluster resume operations.
"""

import logging
import time
import random
from typing import Optional, Callable, Any, List, Type
from functools import wraps
from dataclasses import dataclass

import grpc
from grpc._channel import _InactiveRpcError

# Set up logging
_logger = logging.getLogger(__name__)

# Configuration constants
MAX_RETRY_ATTEMPTS = 5
BASE_RETRY_DELAY = 0.5  # 500ms base delay
MAX_RETRY_DELAY = 30.0  # 30 seconds maximum delay
JITTER_FACTOR = 0.1  # 10% jitter to avoid thundering herd


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = MAX_RETRY_ATTEMPTS
    base_delay: float = BASE_RETRY_DELAY
    max_delay: float = MAX_RETRY_DELAY
    jitter_factor: float = JITTER_FACTOR
    exponential_backoff: bool = True
    retryable_status_codes: List[grpc.StatusCode] = None
    retryable_error_messages: List[str] = None
    
    def __post_init__(self):
        if self.retryable_status_codes is None:
            self.retryable_status_codes = [
                grpc.StatusCode.UNAVAILABLE,
                grpc.StatusCode.RESOURCE_EXHAUSTED,
                grpc.StatusCode.ABORTED,
                grpc.StatusCode.INTERNAL,
                grpc.StatusCode.UNKNOWN  # For 456 errors
            ]
        
        if self.retryable_error_messages is None:
            self.retryable_error_messages = [
                'status: 503',  # Service unavailable
                'status: 456',  # Strategy mismatch
                'connection reset',
                'connection refused',
                'timeout',
                'deadline exceeded',
                'temporary failure'
            ]


class RetryHandler:
    """
    Handles retry logic for various operations with configurable policies.
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number."""
        if self.config.exponential_backoff:
            # Exponential backoff: base_delay * 2^attempt
            delay = self.config.base_delay * (2 ** attempt)
        else:
            # Linear backoff: base_delay * attempt
            delay = self.config.base_delay * attempt
        
        # Cap at maximum delay
        delay = min(delay, self.config.max_delay)
        
        # Add jitter to avoid thundering herd
        jitter = delay * self.config.jitter_factor * random.random()
        delay += jitter
        
        return delay
    
    def is_retryable_error(self, error: Exception) -> bool:
        """Check if an error is retryable based on configuration."""
        if isinstance(error, _InactiveRpcError):
            # Check status code
            if error.code() in self.config.retryable_status_codes:
                return True
            
            # Check error message
            error_details = error.details().lower()
            for message in self.config.retryable_error_messages:
                if message.lower() in error_details:
                    return True
        
        # Check for specific non-gRPC errors
        error_str = str(error).lower()
        for message in self.config.retryable_error_messages:
            if message.lower() in error_str:
                return True
        
        return False
    
    def should_stop_retry(self, error: Exception) -> bool:
        """Check if we should stop retrying based on the error type."""
        if isinstance(error, _InactiveRpcError):
            # Don't retry authentication errors
            if error.code() == grpc.StatusCode.UNAUTHENTICATED:
                return True
            
            # Don't retry permission errors
            if error.code() == grpc.StatusCode.PERMISSION_DENIED:
                return True
            
            # Check for credential-related errors in details
            error_details = error.details().lower()
            if any(phrase in error_details for phrase in ['invalid credentials', 'access denied', 'unauthorized']):
                return True
        
        return False
    
    def execute_with_retry(self, 
                          operation: Callable[[], Any], 
                          operation_name: str = "operation") -> Any:
        """
        Execute an operation with retry logic.
        
        Args:
            operation: The operation to execute
            operation_name: Name for logging purposes
            
        Returns:
            Result of the operation
            
        Raises:
            The last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                result = operation()
                if attempt > 0:
                    _logger.info(f"{operation_name} succeeded on attempt {attempt + 1}")
                return result
                
            except Exception as e:
                last_exception = e
                
                # Check if we should stop retrying
                if self.should_stop_retry(e):
                    _logger.error(f"{operation_name} failed with non-retryable error: {e}")
                    raise e
                
                # Check if this is a retryable error
                if not self.is_retryable_error(e):
                    _logger.error(f"{operation_name} failed with non-retryable error: {e}")
                    raise e
                
                # Don't retry on the last attempt
                if attempt == self.config.max_attempts - 1:
                    break
                
                # Calculate delay and wait
                delay = self.calculate_delay(attempt)
                _logger.warning(f"{operation_name} attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                time.sleep(delay)
        
        # All retries exhausted
        _logger.error(f"{operation_name} failed after {self.config.max_attempts} attempts. Last error: {last_exception}")
        raise last_exception


def with_retry(config: Optional[RetryConfig] = None, operation_name: Optional[str] = None):
    """
    Decorator to add retry logic to a function.
    
    Args:
        config: Retry configuration
        operation_name: Name for logging (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_handler = RetryHandler(config)
            name = operation_name or func.__name__
            
            def operation():
                return func(*args, **kwargs)
            
            return retry_handler.execute_with_retry(operation, name)
        
        return wrapper
    return decorator


# Predefined retry configs for common scenarios
AUTHENTICATION_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=0.5,
    max_delay=5.0,
    retryable_status_codes=[
        grpc.StatusCode.UNAVAILABLE,
        grpc.StatusCode.RESOURCE_EXHAUSTED,
        grpc.StatusCode.UNKNOWN  # For 456 errors
    ],
    retryable_error_messages=['status: 456', 'connection reset', 'timeout']
)

CLUSTER_RESUME_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=2.0,
    max_delay=15.0,
    retryable_status_codes=[
        grpc.StatusCode.UNAVAILABLE,
        grpc.StatusCode.RESOURCE_EXHAUSTED,
        grpc.StatusCode.ABORTED
    ],
    retryable_error_messages=['status: 503', 'connection reset', 'timeout', 'temporary failure']
)

QUERY_EXECUTION_RETRY_CONFIG = RetryConfig(
    max_attempts=2,  # Conservative for queries
    base_delay=1.0,
    max_delay=10.0,
    retryable_status_codes=[
        grpc.StatusCode.UNAVAILABLE,
        grpc.StatusCode.UNKNOWN  # For 456 errors
    ],
    retryable_error_messages=['status: 456', 'connection reset']
)

LOCK_ACQUISITION_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    base_delay=0.1,
    max_delay=2.0,
    exponential_backoff=True,
    retryable_error_messages=['timeout', 'lock contention', 'failed to acquire']
)


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for failing fast when errors persist.
    """
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 expected_exception: Type[Exception] = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker."""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful operation."""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'


# Global circuit breakers for different operations
_authentication_circuit_breaker = CircuitBreaker(
    failure_threshold=10,
    recovery_timeout=120.0,
    expected_exception=_InactiveRpcError
)

_cluster_resume_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=300.0,  # 5 minutes
    expected_exception=Exception
)


def with_circuit_breaker(circuit_breaker: CircuitBreaker):
    """Decorator to add circuit breaker protection to a function."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return circuit_breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator


# High-level retry functions with circuit breaker protection
@with_circuit_breaker(_authentication_circuit_breaker)
@with_retry(AUTHENTICATION_RETRY_CONFIG, "authentication")
def retry_authentication(auth_func: Callable) -> Any:
    """Retry authentication with circuit breaker protection."""
    return auth_func()


@with_circuit_breaker(_cluster_resume_circuit_breaker)
@with_retry(CLUSTER_RESUME_RETRY_CONFIG, "cluster_resume")
def retry_cluster_resume(resume_func: Callable) -> Any:
    """Retry cluster resume with circuit breaker protection."""
    return resume_func()


@with_retry(QUERY_EXECUTION_RETRY_CONFIG, "query_execution")
def retry_query_execution(query_func: Callable) -> Any:
    """Retry query execution with limited retries."""
    return query_func()


def get_retry_handler(operation_type: str) -> RetryHandler:
    """Get a configured retry handler for specific operation types."""
    configs = {
        'authentication': AUTHENTICATION_RETRY_CONFIG,
        'cluster_resume': CLUSTER_RESUME_RETRY_CONFIG,
        'query_execution': QUERY_EXECUTION_RETRY_CONFIG,
        'lock_acquisition': LOCK_ACQUISITION_RETRY_CONFIG
    }
    
    config = configs.get(operation_type, RetryConfig())
    return RetryHandler(config)