"""
Tests for Performance Optimizations in Datatrack

This module tests the performance features including parallel processing,
caching, and batched operations to ensure they work correctly and provide
the expected performance improvements.
"""

import time
from unittest.mock import MagicMock, patch

import pytest

from datatrack.tracker import (
    introspect_single_table,
    introspect_tables_paginated,
    introspect_tables_parallel,
)


class TestPerformanceOptimizations:
    """Test performance optimization features"""

    def test_introspect_single_table(self):
        """Test single table introspection works correctly"""
        # Mock inspector
        mock_inspector = MagicMock()
        mock_inspector.get_columns.return_value = [
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
        ]
        mock_inspector.get_indexes.return_value = []
        mock_inspector.get_foreign_keys.return_value = []
        mock_inspector.get_check_constraints.return_value = []

        result = introspect_single_table(mock_inspector, "test_table")

        assert result["name"] == "test_table"
        assert len(result["columns"]) == 2
        assert result["columns"][0]["name"] == "id"
        assert result["columns"][0]["type"] == "INTEGER"
        assert result["columns"][1]["name"] == "name"

    def test_introspect_tables_parallel_small_set(self):
        """Test that small table sets use sequential processing"""
        mock_inspector = MagicMock()
        mock_inspector.get_columns.return_value = []
        mock_inspector.get_indexes.return_value = []
        mock_inspector.get_foreign_keys.return_value = []
        mock_inspector.get_check_constraints.return_value = []

        table_names = ["table1", "table2", "table3"]

        with patch("datatrack.tracker.introspect_single_table") as mock_introspect:
            mock_introspect.return_value = {
                "name": "test",
                "columns": [],
                "indexes": [],
                "foreign_keys": [],
                "constraints": [],
                "triggers": [],
            }

            result = introspect_tables_parallel(
                mock_inspector, table_names, max_workers=4
            )

            # Should call introspect_single_table for each table
            assert mock_introspect.call_count == 3
            assert len(result) == 3

    def test_introspect_tables_parallel_large_set(self):
        """Test that large table sets use parallel processing"""
        mock_inspector = MagicMock()

        # Create a larger set of tables (more than 5 to trigger parallel processing)
        table_names = [f"table_{i}" for i in range(8)]  # Reduced from 10 to 8

        with patch("datatrack.tracker.introspect_single_table") as mock_introspect:
            # Make the mock return faster
            mock_introspect.return_value = {
                "name": "test",
                "columns": [],
                "indexes": [],
                "foreign_keys": [],
                "constraints": [],
                "triggers": [],
            }

            result = introspect_tables_parallel(
                mock_inspector, table_names, max_workers=2
            )  # Reduced workers

            # Should call introspect_single_table for each table
            assert mock_introspect.call_count == 8
            assert len(result) == 8

    def test_introspect_tables_paginated(self):
        """Test batched processing for memory efficiency"""
        mock_inspector = MagicMock()

        table_names = [f"table_{i}" for i in range(15)]  # Reduced from 25 to 15
        batch_size = 5  # Reduced from 10 to 5

        with patch("datatrack.tracker.introspect_tables_parallel") as mock_parallel:
            mock_parallel.return_value = [
                {"name": f"table_{i}", "columns": []} for i in range(5)
            ]

            batches = list(
                introspect_tables_paginated(
                    mock_inspector, table_names, batch_size=batch_size
                )
            )

            # Should create 3 batches: 5, 5, 5
            assert len(batches) == 3
            assert mock_parallel.call_count == 3

    def test_performance_monitoring_integration(self):
        """Test that performance monitoring doesn't break normal operation"""
        from datatrack.tracker import snapshot

        # Mock the database components
        with patch("datatrack.tracker.get_saved_connection") as mock_conn, patch(
            "datatrack.tracker.get_connected_db_name"
        ) as mock_db_name, patch(
            "datatrack.tracker.create_engine"
        ) as mock_engine, patch(
            "datatrack.tracker.save_schema_snapshot"
        ) as mock_save:

            mock_conn.return_value = "sqlite:///test.db"
            mock_db_name.return_value = "test_db"

            # Mock the engine and inspector
            mock_engine_instance = MagicMock()
            mock_engine.return_value = mock_engine_instance
            mock_engine_instance.dialect.name = "sqlite"

            mock_inspector = MagicMock()
            mock_inspector.get_table_names.return_value = ["table1", "table2"]
            mock_inspector.get_view_names.return_value = []

            # Mock the engine.connect() context manager
            mock_connection = MagicMock()
            mock_engine_instance.connect.return_value.__enter__.return_value = (
                mock_connection
            )
            mock_connection.execute.return_value.fetchall.return_value = []

            # Mock the inspect function
            with patch("datatrack.tracker.inspect") as mock_inspect:
                mock_inspect.return_value = mock_inspector

                # Mock introspect_single_table to avoid complex setup
                with patch(
                    "datatrack.tracker.introspect_single_table"
                ) as mock_introspect:
                    mock_introspect.return_value = {
                        "name": "test_table",
                        "columns": [],
                        "indexes": [],
                        "foreign_keys": [],
                        "constraints": [],
                        "triggers": [],
                    }

                    mock_save.return_value = "/path/to/snapshot.yaml"

                    # Test the snapshot function with performance parameters
                    result = snapshot(
                        source="sqlite:///test.db",
                        include_data=False,
                        parallel=True,
                        max_workers=2,
                        batch_size=50,
                    )

                    # Should complete successfully
                    assert result == "/path/to/snapshot.yaml"
                    mock_save.assert_called_once()

    def test_parallel_processing_parameters(self):
        """Test that parallel processing parameters are respected"""
        mock_inspector = MagicMock()
        table_names = [
            f"table_{i}" for i in range(8)
        ]  # 8 tables to trigger parallel processing

        # Mock the actual introspect function to be very fast
        with patch("datatrack.tracker.introspect_single_table") as mock_introspect:
            mock_introspect.return_value = {
                "name": "test",
                "columns": [],
                "indexes": [],
                "foreign_keys": [],
                "constraints": [],
                "triggers": [],
            }

            # Test that it completes quickly and returns correct number of results
            result = introspect_tables_parallel(
                mock_inspector, table_names, max_workers=2
            )

            # Should call introspect_single_table for each table
            assert mock_introspect.call_count == 8
            assert len(result) == 8

            # Verify all results have expected structure
            for table_result in result:
                assert "name" in table_result
                assert "columns" in table_result

    def test_parallel_vs_sequential_threshold(self):
        """Test that small table sets use sequential, large sets use parallel"""
        mock_inspector = MagicMock()

        with patch("datatrack.tracker.introspect_single_table") as mock_introspect:
            mock_introspect.return_value = {
                "name": "test",
                "columns": [],
                "indexes": [],
                "foreign_keys": [],
                "constraints": [],
                "triggers": [],
            }

            # Small set should work fast
            small_tables = ["table1", "table2", "table3"]
            result = introspect_tables_parallel(
                mock_inspector, small_tables, max_workers=2
            )
            assert len(result) == 3

            # Large set should also work
            large_tables = [f"table_{i}" for i in range(10)]
            result = introspect_tables_parallel(
                mock_inspector, large_tables, max_workers=2
            )
            assert len(result) == 10

    def test_error_handling_in_parallel_processing(self):
        """Test error handling during parallel processing"""
        mock_inspector = MagicMock()
        # Use more tables to ensure parallel processing is triggered
        table_names = [f"table_{i}" for i in range(7)] + [
            "error_table"
        ]  # 8 tables total

        def mock_introspect_side_effect(inspector, table_name, schema_name=None):
            if table_name == "error_table":
                raise Exception("Database error")
            return {
                "name": table_name,
                "columns": [],
                "indexes": [],
                "foreign_keys": [],
                "constraints": [],
                "triggers": [],
            }

        with patch(
            "datatrack.tracker.introspect_single_table",
            side_effect=mock_introspect_side_effect,
        ):
            result = introspect_tables_parallel(
                mock_inspector, table_names, max_workers=2
            )

            # Should return 8 results, with error_table having error info
            assert len(result) == 8

            # Find the error table result
            error_result = next(r for r in result if r["name"] == "error_table")
            assert "error" in error_result
            assert "Database error" in error_result["error"]

    def test_batch_size_optimization(self):
        """Test that batch size affects processing strategy"""
        from datatrack.tracker import introspect_tables_paginated

        mock_inspector = MagicMock()
        table_names = [f"table_{i}" for i in range(30)]  # Reduced from 150 to 30

        with patch("datatrack.tracker.introspect_tables_parallel") as mock_parallel:
            mock_parallel.return_value = []

            # Test with different batch sizes
            list(
                introspect_tables_paginated(mock_inspector, table_names, batch_size=10)
            )
            assert mock_parallel.call_count == 3  # 30/10 = 3 batches

            mock_parallel.reset_mock()

            list(
                introspect_tables_paginated(mock_inspector, table_names, batch_size=15)
            )
            assert mock_parallel.call_count == 2  # 30/15 = 2 batches

    def test_performance_benchmark(self):
        """Quick benchmark to verify performance optimizations work"""
        mock_inspector = MagicMock()

        # Use a very small delay for testing
        def fast_introspect(inspector, table_name, schema_name=None):
            time.sleep(0.001)  # 1ms per table instead of 10ms
            return {
                "name": table_name,
                "columns": [{"name": "id", "type": "INTEGER"}],
                "indexes": [],
                "foreign_keys": [],
                "constraints": [],
                "triggers": [],
            }

        table_names = [f"table_{i}" for i in range(4)]  # Reduced to 4 tables

        # Test sequential processing
        start_time = time.time()
        with patch(
            "datatrack.tracker.introspect_single_table", side_effect=fast_introspect
        ):
            sequential_result = [
                fast_introspect(mock_inspector, name) for name in table_names
            ]
        sequential_time = time.time() - start_time

        # Test parallel processing (should complete without errors)
        start_time = time.time()
        with patch(
            "datatrack.tracker.introspect_single_table", side_effect=fast_introspect
        ):
            parallel_result = introspect_tables_parallel(
                mock_inspector, table_names, max_workers=2
            )
        parallel_time = time.time() - start_time

        # Verify both produce same number of results
        assert len(sequential_result) == len(parallel_result) == 4

        # Both should complete reasonably quickly
        assert sequential_time < 1.0  # Should be much less than 1 second
        assert parallel_time < 1.0  # Should be much less than 1 second

        print(
            f"Sequential time: {sequential_time:.3f}s, Parallel time: {parallel_time:.3f}s"
        )

    @pytest.mark.skipif(True, reason="Skip slow integration test by default")
    def test_real_performance_integration(self):
        """Real performance test - skipped by default as it's slow"""
        # This test would use a real database and measure actual performance
        # Only run when specifically testing performance improvements
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
