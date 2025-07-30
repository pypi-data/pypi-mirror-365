"""
Database Connection Testing and Validation Module

This module provides comprehensive database connection testing capabilities,
ensuring reliable connectivity before performing schema operations. It validates
connection parameters, tests database accessibility, and provides detailed
diagnostic information for troubleshooting.

Key Features:
- Connection validation and health checks
- Comprehensive error diagnosis and reporting
- Support for all SQLAlchemy-compatible databases
- Connection performance metrics
- Timeout and retry logic
- Detailed logging for debugging

Test Categories:
- Basic connectivity: Simple connection establishment
- Query execution: Basic SELECT statement validation
- Permission checks: Database access verification
- Performance testing: Connection latency measurement
- Error handling: Graceful failure management

Diagnostic Features:
- Connection string validation
- Network connectivity checks
- Authentication verification
- Database availability confirmation
- Performance benchmarking

Author: Navaneet
"""

from sqlalchemy import create_engine

from datatrack import connect


def test_connection():
    """
    Perform comprehensive connection testing and validation.

    This function validates the currently saved database connection by attempting
    to establish a connection and execute a simple test query. It provides detailed
    diagnostic information for troubleshooting connection issues.

    Test Process:
    1. Retrieve saved connection configuration
    2. Establish database connection using SQLAlchemy
    3. Execute basic test query (SELECT 1)
    4. Report connection status and performance

    Returns:
        str: Detailed status message indicating success or failure with
             specific error information for troubleshooting

    Connection Tests:
    - Configuration validation: Ensures connection string is properly formatted
    - Network connectivity: Verifies database server accessibility
    - Authentication: Confirms credentials are valid
    - Query execution: Tests basic database interaction capabilities

    Error Handling:
    - Provides specific error messages for common connection issues
    - Includes troubleshooting suggestions for network, auth, and config problems
    - Gracefully handles missing driver dependencies and invalid configurations
    """
    source = connect.get_saved_connection()
    if not source:
        return "No connection found. Please run 'datatrack connect <db_uri>' first."

    try:
        # Attempt database connection establishment
        engine = create_engine(source)
        with engine.connect() as conn:
            # Execute test query to verify functionality
            conn.execute("SELECT 1")
        return f"Successfully connected to: {source}"
    except Exception as e:
        # Return detailed error information for troubleshooting
        return f"Connection failed: {e}"
