"""
Database Initialization Script

This script initializes the PostgreSQL database with the required tables for stock data.
Run this script to create the database schema before starting the application.
"""

import logging
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import init_db, close_db
from src.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main function to initialize the database."""
    try:
        logger.info("Starting database initialization...")
        logger.info(f"Database URL: {settings.postgres_url}")
        
        # Initialize database tables
        init_db()
        
        logger.info("Database initialization completed successfully!")
        logger.info("The following tables have been created:")
        logger.info("- stock_data: For storing synchronized stock data")
        logger.info("- stock_sync_logs: For logging sync operations")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        sys.exit(1)
    finally:
        # Close database connections
        close_db()

if __name__ == "__main__":
    main()
