"""
Performance Monitoring Module

This module provides performance tracking and optimization utilities
for Datatrack operations, helping identify bottlenecks and measure
the effectiveness of performance improvements.

Features:
- Execution time measurement and reporting
- Memory usage tracking for large schema operations
- Performance metrics collection and analysis
- Optimization recommendations based on usage patterns

Author: Navaneet
"""

import functools
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List


@dataclass
class PerformanceMetrics:
    """Performance metrics for database operations"""

    operation_name: str
    start_time: float
    end_time: float
    duration: float
    table_count: int
    parallel_enabled: bool
    max_workers: int
    batch_size: int
    memory_usage_mb: float = 0.0

    @property
    def tables_per_second(self) -> float:
        """Calculate tables processed per second"""
        if self.duration > 0:
            return self.table_count / self.duration
        return 0.0


class PerformanceMonitor:
    """Monitor and track performance metrics for Datatrack operations"""

    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.history_file = Path(".databases/performance_history.json")

    def start_operation(self, operation_name: str, **kwargs) -> str:
        """Start timing an operation"""
        operation_id = f"{operation_name}_{int(time.time())}"
        return operation_id

    def end_operation(self, operation_id: str, **metrics_data) -> PerformanceMetrics:
        """End timing an operation and record metrics"""
        # This would be implemented with actual timing logic
        pass

    def get_recommendations(self, metrics: PerformanceMetrics) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        if metrics.table_count > 100 and not metrics.parallel_enabled:
            recommendations.append(
                "Consider enabling parallel processing (--parallel) for large schemas"
            )

        if metrics.max_workers < 4:
            recommendations.append(
                f"Consider increasing max workers (currently {metrics.max_workers})"
            )

        if metrics.table_count > 1000 and metrics.batch_size == 100:
            recommendations.append(
                "Consider increasing batch size (--batch-size) for very large schemas"
            )

        if metrics.duration > 60:
            recommendations.append(
                "For frequent snapshots, consider using incremental tracking"
            )

        return recommendations

    def save_metrics(self, metrics: PerformanceMetrics):
        """Save performance metrics to history file"""
        if not self.history_file.parent.exists():
            self.history_file.parent.mkdir(parents=True, exist_ok=True)

        history = []
        if self.history_file.exists():
            with open(self.history_file) as f:
                history = json.load(f)

        metrics_dict = {
            "operation_name": metrics.operation_name,
            "timestamp": metrics.start_time,
            "duration": metrics.duration,
            "table_count": metrics.table_count,
            "tables_per_second": metrics.tables_per_second,
            "parallel_enabled": metrics.parallel_enabled,
            "max_workers": metrics.max_workers,
            "batch_size": metrics.batch_size,
            "memory_usage_mb": metrics.memory_usage_mb,
        }

        history.append(metrics_dict)

        # Keep only the last 100 entries
        if len(history) > 100:
            history = history[-100:]

        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=2)


def performance_timer(operation_name: str):
    """Decorator to time function execution and collect performance metrics"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time

                # Extract relevant metrics from function arguments
                table_count = kwargs.get("table_count", 0)
                parallel = kwargs.get("parallel", False)
                max_workers = kwargs.get("max_workers", 1)
                batch_size = kwargs.get("batch_size", 100)

                metrics = PerformanceMetrics(
                    operation_name=operation_name,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    table_count=table_count,
                    parallel_enabled=parallel,
                    max_workers=max_workers,
                    batch_size=batch_size,
                )

                # Print performance summary
                print("\n📊 Performance Summary:")
                print(f"   Operation: {operation_name}")
                print(f"   Duration: {duration:.2f} seconds")
                print(f"   Tables processed: {table_count}")
                print(f"   Tables/second: {metrics.tables_per_second:.2f}")
                print(
                    f"   Parallel processing: {'Enabled' if parallel else 'Disabled'}"
                )

                monitor = PerformanceMonitor()
                recommendations = monitor.get_recommendations(metrics)
                if recommendations:
                    print("\n💡 Performance Recommendations:")
                    for rec in recommendations:
                        print(f"   • {rec}")

                monitor.save_metrics(metrics)

                return result

            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                print(f"❌ Operation failed after {duration:.2f} seconds: {e}")
                raise

        return wrapper

    return decorator


def get_performance_history() -> List[Dict]:
    """Get performance history from stored metrics"""
    history_file = Path(".databases/performance_history.json")
    if history_file.exists():
        with open(history_file) as f:
            return json.load(f)
    return []


def analyze_performance_trends() -> dict:
    """Analyze performance trends over time"""
    history = get_performance_history()
    if not history:
        return {"message": "No performance history available"}

    # Calculate averages and trends
    recent_operations = history[-10:]  # Last 10 operations

    avg_duration = sum(op["duration"] for op in recent_operations) / len(
        recent_operations
    )
    avg_tables_per_second = sum(
        op["tables_per_second"] for op in recent_operations
    ) / len(recent_operations)

    parallel_usage = sum(1 for op in recent_operations if op["parallel_enabled"]) / len(
        recent_operations
    )

    return {
        "total_operations": len(history),
        "recent_avg_duration": avg_duration,
        "recent_avg_tables_per_second": avg_tables_per_second,
        "parallel_usage_percentage": parallel_usage * 100,
        "recommendations": [
            (
                "Enable parallel processing more often"
                if parallel_usage < 0.5
                else "Good parallel processing usage"
            ),
            (
                "Consider optimizing for speed"
                if avg_tables_per_second < 10
                else "Good processing speed"
            ),
        ],
    }
