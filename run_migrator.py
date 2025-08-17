#!/usr/bin/env python3
"""
Standalone DatabaseMigrator Runner

This script runs the DatabaseMigrator without importing the full src package
to avoid dependency issues with yfinance and other modules.
"""

import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main function to run the DatabaseMigrator."""
    try:
        logger.info("Starting DatabaseMigrator...")
        logger.info("=" * 50)
        
        # Import the migrator directly
        from src.migrator.database_migrator import DatabaseMigrator
        
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
            return False
        
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
        return True
        
    except Exception as e:
        logger.error(f"DatabaseMigrator failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
