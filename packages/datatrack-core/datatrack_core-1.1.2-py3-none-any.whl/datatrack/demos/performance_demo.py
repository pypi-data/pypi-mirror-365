#!/usr/bin/env python3
"""
Performance Demonstration Script

This script demonstrates the performance improvements implemented in Datatrack,
showing the difference between sequential and parallel processing for database
schema introspection.
"""

import time
from unittest.mock import MagicMock, patch

from datatrack.tracker import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_MAX_WORKERS,
    introspect_tables_paginated,
    introspect_tables_parallel,
)


def simulate_database_latency(inspector, table_name, schema_name=None):
    """Simulate database introspection with realistic latency"""
    # Simulate network/database latency (5ms per table)
    time.sleep(0.005)

    return {
        "name": table_name,
        "schema": schema_name,
        "columns": [
            {
                "name": "id",
                "type": "INTEGER",
                "nullable": False,
                "primary_key": True,
                "autoincrement": True,
                "default": None,
                "comment": None,
            },
            {
                "name": "name",
                "type": "VARCHAR(255)",
                "nullable": False,
                "primary_key": False,
                "autoincrement": False,
                "default": None,
                "comment": None,
            },
            {
                "name": "created_at",
                "type": "TIMESTAMP",
                "nullable": False,
                "primary_key": False,
                "autoincrement": False,
                "default": "CURRENT_TIMESTAMP",
                "comment": None,
            },
        ],
        "indexes": [
            {
                "name": f"idx_{table_name}_name",
                "columns": ["name"],
                "unique": False,
                "type": "btree",
                "dialect_options": {},
            }
        ],
        "foreign_keys": [],
        "constraints": [],
        "triggers": [],
    }


def benchmark_sequential_processing(table_names):
    """Benchmark sequential table processing"""
    mock_inspector = MagicMock()

    print(f"🔄 Processing {len(table_names)} tables sequentially...")
    start_time = time.time()

    with patch(
        "datatrack.tracker.introspect_single_table",
        side_effect=simulate_database_latency,
    ):
        results = []
        for table_name in table_names:
            result = simulate_database_latency(mock_inspector, table_name)
            results.append(result)

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"✅ Sequential processing completed in {elapsed:.3f} seconds")
    print(f"   Average time per table: {elapsed/len(table_names):.3f} seconds")

    return elapsed, results


def benchmark_parallel_processing(table_names, max_workers=DEFAULT_MAX_WORKERS):
    """Benchmark parallel table processing"""
    mock_inspector = MagicMock()

    print(
        f"⚡ Processing {len(table_names)} tables in parallel (workers: {max_workers})..."
    )
    start_time = time.time()

    with patch(
        "datatrack.tracker.introspect_single_table",
        side_effect=simulate_database_latency,
    ):
        results = introspect_tables_parallel(
            mock_inspector, table_names, max_workers=max_workers
        )

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"✅ Parallel processing completed in {elapsed:.3f} seconds")
    print(f"   Average time per table: {elapsed/len(table_names):.3f} seconds")

    return elapsed, results


def benchmark_batched_processing(table_names, batch_size=DEFAULT_BATCH_SIZE):
    """Benchmark batched table processing for memory efficiency"""
    mock_inspector = MagicMock()

    print(
        f"📦 Processing {len(table_names)} tables in batches (batch size: {batch_size})..."
    )
    start_time = time.time()

    with patch(
        "datatrack.tracker.introspect_single_table",
        side_effect=simulate_database_latency,
    ):
        results = []
        for batch in introspect_tables_paginated(
            mock_inspector, table_names, batch_size=batch_size
        ):
            results.extend(batch)

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"✅ Batched processing completed in {elapsed:.3f} seconds")
    print(f"   Average time per table: {elapsed/len(table_names):.3f} seconds")

    return elapsed, results


def main():
    """Run performance benchmarks and display results"""
    print("🚀 Datatrack Performance Optimization Demo")
    print("=" * 50)

    # Test with different schema sizes
    test_cases = [
        ("Small Schema", 10),
        ("Medium Schema", 25),
        ("Large Schema", 50),
    ]

    for case_name, table_count in test_cases:
        print(f"\n📊 {case_name} ({table_count} tables)")
        print("-" * 40)

        # Generate table names
        table_names = [f"table_{i:03d}" for i in range(table_count)]

        # Benchmark sequential processing
        seq_time, seq_results = benchmark_sequential_processing(table_names)

        # Benchmark parallel processing
        par_time, par_results = benchmark_parallel_processing(
            table_names, max_workers=4
        )

        # Benchmark batched processing
        batch_time, batch_results = benchmark_batched_processing(
            table_names, batch_size=10
        )

        # Calculate improvements
        seq_speedup = ((seq_time - par_time) / seq_time) * 100
        batch_speedup = ((seq_time - batch_time) / seq_time) * 100

        print("\n📈 Performance Summary:")
        print(f"   Sequential: {seq_time:.3f}s (baseline)")
        print(f"   Parallel:   {par_time:.3f}s ({seq_speedup:+.1f}% change)")
        print(f"   Batched:    {batch_time:.3f}s ({batch_speedup:+.1f}% change)")

        # Verify all methods produce same number of results
        assert len(seq_results) == len(par_results) == len(batch_results) == table_count

        print(f"✅ All methods processed {table_count} tables correctly")

    print("\n🎯 Performance Optimization Features:")
    print("   ✅ Parallel processing for large schemas (>5 tables)")
    print("   ✅ Sequential processing for small schemas (≤5 tables)")
    print("   ✅ Batched processing for memory efficiency")
    print("   ✅ Configurable worker count and batch size")
    print("   ✅ Error handling in parallel environments")
    print("   ✅ Automatic processing strategy selection")

    print("\n💡 CLI Usage Examples:")
    print("   # Use parallel processing (default)")
    print("   datatrack snapshot --parallel")
    print("   ")
    print("   # Use sequential processing")
    print("   datatrack snapshot --no-parallel")
    print("   ")
    print("   # Configure workers and batch size")
    print("   datatrack snapshot --max-workers 8 --batch-size 50")


if __name__ == "__main__":
    main()
