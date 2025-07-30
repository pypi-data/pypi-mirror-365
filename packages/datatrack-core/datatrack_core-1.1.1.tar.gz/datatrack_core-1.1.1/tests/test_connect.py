"""
Unit tests for datatrack.connect module.
"""

from unittest.mock import MagicMock, mock_open, patch

import pytest
from sqlalchemy.exc import ArgumentError, OperationalError

from datatrack.connect import (
    get_connected_db_name,
    get_saved_connection,
    remove_connection,
    save_connection,
)


class TestGetConnectedDbName:
    """Test cases for get_connected_db_name function."""

    def test_sqlite_database_name(self):
        """Test extracting database name from SQLite URI."""
        sqlite_uri = "sqlite:///test_database.db"

        with patch("datatrack.connect.DB_LINK_FILE") as mock_file:
            mock_file.exists.return_value = True

            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load", return_value={"link": sqlite_uri}):
                    result = get_connected_db_name()
                    assert result == "test_database"

    def test_mysql_database_name(self):
        """Test extracting database name from MySQL URI."""
        mysql_uri = "mysql+pymysql://user:pass@localhost:3306/my_database"

        with patch("datatrack.connect.DB_LINK_FILE") as mock_file:
            mock_file.exists.return_value = True

            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load", return_value={"link": mysql_uri}):
                    result = get_connected_db_name()
                    assert result == "my_database"

    def test_postgresql_database_name(self):
        """Test extracting database name from PostgreSQL URI."""
        postgres_uri = "postgresql://user:pass@localhost:5432/postgres_db"

        with patch("datatrack.connect.DB_LINK_FILE") as mock_file:
            mock_file.exists.return_value = True

            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load", return_value={"link": postgres_uri}):
                    result = get_connected_db_name()
                    assert result == "postgres_db"

    def test_no_connection_file(self):
        """Test when no connection file exists."""
        with patch("datatrack.connect.DB_LINK_FILE") as mock_file:
            mock_file.exists.return_value = False

            with pytest.raises(ValueError, match="No database connection found"):
                get_connected_db_name()

    def test_sanitize_database_name(self):
        """Test that database names are properly sanitized."""
        uri_with_special_chars = "sqlite:///test-db@name#.db"

        with patch("datatrack.connect.DB_LINK_FILE") as mock_file:
            mock_file.exists.return_value = True

            with patch("builtins.open", mock_open()):
                with patch(
                    "yaml.safe_load", return_value={"link": uri_with_special_chars}
                ):
                    result = get_connected_db_name()
                    assert result == "test-db_name"


class TestSaveConnection:
    """Test cases for save_connection function."""

    @patch("datatrack.connect.create_engine")
    @patch("datatrack.connect.CONFIG_DIR")
    @patch("datatrack.connect.DB_LINK_FILE")
    def test_save_connection_success(
        self, mock_db_file, mock_config_dir, mock_create_engine
    ):
        """Test successful connection save."""
        mock_db_file.exists.return_value = False
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        # Mock the context manager
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=None)

        with patch("builtins.open", mock_open()) as mock_file:
            with patch("yaml.dump") as mock_yaml_dump:
                with patch("builtins.print") as mock_print:
                    save_connection("sqlite:///test.db")

                    mock_create_engine.assert_called_once_with("sqlite:///test.db")
                    mock_conn.execute.assert_called_once()
                    mock_config_dir.mkdir.assert_called_once_with(
                        parents=True, exist_ok=True
                    )
                    mock_yaml_dump.assert_called_once_with(
                        {"link": "sqlite:///test.db"}, mock_file().__enter__()
                    )
                    mock_print.assert_called_with(
                        "Successfully connected and saved link:\n   sqlite:///test.db"
                    )

    @patch("datatrack.connect.DB_LINK_FILE")
    def test_save_connection_already_exists(self, mock_db_file):
        """Test save connection when connection already exists."""
        mock_db_file.exists.return_value = True

        with patch("builtins.print") as mock_print:
            save_connection("sqlite:///test.db")

            mock_print.assert_any_call("A database is already connected.")
            mock_print.assert_any_call(
                "   Disconnect first using: `datatrack disconnect`\n"
            )

    @patch("datatrack.connect.create_engine")
    @patch("datatrack.connect.DB_LINK_FILE")
    def test_save_connection_operational_error_access_denied(
        self, mock_db_file, mock_create_engine
    ):
        """Test save connection with access denied error."""
        mock_db_file.exists.return_value = False
        mock_create_engine.side_effect = OperationalError(
            "", "", "Access denied for user"
        )

        with patch("builtins.print") as mock_print:
            save_connection("mysql://user:pass@localhost/db")

            mock_print.assert_called_with(
                "Access denied. Please check your DB username/password."
            )

    @patch("datatrack.connect.create_engine")
    @patch("datatrack.connect.DB_LINK_FILE")
    def test_save_connection_operational_error_cant_connect(
        self, mock_db_file, mock_create_engine
    ):
        """Test save connection with connection error."""
        mock_db_file.exists.return_value = False
        mock_create_engine.side_effect = OperationalError(
            "", "", "Can't connect to MySQL server"
        )

        with patch("builtins.print") as mock_print:
            save_connection("mysql://user:pass@localhost/db")

            mock_print.assert_called_with(
                "Could not connect to server. Is the DB server running?"
            )

    @patch("datatrack.connect.create_engine")
    @patch("datatrack.connect.DB_LINK_FILE")
    def test_save_connection_argument_error(self, mock_db_file, mock_create_engine):
        """Test save connection with invalid connection string."""
        mock_db_file.exists.return_value = False
        mock_create_engine.side_effect = ArgumentError("Invalid connection string")

        with patch("builtins.print") as mock_print:
            save_connection("invalid://connection")

            mock_print.assert_any_call(
                "Invalid connection string. Please verify format."
            )

    @patch("datatrack.connect.create_engine")
    @patch("datatrack.connect.DB_LINK_FILE")
    def test_save_connection_module_not_found(self, mock_db_file, mock_create_engine):
        """Test save connection with missing driver."""
        mock_db_file.exists.return_value = False
        mock_create_engine.side_effect = ModuleNotFoundError(
            "No module named 'pymysql'"
        )

        with patch("builtins.print") as mock_print:
            save_connection("mysql://user:pass@localhost/db")

            mock_print.assert_any_call(
                "Missing driver. Please install required DB driver packages."
            )


class TestGetSavedConnection:
    """Test cases for get_saved_connection function."""

    def test_get_saved_connection_exists(self):
        """Test getting saved connection when file exists."""
        test_uri = "sqlite:///test.db"

        with patch("datatrack.connect.DB_LINK_FILE") as mock_file:
            mock_file.exists.return_value = True

            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load", return_value={"link": test_uri}):
                    result = get_saved_connection()
                    assert result == test_uri

    def test_get_saved_connection_not_exists(self):
        """Test getting saved connection when file doesn't exist."""
        with patch("datatrack.connect.DB_LINK_FILE") as mock_file:
            mock_file.exists.return_value = False

            result = get_saved_connection()
            assert result is None

    def test_get_saved_connection_no_link(self):
        """Test getting saved connection when file exists but no link."""
        with patch("datatrack.connect.DB_LINK_FILE") as mock_file:
            mock_file.exists.return_value = True

            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load", return_value={}):
                    result = get_saved_connection()
                    assert result is None


class TestRemoveConnection:
    """Test cases for remove_connection function."""

    def test_remove_connection_exists(self):
        """Test removing connection when file exists."""
        with patch("datatrack.connect.DB_LINK_FILE") as mock_file:
            mock_file.exists.return_value = True

            with patch("builtins.print") as mock_print:
                remove_connection()

                mock_file.unlink.assert_called_once()
                mock_print.assert_called_with("Disconnected and removed saved DB link.")

    def test_remove_connection_not_exists(self):
        """Test removing connection when file doesn't exist."""
        with patch("datatrack.connect.DB_LINK_FILE") as mock_file:
            mock_file.exists.return_value = False

            with patch("builtins.print") as mock_print:
                remove_connection()

                mock_file.unlink.assert_not_called()
                mock_print.assert_called_with("No active database connection found.")
