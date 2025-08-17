#!/usr/bin/env python3
"""
Example usage of DatabaseMigrator class.

This script demonstrates how to use the DatabaseMigrator to:
- Check database status
- Create database if it doesn't exist
- Initialize tables and run migrations
- Get database information
"""

import logging
import sys
import os

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

def main():
    """Main function demonstrating DatabaseMigrator usage."""
    try:
        logger.info("DatabaseMigrator Example Usage")
        logger.info("=" * 50)
        
        # Initialize the migrator
        migrator = DatabaseMigrator()
        
        # Get initial database status
        logger.info("Checking database status...")
        status = migrator.get_database_status()
        
        logger.info(f"Database: {status['database_name']}")
        logger.info(f"Exists: {status['database_exists']}")
        logger.info(f"Connection: {status['connection_status']}")
        
        if 'postgres_version' in status:
            logger.info(f"PostgreSQL Version: {status['postgres_version']}")
        
        # Initialize database (creates if doesn't exist, creates tables, runs migrations)
        logger.info("\nInitializing database...")
        if migrator.initialize_database():
            logger.info("✅ Database initialization successful!")
        else:
            logger.error("❌ Database initialization failed!")
            return
        
        # Get updated status after initialization
        logger.info("\nUpdated database status:")
        updated_status = migrator.get_database_status()
        
        logger.info(f"Database: {updated_status['database_name']}")
        logger.info(f"Exists: {updated_status['database_exists']}")
        logger.info(f"Connection: {updated_status['connection_status']}")
        
        # Show table information
        if updated_status['tables']:
            logger.info("\nDatabase tables:")
            for table_name, table_info in updated_status['tables'].items():
                logger.info(f"  📋 {table_name}")
                logger.info(f"    Columns: {', '.join(table_info['columns'])}")
                if table_info['indexes']:
                    logger.info(f"    Indexes: {', '.join(table_info['indexes'])}")
                if table_info['foreign_keys']:
                    logger.info(f"    Foreign Keys: {', '.join(table_info['foreign_keys'])}")
        else:
            logger.info("No tables found in database")
        
        logger.info("\n🎉 Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Example usage failed: {e}")
        sys.exit(1)

def check_database_only():
    """Simple function to just check if database exists."""
    try:
        migrator = DatabaseMigrator()
        
        if migrator.database_exists():
            logger.info(f"✅ Database '{migrator.database_name}' exists")
            return True
        else:
            logger.info(f"❌ Database '{migrator.database_name}' does not exist")
            return False
            
    except Exception as e:
        logger.error(f"Error checking database: {e}")
        return False

def create_database_only():
    """Simple function to just create the database."""
    try:
        migrator = DatabaseMigrator()
        
        if migrator.create_database():
            logger.info(f"✅ Database '{migrator.database_name}' created successfully")
            return True
        else:
            logger.error(f"❌ Failed to create database '{migrator.database_name}'")
            return False
            
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False

if __name__ == "__main__":
    # You can call different functions based on your needs:
    
    # Full initialization (recommended for first-time setup)
    main()
    
    # Or just check if database exists:
    # check_database_only()
    
    # Or just create database:
    # create_database_only()
