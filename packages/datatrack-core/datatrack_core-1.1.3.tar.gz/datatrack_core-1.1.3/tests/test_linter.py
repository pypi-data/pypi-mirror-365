"""
Unit tests for datatrack.linter module.
"""

from unittest.mock import MagicMock, mock_open, patch

import pytest

from datatrack.linter import (
    AMBIGUOUS_NAMES,
    GENERIC_TYPES,
    MAX_NAME_LENGTH,
    RESERVED_KEYWORDS,
    is_snake_case,
    lint_schema,
    load_latest_snapshot,
)


class TestIsSnakeCase:
    """Test cases for is_snake_case function."""

    def test_valid_snake_case(self):
        """Test valid snake_case names."""
        valid_names = [
            "user",
            "user_profile",
            "order_item",
            "simple_name",
            "a",
            "a1",
            "test_123",
        ]
        for name in valid_names:
            assert is_snake_case(name), f"Should be valid: {name}"

    def test_invalid_snake_case(self):
        """Test invalid snake_case names."""
        invalid_names = [
            "UserProfile",
            "orderItem",
            "user-profile",
            "User_Profile",
            "1user",
            "_user",
        ]
        for name in invalid_names:
            assert not is_snake_case(name), f"Should be invalid: {name}"


class TestLoadLatestSnapshot:
    """Test cases for load_latest_snapshot function."""

    @patch("datatrack.linter.get_connected_db_name")
    @patch("datatrack.linter.Path")
    @patch("datatrack.linter.sorted")
    def test_load_latest_snapshot_success(
        self, mock_sorted, mock_path_class, mock_get_db_name
    ):
        """Test successful loading of latest snapshot."""
        mock_get_db_name.return_value = "test_db"

        # Create a chain of mocked path objects
        mock_base_path = MagicMock()
        mock_db_path = MagicMock()
        mock_snap_dir = MagicMock()

        mock_path_class.return_value = mock_base_path
        mock_base_path.__truediv__.return_value = mock_db_path
        mock_db_path.__truediv__.return_value = mock_snap_dir

        # Mock snapshot files
        snapshot_files = [
            "snapshot_20240101_120000.yaml",
            "snapshot_20240101_110000.yaml",
        ]
        mock_snap_dir.glob.return_value = snapshot_files
        mock_sorted.return_value = list(reversed(snapshot_files))  # Latest first

        # Mock file content
        snapshot_data = {"tables": [{"name": "users"}]}

        with patch("builtins.open", mock_open()):
            with patch("yaml.safe_load", return_value=snapshot_data):
                result = load_latest_snapshot()

                assert result == snapshot_data
                mock_snap_dir.glob.assert_called_once_with("*.yaml")
                mock_sorted.assert_called_once()

    @patch("datatrack.linter.get_connected_db_name")
    @patch("datatrack.linter.Path")
    def test_load_latest_snapshot_no_files(self, mock_path, mock_get_db_name):
        """Test load_latest_snapshot with no snapshot files."""
        mock_get_db_name.return_value = "test_db"

        mock_snap_dir = MagicMock()
        mock_path.return_value = mock_snap_dir
        mock_snap_dir.glob.return_value = []  # No files

        with pytest.raises(ValueError, match="No snapshots found"):
            load_latest_snapshot()


class TestLintSchema:
    """Test cases for lint_schema function."""

    def test_lint_schema_valid(self):
        """Test linting a valid schema."""
        valid_schema = {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "BIGINT"},  # Not generic
                        {"name": "name", "type": "VARCHAR(100)"},
                        {"name": "email", "type": "VARCHAR(255)"},
                    ],
                }
            ]
        }

        warnings = lint_schema(valid_schema)
        assert len(warnings) == 0

    def test_lint_schema_table_name_issues(self):
        """Test linting schema with table name issues."""
        problematic_schema = {
            "tables": [
                {"name": "data", "columns": []},  # Ambiguous name
                {"name": "select", "columns": []},  # Reserved keyword
                {"name": "UserProfiles", "columns": []},  # Not snake_case
                {"name": "a" * (MAX_NAME_LENGTH + 1), "columns": []},  # Too long
            ]
        }

        warnings = lint_schema(problematic_schema)

        # Should have warnings for each issue
        assert len(warnings) >= 4
        assert any("ambiguous" in warning.lower() for warning in warnings)
        assert any("reserved" in warning.lower() for warning in warnings)
        assert any("snake_case" in warning.lower() for warning in warnings)
        assert any("exceeds max length" in warning.lower() for warning in warnings)

    def test_lint_schema_column_issues(self):
        """Test linting schema with column issues."""
        problematic_schema = {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "select", "type": "INTEGER"},  # Reserved keyword
                        {
                            "name": "data",
                            "type": "text",
                        },  # Ambiguous name + generic type
                        {"name": "UserName", "type": "VARCHAR(100)"},  # Not snake_case
                        {
                            "name": "a" * (MAX_NAME_LENGTH + 1),
                            "type": "INTEGER",
                        },  # Too long
                    ],
                }
            ]
        }

        warnings = lint_schema(problematic_schema)

        # Should have warnings for column issues
        assert len(warnings) >= 4
        assert any(
            "reserved" in warning.lower() and "column" in warning.lower()
            for warning in warnings
        )
        assert any(
            "ambiguous" in warning.lower() and "column" in warning.lower()
            for warning in warnings
        )
        assert any(
            "snake_case" in warning.lower() and "column" in warning.lower()
            for warning in warnings
        )
        assert any("generic type" in warning.lower() for warning in warnings)

    def test_lint_schema_empty(self):
        """Test linting empty schema."""
        empty_schema = {"tables": []}
        warnings = lint_schema(empty_schema)
        assert len(warnings) == 0

    def test_lint_schema_no_tables_key(self):
        """Test linting schema without tables key."""
        schema = {}
        warnings = lint_schema(schema)
        assert len(warnings) == 0

    def test_lint_schema_generic_types(self):
        """Test detection of generic types."""
        schema_with_generic_types = {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "field1", "type": "string"},
                        {"name": "field2", "type": "integer"},
                        {"name": "field3", "type": "text"},
                        {"name": "field4", "type": "json"},
                        {"name": "proper_field", "type": "VARCHAR(255)"},  # Not generic
                    ],
                }
            ]
        }

        warnings = lint_schema(schema_with_generic_types)

        # Should warn about generic types but not VARCHAR(255)
        generic_warnings = [w for w in warnings if "generic type" in w.lower()]
        assert len(generic_warnings) == 4  # For string, integer, text, json
        assert not any("proper_field" in warning for warning in warnings)


class TestLinterConstants:
    """Test that linter constants are properly defined."""

    def test_max_name_length(self):
        """Test that MAX_NAME_LENGTH is defined and reasonable."""
        assert isinstance(MAX_NAME_LENGTH, int)
        assert MAX_NAME_LENGTH > 0

    def test_ambiguous_names_set(self):
        """Test that AMBIGUOUS_NAMES is a set with expected values."""
        assert isinstance(AMBIGUOUS_NAMES, set)
        assert "data" in AMBIGUOUS_NAMES
        assert "value" in AMBIGUOUS_NAMES
        assert len(AMBIGUOUS_NAMES) > 0

    def test_reserved_keywords_set(self):
        """Test that RESERVED_KEYWORDS is a set with expected values."""
        assert isinstance(RESERVED_KEYWORDS, set)
        assert "select" in RESERVED_KEYWORDS
        assert "from" in RESERVED_KEYWORDS
        assert len(RESERVED_KEYWORDS) > 0

    def test_generic_types_set(self):
        """Test that GENERIC_TYPES is a set with expected values."""
        assert isinstance(GENERIC_TYPES, set)
        assert "string" in GENERIC_TYPES
        assert "integer" in GENERIC_TYPES
        assert len(GENERIC_TYPES) > 0


class TestLinterIntegration:
    """Integration tests for linter functionality."""

    def test_complete_linting_workflow(self):
        """Test complete linting workflow with various issues."""
        comprehensive_schema = {
            "tables": [
                {
                    "name": "data",  # Ambiguous
                    "columns": [
                        {"name": "select", "type": "text"},  # Reserved + generic
                        {
                            "name": "veryLongColumnNameThatExceedsTheMaximumAllowed",
                            "type": "VARCHAR(100)",
                        },  # Too long
                    ],
                },
                {
                    "name": "proper_users",
                    "columns": [
                        {"name": "id", "type": "BIGINT"},  # Not generic
                        {"name": "name", "type": "VARCHAR(100)"},
                        {"name": "email", "type": "VARCHAR(255)"},
                    ],
                },
            ]
        }

        warnings = lint_schema(comprehensive_schema)

        # Should have multiple warnings but not fail
        assert len(warnings) > 0
        assert all(isinstance(warning, str) for warning in warnings)

        # Should not have warnings for the proper table
        proper_table_warnings = [w for w in warnings if "proper_users" in w]
        assert len(proper_table_warnings) == 0
