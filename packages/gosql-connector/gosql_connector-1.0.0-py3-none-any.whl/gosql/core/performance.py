"""
Performance monitoring and metrics for GoSQL.

This module provides performance monitoring capabilities including query timing,
memory usage tracking, and connection pool statistics.
"""

import time
import threading
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any
import psutil
import os


class PerformanceMonitor:
    """
    Performance monitoring class for tracking GoSQL operations.
    
    Tracks query execution times, memory usage, connection pool statistics,
    and other performance metrics.
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize performance monitor.
        
        Args:
            max_history: Maximum number of query records to keep in history
        """
        self.max_history = max_history
        self._lock = threading.Lock()
        self._reset_stats()
        
    def _reset_stats(self):
        """Reset all statistics."""
        self.query_times = deque(maxlen=self.max_history)
        self.query_count = 0
        self.total_query_time = 0.0
        self.connection_count = 0
        self.active_connections = 0
        self.pool_stats = defaultdict(int)
        self.error_count = 0
        self.last_reset_time = time.time()
        
        # Database-specific stats
        self.db_stats = defaultdict(lambda: {
            'query_count': 0,
            'total_time': 0.0,
            'error_count': 0
        })
        
        # Query type stats
        self.query_type_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'avg_time': 0.0
        })
    
    def record_query(self, query_time: float, db_type: str = 'unknown', 
                    query_type: str = 'unknown', success: bool = True):
        """
        Record a query execution.
        
        Args:
            query_time: Query execution time in seconds
            db_type: Database type (mysql, postgresql, mssql)
            query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
            success: Whether the query was successful
        """
        with self._lock:
            self.query_times.append(query_time)
            self.query_count += 1
            self.total_query_time += query_time
            
            # Database-specific stats
            self.db_stats[db_type]['query_count'] += 1
            self.db_stats[db_type]['total_time'] += query_time
            if not success:
                self.error_count += 1
                self.db_stats[db_type]['error_count'] += 1
            
            # Query type stats
            self.query_type_stats[query_type]['count'] += 1
            self.query_type_stats[query_type]['total_time'] += query_time
            self.query_type_stats[query_type]['avg_time'] = (
                self.query_type_stats[query_type]['total_time'] / 
                self.query_type_stats[query_type]['count']
            )
    
    def record_connection(self, created: bool = True):
        """
        Record connection creation or destruction.
        
        Args:
            created: True if connection was created, False if destroyed
        """
        with self._lock:
            if created:
                self.connection_count += 1
                self.active_connections += 1
            else:
                self.active_connections = max(0, self.active_connections - 1)
    
    def record_pool_event(self, event_type: str):
        """
        Record connection pool events.
        
        Args:
            event_type: Type of pool event (acquire, release, timeout, etc.)
        """
        with self._lock:
            self.pool_stats[event_type] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get current performance statistics.
        
        Returns:
            Dictionary containing performance metrics
        """
        with self._lock:
            current_time = time.time()
            elapsed_time = current_time - self.last_reset_time
            
            # Memory usage
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            stats = {
                # Basic query stats
                'query_count': self.query_count,
                'total_query_time': self.total_query_time,
                'average_query_time': (
                    self.total_query_time / self.query_count if self.query_count > 0 else 0
                ),
                'queries_per_second': self.query_count / elapsed_time if elapsed_time > 0 else 0,
                'error_count': self.error_count,
                'error_rate': self.error_count / self.query_count if self.query_count > 0 else 0,
                
                # Recent performance (last 100 queries)
                'recent_avg_time': (
                    sum(list(self.query_times)[-100:]) / min(100, len(self.query_times))
                    if self.query_times else 0
                ),
                'recent_max_time': max(list(self.query_times)[-100:]) if self.query_times else 0,
                'recent_min_time': min(list(self.query_times)[-100:]) if self.query_times else 0,
                
                # Connection stats
                'total_connections_created': self.connection_count,
                'active_connections': self.active_connections,
                
                # Pool stats
                'pool_events': dict(self.pool_stats),
                
                # Memory usage
                'memory_usage_mb': memory_info.rss / 1024 / 1024,
                'memory_usage_percent': process.memory_percent(),
                
                # System stats
                'cpu_percent': process.cpu_percent(),
                'elapsed_time': elapsed_time,
                
                # Database-specific stats
                'database_stats': dict(self.db_stats),
                
                # Query type stats
                'query_type_stats': dict(self.query_type_stats)
            }
            
            return stats
    
    def get_percentiles(self, percentiles: List[float] = [50, 90, 95, 99]) -> Dict[float, float]:
        """
        Get query time percentiles.
        
        Args:
            percentiles: List of percentiles to calculate
            
        Returns:
            Dictionary mapping percentile to time in seconds
        """
        with self._lock:
            if not self.query_times:
                return {p: 0.0 for p in percentiles}
            
            sorted_times = sorted(self.query_times)
            result = {}
            
            for p in percentiles:
                index = int((p / 100.0) * len(sorted_times))
                index = min(index, len(sorted_times) - 1)
                result[p] = sorted_times[index]
            
            return result
    
    def reset(self):
        """Reset all statistics."""
        with self._lock:
            self._reset_stats()
    
    def print_summary(self):
        """Print a formatted summary of performance statistics."""
        stats = self.get_stats()
        percentiles = self.get_percentiles()
        
        print("=" * 80)
        print("GoSQL Performance Summary")
        print("=" * 80)
        
        print(f"Total Queries: {stats['query_count']:,}")
        print(f"Total Query Time: {stats['total_query_time']:.3f}s")
        print(f"Average Query Time: {stats['average_query_time']*1000:.2f}ms")
        print(f"Queries Per Second: {stats['queries_per_second']:.1f}")
        print(f"Error Rate: {stats['error_rate']*100:.2f}%")
        
        print("\nQuery Time Percentiles:")
        for p, time_val in percentiles.items():
            print(f"  P{p}: {time_val*1000:.2f}ms")
        
        print(f"\nConnections:")
        print(f"  Created: {stats['total_connections_created']}")
        print(f"  Active: {stats['active_connections']}")
        
        print(f"\nMemory Usage:")
        print(f"  RSS: {stats['memory_usage_mb']:.1f} MB")
        print(f"  Percent: {stats['memory_usage_percent']:.1f}%")
        
        if stats['database_stats']:
            print("\nDatabase Stats:")
            for db, db_stats in stats['database_stats'].items():
                print(f"  {db}: {db_stats['query_count']} queries, "
                      f"{db_stats['total_time']:.3f}s total")
        
        print("=" * 80)


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


class QueryTimer:
    """Context manager for timing queries."""
    
    def __init__(self, monitor: PerformanceMonitor, db_type: str = 'unknown', 
                 query_type: str = 'unknown'):
        self.monitor = monitor
        self.db_type = db_type
        self.query_type = query_type
        self.start_time = None
        self.success = True
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            query_time = time.time() - self.start_time
            self.success = exc_type is None
            self.monitor.record_query(
                query_time, self.db_type, self.query_type, self.success
            )


def time_query(monitor: PerformanceMonitor = None, db_type: str = 'unknown', 
               query_type: str = 'unknown'):
    """
    Decorator for timing queries.
    
    Args:
        monitor: Performance monitor instance
        db_type: Database type
        query_type: Query type
    """
    if monitor is None:
        monitor = performance_monitor
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            with QueryTimer(monitor, db_type, query_type):
                return func(*args, **kwargs)
        return wrapper
    return decorator
