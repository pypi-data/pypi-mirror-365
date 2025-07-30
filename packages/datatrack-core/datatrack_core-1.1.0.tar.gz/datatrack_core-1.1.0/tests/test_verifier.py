"""
Unit tests for datatrack.verifier module.
"""

from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml

from datatrack.verifier import (
    DEFAULT_RULES,
    is_snake_case,
    load_latest_snapshot,
    load_rules,
    verify_schema,
)


class TestLoadRules:
    """Test cases for load_rules function."""

    def test_load_rules_file_exists(self, tmp_path):
        """Test loading rules from existing file."""
        rules_file = tmp_path / "schema_rules.yaml"
        custom_rules = {
            "rules": {
                "enforce_snake_case": False,
                "reserved_keywords": ["keyword", "custom"],
            }
        }

        with open(rules_file, "w") as f:
            yaml.dump(custom_rules, f)

        with patch("datatrack.verifier.Path") as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value = rules_file

            result = load_rules()

        expected = {
            "enforce_snake_case": False,
            "reserved_keywords": {"keyword", "custom"},
        }
        assert result == expected

    def test_load_rules_file_not_exists(self):
        """Test loading rules when file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            result = load_rules()
            assert result == DEFAULT_RULES

    def test_load_rules_yaml_error(self):
        """Test loading rules with YAML error."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch(
                    "yaml.safe_load", side_effect=yaml.YAMLError("Invalid YAML")
                ):
                    with patch("builtins.print") as mock_print:
                        result = load_rules()
                        assert result == DEFAULT_RULES
                        mock_print.assert_called()


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
            "_test",
            "test_",
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
            "user name",
            "user@test",
        ]
        for name in invalid_names:
            assert not is_snake_case(name), f"Should be invalid: {name}"


class TestVerifySchema:
    """Test cases for verify_schema function."""

    def test_verify_schema_valid(self):
        """Test verification of valid schema."""
        valid_schema = {
            "tables": [
                {
                    "name": "users",
                    "columns": [{"name": "id"}, {"name": "name"}, {"name": "email"}],
                }
            ]
        }

        rules = {"enforce_snake_case": True, "reserved_keywords": {"select", "from"}}

        violations = verify_schema(valid_schema, rules)
        assert len(violations) == 0

    def test_verify_schema_snake_case_violations(self):
        """Test schema with snake_case violations."""
        schema = {
            "tables": [
                {
                    "name": "UserTable",  # Not snake_case
                    "columns": [
                        {"name": "UserName"},  # Not snake_case
                        {"name": "user_email"},  # Valid
                    ],
                }
            ]
        }

        rules = {"enforce_snake_case": True, "reserved_keywords": set()}

        violations = verify_schema(schema, rules)
        assert len(violations) == 2  # Table name + column name
        assert any("UserTable" in violation for violation in violations)
        assert any("UserName" in violation for violation in violations)

    def test_verify_schema_reserved_keywords(self):
        """Test schema with reserved keyword violations."""
        schema = {
            "tables": [
                {
                    "name": "select",  # Reserved keyword
                    "columns": [
                        {"name": "from"},  # Reserved keyword
                        {"name": "user_id"},  # Valid
                    ],
                }
            ]
        }

        rules = {"enforce_snake_case": False, "reserved_keywords": {"select", "from"}}

        violations = verify_schema(schema, rules)
        assert len(violations) == 2  # Table name + column name
        assert any(
            "select" in violation and "reserved" in violation
            for violation in violations
        )
        assert any(
            "from" in violation and "reserved" in violation for violation in violations
        )

    def test_verify_schema_snake_case_disabled(self):
        """Test verification with snake_case enforcement disabled."""
        schema = {
            "tables": [
                {
                    "name": "UserTable",  # Would be violation if enabled
                    "columns": [{"name": "UserName"}],  # Would be violation if enabled
                }
            ]
        }

        rules = {"enforce_snake_case": False, "reserved_keywords": set()}

        violations = verify_schema(schema, rules)
        assert len(violations) == 0

    def test_verify_schema_data_validation(self):
        """Test schema data validation."""
        schema = {
            "tables": [
                {"name": "users", "columns": [{"name": "id"}, {"name": "name"}]}
            ],
            "data": {
                "users": [
                    {"id": 1, "name": "John"},  # Valid row
                    {
                        "id": 2,
                        "extra_field": "value",
                    },  # Missing 'name', has extra field
                    "invalid_row",  # Not a dictionary
                ]
            },
        }

        rules = {"enforce_snake_case": False, "reserved_keywords": set()}

        violations = verify_schema(schema, rules)

        # Should have violations for data issues
        assert len(violations) >= 3
        assert any("missing keys" in violation for violation in violations)
        assert any("unknown keys" in violation for violation in violations)
        assert any("not a dictionary" in violation for violation in violations)

    def test_verify_schema_data_not_list(self):
        """Test schema with data that's not a list."""
        schema = {
            "tables": [{"name": "users", "columns": [{"name": "id"}]}],
            "data": {"users": "not_a_list"},  # Should be a list
        }

        rules = {"enforce_snake_case": False, "reserved_keywords": set()}

        violations = verify_schema(schema, rules)
        assert len(violations) == 1
        assert "not a list" in violations[0]

    def test_verify_schema_missing_data(self):
        """Test schema with missing data for tables."""
        schema = {
            "tables": [
                {"name": "users", "columns": [{"name": "id"}]},
                {"name": "posts", "columns": [{"name": "id"}]},
            ],
            "data": {
                "users": [{"id": 1}]
                # Missing 'posts' data
            },
        }

        rules = {"enforce_snake_case": False, "reserved_keywords": set()}

        violations = verify_schema(schema, rules)
        assert len(violations) == 1
        assert "No data found for table `posts`" in violations[0]

    def test_verify_schema_empty_tables(self):
        """Test verification with empty tables."""
        schema = {"tables": []}
        rules = {"enforce_snake_case": True, "reserved_keywords": set()}

        violations = verify_schema(schema, rules)
        assert len(violations) == 0

    def test_verify_schema_no_tables_key(self):
        """Test verification with no tables key."""
        schema = {}
        rules = {"enforce_snake_case": True, "reserved_keywords": set()}

        violations = verify_schema(schema, rules)
        assert len(violations) == 0


class TestLoadLatestSnapshot:
    """Test cases for load_latest_snapshot function."""

    @patch("datatrack.verifier.get_connected_db_name")
    @patch("datatrack.verifier.Path")
    def test_load_latest_snapshot_success(self, mock_path, mock_get_db_name):
        """Test successful loading of latest snapshot."""
        mock_get_db_name.return_value = "test_db"

        # Mock the Path construction chain
        mock_snap_dir = MagicMock()

        mock_path.return_value.__truediv__.return_value.__truediv__.return_value = (
            mock_snap_dir
        )

        # Create mock snapshot files with proper sorting behavior
        snapshot1 = MagicMock()
        snapshot1.__lt__ = lambda self, other: False  # Latest file
        snapshot2 = MagicMock()
        snapshot2.__lt__ = lambda self, other: True  # Older file

        mock_snap_dir.glob.return_value = [snapshot2, snapshot1]

        # Mock file content
        snapshot_data = {"tables": [{"name": "users"}]}

        with patch("builtins.open", mock_open()), patch(
            "yaml.safe_load", return_value=snapshot_data
        ):
            result = load_latest_snapshot()

            assert result == snapshot_data

    @patch("datatrack.verifier.get_connected_db_name")
    @patch("datatrack.verifier.Path")
    def test_load_latest_snapshot_no_files(self, mock_path, mock_get_db_name):
        """Test load_latest_snapshot when no files exist."""
        mock_get_db_name.return_value = "test_db"

        mock_snap_dir = MagicMock()
        mock_path.return_value = mock_snap_dir
        mock_snap_dir.glob.return_value = []  # No files

        with pytest.raises(ValueError, match="No snapshots found"):
            load_latest_snapshot()


class TestVerifierIntegration:
    """Integration tests for verifier functionality."""

    def test_comprehensive_verification_workflow(self):
        """Test comprehensive verification workflow."""
        problematic_schema = {
            "tables": [
                {
                    "name": "User_Table",  # Mixed case (snake_case violation if enforced)
                    "columns": [
                        {"name": "from"},  # Reserved keyword
                        {"name": "userName"},  # Not snake_case
                    ],
                }
            ],
            "data": {
                "User_Table": [
                    {
                        "from": "test",
                        "extra": "field",
                    },  # Missing userName, has extra field
                ]
            },
        }

        rules = {
            "enforce_snake_case": True,
            "reserved_keywords": {"from", "select", "where"},
        }

        violations = verify_schema(problematic_schema, rules)

        # Should have multiple violations
        assert len(violations) > 0
        assert any("snake_case" in violation for violation in violations)
        assert any("reserved" in violation for violation in violations)
        assert any("missing keys" in violation for violation in violations)

    def test_verification_with_default_rules(self):
        """Test verification using default rules."""
        schema = {
            "tables": [
                {
                    "name": "select",  # Should be caught by default reserved keywords
                    "columns": [
                        {
                            "name": "NotSnakeCase"
                        }  # Should be caught by snake_case enforcement
                    ],
                }
            ]
        }

        violations = verify_schema(schema, DEFAULT_RULES)

        # Should have violations from default rules
        assert len(violations) > 0
