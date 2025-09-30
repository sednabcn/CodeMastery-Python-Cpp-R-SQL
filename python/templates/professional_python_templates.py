"""
Module Name: Professional Python Template

This module provides a comprehensive template for professional Python development
including context managers, unit testing, logging, type hints, and proper documentation.

Author: Your Name
Created: 2025-09-30
Version: 1.0.0
"""

# Standard library imports
import logging
import sys
import threading
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generator,
    Generic,
    Iterable,
    List,
    Literal,
    Optional,
    Protocol,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

# Third-party imports (if any)
# import numpy as np
# import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Type variables
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
NumericType = TypeVar('NumericType', int, float)


# ============================================================================
# CONTEXT MANAGERS
# ============================================================================

class Timer:
    """
    Context manager for timing code execution.
    
    This context manager measures and logs the execution time of code blocks.
    
    Attributes:
        name: Name of the operation being timed
        start_time: Timestamp when context was entered
        
    Example:
        >>> with Timer("data processing"):
        ...     # Your code here
        ...     process_data()
    """
    
    def __init__(self, name: str = "Operation") -> None:
        """
        Initialize the Timer context manager.
        
        Args:
            name: Description of the operation being timed
        """
        self.name = name
        self.start_time: Optional[float] = None
        
    def __enter__(self) -> 'Timer':
        """Enter the context manager and start timing."""
        self.start_time = time.time()
        logger.info(f"Starting: {self.name}")
        return self
        
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any]
    ) -> bool:
        """
        Exit the context manager and log elapsed time.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
            
        Returns:
            False to propagate any exception that occurred
        """
        elapsed = time.time() - (self.start_time or 0)
        logger.info(f"Completed: {self.name} in {elapsed:.2f} seconds")
        return False


class DatabaseConnection:
    """
    Context manager for database connections.
    
    This context manager ensures proper connection handling with automatic
    commit/rollback and connection cleanup.
    
    Attributes:
        connection_string: Database connection string
        connection: Active database connection
        
    Example:
        >>> with DatabaseConnection("postgresql://...") as conn:
        ...     conn.execute("SELECT * FROM users")
    """
    
    def __init__(self, connection_string: str) -> None:
        """
        Initialize the database connection manager.
        
        Args:
            connection_string: Database connection URL
        """
        self.connection_string = connection_string
        self.connection: Optional[Any] = None
        
    def __enter__(self) -> 'DatabaseConnection':
        """Establish database connection."""
        logger.info(f"Connecting to database: {self.connection_string}")
        # self.connection = actual_db_connection()
        return self
        
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any]
    ) -> bool:
        """
        Close database connection with proper cleanup.
        
        Commits transaction on success, rolls back on error.
        """
        if exc_type is not None:
            logger.error(f"Database error: {exc_val}")
            # self.connection.rollback()
        else:
            logger.info("Committing transaction")
            # self.connection.commit()
            
        if self.connection:
            # self.connection.close()
            logger.info("Database connection closed")
        return False


@contextmanager
def managed_resource(resource_name: str) -> Generator[Dict[str, Any], None, None]:
    """
    Function-based context manager for resource management.
    
    This is a generator-based context manager that can be used with @contextmanager
    decorator for simpler context manager creation.
    
    Args:
        resource_name: Name of the resource being managed
        
    Yields:
        Dictionary containing the managed resource
        
    Example:
        >>> with managed_resource("file_handle") as resource:
        ...     resource['data'] = "some data"
    """
    logger.info(f"Acquiring resource: {resource_name}")
    resource: Dict[str, Any] = {"name": resource_name, "active": True}
    try:
        yield resource
    except Exception as e:
        logger.error(f"Error with resource {resource_name}: {e}")
        raise
    finally:
        resource["active"] = False
        logger.info(f"Released resource: {resource_name}")


# ============================================================================
# THREAD-SAFE CLASSES
# ============================================================================

class ThreadSafeCounter:
    """
    Thread-safe counter implementation.
    
    This class provides a counter that can be safely incremented and decremented
    from multiple threads simultaneously.
    
    Attributes:
        _value: Current counter value
        _lock: Threading lock for synchronization
        
    Example:
        >>> counter = ThreadSafeCounter()
        >>> counter.increment()
        >>> print(counter.value)
        1
    """
    
    def __init__(self, initial_value: int = 0) -> None:
        """
        Initialize the thread-safe counter.
        
        Args:
            initial_value: Starting value for the counter
        """
        self._value: int = initial_value
        self._lock: threading.Lock = threading.Lock()
        logger.debug(f"ThreadSafeCounter initialized with value: {initial_value}")
        
    def increment(self, amount: int = 1) -> int:
        """
        Increment the counter in a thread-safe manner.
        
        Args:
            amount: Amount to increment by
            
        Returns:
            New counter value after increment
        """
        with self._lock:
            self._value += amount
            logger.debug(f"Counter incremented to: {self._value}")
            return self._value
            
    def decrement(self, amount: int = 1) -> int:
        """
        Decrement the counter in a thread-safe manner.
        
        Args:
            amount: Amount to decrement by
            
        Returns:
            New counter value after decrement
        """
        with self._lock:
            self._value -= amount
            logger.debug(f"Counter decremented to: {self._value}")
            return self._value
            
    @property
    def value(self) -> int:
        """
        Get current counter value in a thread-safe manner.
        
        Returns:
            Current counter value
        """
        with self._lock:
            return self._value


# ============================================================================
# GENERIC CLASSES AND FUNCTIONS
# ============================================================================

class DataProcessor(Generic[T]):
    """
    Generic data processor that works with any type.
    
    This class demonstrates the use of generics for type-safe data processing
    that works with different data types.
    
    Type Parameters:
        T: Type of data being processed
        
    Attributes:
        data: List of items to process
        
    Example:
        >>> processor = DataProcessor[int]([1, 2, 3, 4, 5])
        >>> result = processor.filter(lambda x: x > 2)
    """
    
    def __init__(self, data: List[T]) -> None:
        """
        Initialize the data processor.
        
        Args:
            data: List of items to process
        """
        self.data: List[T] = data
        logger.info(f"DataProcessor initialized with {len(data)} items")
        
    def filter(self, predicate: Callable[[T], bool]) -> List[T]:
        """
        Filter data using a predicate function.
        
        Args:
            predicate: Function that returns True for items to keep
            
        Returns:
            Filtered list of items
        """
        result = [item for item in self.data if predicate(item)]
        logger.debug(f"Filtered {len(self.data)} items to {len(result)} items")
        return result
        
    def transform(self, func: Callable[[T], K]) -> List[K]:
        """
        Transform data using a mapping function.
        
        Args:
            func: Function to apply to each item
            
        Returns:
            List of transformed items
        """
        result = [func(item) for item in self.data]
        logger.debug(f"Transformed {len(self.data)} items")
        return result


def process_items(
    items: Sequence[T],
    processor: Callable[[T], K],
    *,
    parallel: bool = False,
    max_workers: Optional[int] = None
) -> List[K]:
    """
    Process a sequence of items using a given processor function.
    
    This function demonstrates proper type hints, keyword-only arguments,
    and comprehensive documentation.
    
    Args:
        items: Sequence of items to process
        processor: Function to apply to each item
        parallel: Whether to process items in parallel
        max_workers: Maximum number of worker threads (if parallel=True)
        
    Returns:
        List of processed items
        
    Raises:
        ValueError: If max_workers is negative
        TypeError: If processor is not callable
        
    Example:
        >>> items = [1, 2, 3, 4, 5]
        >>> result = process_items(items, lambda x: x * 2)
        >>> print(result)
        [2, 4, 6, 8, 10]
    """
    if not callable(processor):
        raise TypeError("processor must be callable")
        
    if max_workers is not None and max_workers < 0:
        raise ValueError("max_workers must be non-negative")
        
    logger.info(f"Processing {len(items)} items (parallel={parallel})")
    
    with Timer("Item processing"):
        if parallel:
            # Parallel processing logic here
            logger.info(f"Using parallel processing with {max_workers} workers")
            result = [processor(item) for item in items]
        else:
            result = [processor(item) for item in items]
            
    return result


@overload
def get_value(data: Dict[K, V], key: K) -> V: ...

@overload
def get_value(data: Dict[K, V], key: K, default: T) -> Union[V, T]: ...

def get_value(
    data: Dict[K, V],
    key: K,
    default: Optional[T] = None
) -> Union[V, T, None]:
    """
    Get value from dictionary with optional default.
    
    This function demonstrates the use of @overload for more precise type hints.
    
    Args:
        data: Dictionary to get value from
        key: Key to lookup
        default: Default value if key not found
        
    Returns:
        Value from dictionary or default value
        
    Example:
        >>> data = {"name": "John", "age": 30}
        >>> name = get_value(data, "name")
        >>> city = get_value(data, "city", "Unknown")
    """
    return data.get(key, default)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main() -> None:
    """
    Main execution function.
    
    This function demonstrates the usage of all components defined above.
    """
    logger.info("=" * 70)
    logger.info("Starting application")
    logger.info("=" * 70)
    
    try:
        # Demonstrate Timer context manager
        with Timer("Main process"):
            # Demonstrate thread-safe counter
            counter = ThreadSafeCounter(0)
            for _ in range(5):
                counter.increment()
            logger.info(f"Final counter value: {counter.value}")
            
            # Demonstrate generic data processor
            processor = DataProcessor[int]([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
            even_numbers = processor.filter(lambda x: x % 2 == 0)
            logger.info(f"Even numbers: {even_numbers}")
            
            # Demonstrate managed resource
            with managed_resource("sample_resource") as resource:
                logger.info(f"Using resource: {resource['name']}")
                
        logger.info("Application completed successfully")
        
    except Exception as e:
        logger.exception(f"Application error: {e}")
        raise
    finally:
        logger.info("Cleanup completed")


if __name__ == "__main__":
    main()


# ============================================================================
# UNIT TESTS
# ============================================================================

import unittest


class TestThreadSafeCounter(unittest.TestCase):
    """Unit tests for ThreadSafeCounter class."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.counter = ThreadSafeCounter(0)
        
    def test_initial_value(self) -> None:
        """Test counter initialization with default value."""
        counter = ThreadSafeCounter()
        self.assertEqual(counter.value, 0)
        
    def test_initial_value_custom(self) -> None:
        """Test counter initialization with custom value."""
        counter = ThreadSafeCounter(10)
        self.assertEqual(counter.value, 10)
        
    def test_increment(self) -> None:
        """Test counter increment operation."""
        self.counter.increment()
        self.assertEqual(self.counter.value, 1)
        
    def test_increment_amount(self) -> None:
        """Test counter increment with custom amount."""
        self.counter.increment(5)
        self.assertEqual(self.counter.value, 5)
        
    def test_decrement(self) -> None:
        """Test counter decrement operation."""
        self.counter.increment(10)
        self.counter.decrement()
        self.assertEqual(self.counter.value, 9)
        
    def test_thread_safety(self) -> None:
        """Test counter thread safety with multiple threads."""
        def increment_many(counter: ThreadSafeCounter, times: int) -> None:
            for _ in range(times):
                counter.increment()
                
        threads = [
            threading.Thread(target=increment_many, args=(self.counter, 100))
            for _ in range(10)
        ]
        
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
            
        self.assertEqual(self.counter.value, 1000)


class TestDataProcessor(unittest.TestCase):
    """Unit tests for DataProcessor class."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.processor = DataProcessor[int]([1, 2, 3, 4, 5])
        
    def test_filter(self) -> None:
        """Test data filtering."""
        result = self.processor.filter(lambda x: x > 3)
        self.assertEqual(result, [4, 5])
        
    def test_transform(self) -> None:
        """Test data transformation."""
        result = self.processor.transform(lambda x: x * 2)
        self.assertEqual(result, [2, 4, 6, 8, 10])
        
    def test_empty_data(self) -> None:
        """Test processor with empty data."""
        processor = DataProcessor[str]([])
        result = processor.filter(lambda x: True)
        self.assertEqual(result, [])


class TestProcessItems(unittest.TestCase):
    """Unit tests for process_items function."""
    
    def test_process_items_basic(self) -> None:
        """Test basic item processing."""
        items = [1, 2, 3, 4, 5]
        result = process_items(items, lambda x: x * 2)
        self.assertEqual(result, [2, 4, 6, 8, 10])
        
    def test_process_items_invalid_processor(self) -> None:
        """Test error handling for invalid processor."""
        items = [1, 2, 3]
        with self.assertRaises(TypeError):
            process_items(items, "not_callable")  # type: ignore
            
    def test_process_items_negative_workers(self) -> None:
        """Test error handling for negative max_workers."""
        items = [1, 2, 3]
        with self.assertRaises(ValueError):
            process_items(items, lambda x: x, parallel=True, max_workers=-1)


class TestContextManagers(unittest.TestCase):
    """Unit tests for context managers."""
    
    def test_timer_context_manager(self) -> None:
        """Test Timer context manager."""
        with Timer("test") as timer:
            time.sleep(0.1)
        self.assertIsNotNone(timer.start_time)
        
    def test_managed_resource(self) -> None:
        """Test managed_resource context manager."""
        with managed_resource("test_resource") as resource:
            self.assertTrue(resource["active"])
            self.assertEqual(resource["name"], "test_resource")


# To run tests: python -m unittest this_module.py
# Or: pytest this_module.py (if pytest is installed)
