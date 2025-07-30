"""
Unit tests for datatrack.diff module.
"""

from unittest.mock import MagicMock, mock_open, patch

import pytest

from datatrack.diff import diff_schemas, load_snapshots


class TestLoadSnapshots:
    """Test cases for load_snapshots function."""

    @patch("datatrack.diff.get_connected_db_name")
    @patch("datatrack.diff.Path")
    def test_load_snapshots_success(self, mock_path, mock_get_db_name):
        """Test successful loading of two snapshots."""
        mock_get_db_name.return_value = "test_db"

        # Mock the path construction chain: Path(".databases/exports") / db_name / "snapshots"
        mock_snap_dir = MagicMock()
        mock_path.return_value.__truediv__.return_value.__truediv__.return_value = (
            mock_snap_dir
        )

        # Create mock snapshot files with proper sorting
        snapshot1 = MagicMock()
        snapshot1.__lt__ = lambda self, other: False  # Newer (first in reverse sort)
        snapshot2 = MagicMock()
        snapshot2.__lt__ = lambda self, other: True  # Older (second in reverse sort)

        mock_snap_dir.glob.return_value = [snapshot1, snapshot2]

        # Mock data for the snapshots
        newer_data = {"tables": [{"name": "users_new"}]}
        older_data = {"tables": [{"name": "users_old"}]}

        # Mock file opening and YAML loading
        with patch("builtins.open", mock_open()), patch(
            "yaml.safe_load", side_effect=[newer_data, older_data]
        ):
            older, newer = load_snapshots()

            assert older == older_data
            assert newer == newer_data

    @patch("datatrack.diff.get_connected_db_name")
    @patch("datatrack.diff.Path")
    def test_load_snapshots_insufficient_files(self, mock_path, mock_get_db_name):
        """Test load_snapshots with insufficient snapshot files."""
        mock_get_db_name.return_value = "test_db"

        mock_snap_dir = MagicMock()
        mock_path.return_value = mock_snap_dir
        mock_snap_dir.glob.return_value = []  # No files

        with pytest.raises(FileNotFoundError, match="Need at least 2 snapshots"):
            load_snapshots()

    @patch("datatrack.diff.get_connected_db_name")
    @patch("datatrack.diff.Path")
    def test_load_snapshots_one_file_only(self, mock_path, mock_get_db_name):
        """Test load_snapshots with only one snapshot file."""
        mock_get_db_name.return_value = "test_db"

        mock_snap_dir = MagicMock()
        mock_path.return_value = mock_snap_dir

        snapshot1 = MagicMock()
        mock_snap_dir.glob.return_value = [snapshot1]  # Only one file

        with pytest.raises(FileNotFoundError, match="Need at least 2 snapshots"):
            load_snapshots()


class TestDiffSchemas:
    """Test cases for diff_schemas function."""

    def test_diff_schemas_added_table(self, capsys):
        """Test diff with added table."""
        old_schema = {"tables": [{"name": "users", "columns": []}]}

        new_schema = {
            "tables": [
                {"name": "users", "columns": []},
                {"name": "posts", "columns": []},
            ]
        }

        diff_schemas(old_schema, new_schema)

        captured = capsys.readouterr()
        assert "+ Added table: posts" in captured.out
        assert "SCHEMA DIFF" in captured.out

    def test_diff_schemas_removed_table(self, capsys):
        """Test diff with removed table."""
        old_schema = {
            "tables": [
                {"name": "users", "columns": []},
                {"name": "posts", "columns": []},
            ]
        }

        new_schema = {"tables": [{"name": "users", "columns": []}]}

        diff_schemas(old_schema, new_schema)

        captured = capsys.readouterr()
        assert "- Removed table: posts" in captured.out

    def test_diff_schemas_no_table_changes(self, capsys):
        """Test diff with no table changes."""
        schema = {"tables": [{"name": "users", "columns": []}]}

        diff_schemas(schema, schema)

        captured = capsys.readouterr()
        assert "No tables added or removed." in captured.out

    def test_diff_schemas_added_column(self, capsys):
        """Test diff with added column."""
        old_schema = {
            "tables": [
                {"name": "users", "columns": [{"name": "id", "type": "INTEGER"}]}
            ]
        }

        new_schema = {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "INTEGER"},
                        {"name": "email", "type": "VARCHAR(255)"},
                    ],
                }
            ]
        }

        diff_schemas(old_schema, new_schema)

        captured = capsys.readouterr()
        assert "+ users.email (VARCHAR(255))" in captured.out

    def test_diff_schemas_removed_column(self, capsys):
        """Test diff with removed column."""
        old_schema = {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "INTEGER"},
                        {"name": "email", "type": "VARCHAR(255)"},
                    ],
                }
            ]
        }

        new_schema = {
            "tables": [
                {"name": "users", "columns": [{"name": "id", "type": "INTEGER"}]}
            ]
        }

        diff_schemas(old_schema, new_schema)

        captured = capsys.readouterr()
        assert "- users.email (VARCHAR(255))" in captured.out

    def test_diff_schemas_changed_column_type(self, capsys):
        """Test diff with changed column type."""
        old_schema = {
            "tables": [
                {"name": "users", "columns": [{"name": "name", "type": "VARCHAR(50)"}]}
            ]
        }

        new_schema = {
            "tables": [
                {"name": "users", "columns": [{"name": "name", "type": "VARCHAR(100)"}]}
            ]
        }

        diff_schemas(old_schema, new_schema)

        captured = capsys.readouterr()
        assert "~ users.name changed: VARCHAR(50) -> VARCHAR(100)" in captured.out

    def test_diff_schemas_views_changes(self, capsys):
        """Test diff with view changes."""
        old_schema = {"tables": [], "views": [{"name": "user_view"}]}

        new_schema = {
            "tables": [],
            "views": [{"name": "user_view"}, {"name": "post_view"}],
        }

        diff_schemas(old_schema, new_schema)

        captured = capsys.readouterr()
        assert "Views Changes:" in captured.out
        assert "+ Added view: post_view" in captured.out

    def test_diff_schemas_data_changes(self, capsys):
        """Test diff with data changes."""
        old_schema = {"tables": [], "data": {"users": [{"id": 1, "name": "John"}]}}

        new_schema = {
            "tables": [],
            "data": {"users": [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]},
        }

        diff_schemas(old_schema, new_schema)

        captured = capsys.readouterr()
        assert "DATA DIFF" in captured.out
        assert "Data changes in `users`:" in captured.out

    def test_diff_schemas_no_data_changes(self, capsys):
        """Test diff with no data changes."""
        schema = {"tables": [], "data": {"users": [{"id": 1, "name": "John"}]}}

        diff_schemas(schema, schema)

        captured = capsys.readouterr()
        assert "No data changes in `users`." in captured.out

    def test_diff_schemas_multiple_object_types(self, capsys):
        """Test diff with multiple object types."""
        old_schema = {
            "tables": [],
            "views": [{"name": "old_view"}],
            "triggers": [{"name": "old_trigger"}],
            "procedures": [{"name": "old_proc"}],
            "functions": [{"name": "old_func"}],
            "sequences": [{"name": "old_seq"}],  # Use objects with name key
        }

        new_schema = {
            "tables": [],
            "views": [{"name": "new_view"}],
            "triggers": [{"name": "new_trigger"}],
            "procedures": [{"name": "new_proc"}],
            "functions": [{"name": "new_func"}],
            "sequences": [{"name": "new_seq"}],  # Use objects with name key
        }

        diff_schemas(old_schema, new_schema)

        captured = capsys.readouterr()
        assert "Views Changes:" in captured.out
        assert "Triggers Changes:" in captured.out
        assert "Procedures Changes:" in captured.out
        assert "Functions Changes:" in captured.out
        assert "Sequences Changes:" in captured.out

    def test_diff_schemas_empty_schemas(self, capsys):
        """Test diff with empty schemas."""
        empty_schema = {"tables": []}

        diff_schemas(empty_schema, empty_schema)

        captured = capsys.readouterr()
        assert "SCHEMA DIFF" in captured.out
        assert "DATA DIFF" in captured.out
        assert "Diff complete." in captured.out
