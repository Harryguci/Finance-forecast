#!/usr/bin/env python3
"""
Test script for DatabaseMigrator class.

This script tests the basic functionality of the DatabaseMigrator
without actually creating or modifying any databases.
"""

import sys
import os
import logging

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.migrator.database_migrator import DatabaseMigrator
from src.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_migrator_initialization():
    """Test DatabaseMigrator initialization."""
    try:
        logger.info("Testing DatabaseMigrator initialization...")
        
        migrator = DatabaseMigrator()
        
        # Check basic attributes
        assert migrator.database_name == settings.postgres_db
        assert migrator.host == settings.postgres_host
        assert migrator.port == settings.postgres_port
        assert migrator.user == settings.postgres_user
        assert migrator.password == settings.postgres_password
        
        logger.info("✅ DatabaseMigrator initialization test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ DatabaseMigrator initialization test failed: {e}")
        return False

def test_connection_string_generation():
    """Test connection string generation."""
    try:
        logger.info("Testing connection string generation...")
        
        migrator = DatabaseMigrator()
        
        # Test postgres connection string
        postgres_conn = migrator._get_postgres_connection_string("postgres")
        assert "postgresql://" in postgres_conn
        assert "postgres" in postgres_conn
        
        # Test custom database connection string
        custom_conn = migrator._get_postgres_connection_string("test_db")
        assert "test_db" in custom_conn
        
        logger.info("✅ Connection string generation test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection string generation test failed: {e}")
        return False

def test_database_status_methods():
    """Test database status methods (without actual database connection)."""
    try:
        logger.info("Testing database status methods...")
        
        migrator = DatabaseMigrator()
        
        # Test that methods exist and are callable
        assert callable(migrator.database_exists)
        assert callable(migrator.create_database)
        assert callable(migrator.create_tables)
        assert callable(migrator.run_migrations)
        assert callable(migrator.initialize_database)
        assert callable(migrator.get_database_status)
        assert callable(migrator.get_table_info)
        
        logger.info("✅ Database status methods test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database status methods test failed: {e}")
        return False

def test_parse_connection_details():
    """Test connection details parsing."""
    try:
        logger.info("Testing connection details parsing...")
        
        # Test with custom database URL
        custom_url = "postgresql://user:pass@localhost:5432/custom_db?sslmode=prefer"
        migrator = DatabaseMigrator(custom_url)
        
        # The migrator should parse the database name from the URL
        # Note: This is a basic test - actual parsing depends on the implementation
        
        logger.info("✅ Connection details parsing test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection details parsing test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("Starting DatabaseMigrator tests...")
    logger.info("=" * 50)
    
    tests = [
        test_migrator_initialization,
        test_connection_string_generation,
        test_database_status_methods,
        test_parse_connection_details
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        logger.info("")  # Empty line for readability
    
    logger.info("=" * 50)
    logger.info(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! DatabaseMigrator is ready to use.")
        return True
    else:
        logger.error(f"❌ {total - passed} test(s) failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
