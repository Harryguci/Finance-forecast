import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text, inspect, MetaData
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Optional, List, Dict, Any
import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import settings

logger = logging.getLogger(__name__)

# Create our own Base for migrations to avoid circular imports
MigrationBase = declarative_base()

class DatabaseMigrator:
    """
    Database migration utility for creating and managing PostgreSQL databases.
    
    This class handles:
    - Database existence checks
    - Database creation
    - Table creation and updates
    - Schema migrations
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize the DatabaseMigrator.
        
        Args:
            database_url: Optional database URL. If not provided, uses settings.
        """
        self.database_url = database_url or settings.postgres_url
        self.database_name = settings.postgres_db
        self.host = settings.postgres_host
        self.port = settings.postgres_port
        self.user = settings.postgres_user
        self.password = settings.postgres_password
        
        # Parse connection details for database creation
        self._parse_connection_details()
    
    def _parse_connection_details(self):
        """Parse connection details from database URL or settings."""
        if self.database_url:
            # Extract database name from URL if present
            if '/' in self.database_url.split('@')[-1]:
                db_part = self.database_url.split('@')[-1].split('/')[-1]
                if '?' in db_part:
                    self.database_name = db_part.split('?')[0]
                else:
                    self.database_name = db_part
    
    def _get_postgres_connection_string(self, database: Optional[str] = None) -> str:
        """
        Get PostgreSQL connection string for a specific database.
        
        Args:
            database: Database name. If None, connects to postgres database.
            
        Returns:
            Connection string
        """
        db_name = database or "postgres"
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{db_name}?sslmode={settings.postgres_ssl_mode}"
    
    def database_exists(self) -> bool:
        """
        Check if the target database exists.
        
        Returns:
            True if database exists, False otherwise
        """
        try:
            # Connect to postgres database to check if our target database exists
            conn_string = self._get_postgres_connection_string("postgres")
            engine = create_engine(conn_string)
            
            with engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT 1 FROM pg_database WHERE datname = :db_name"
                ), {"db_name": self.database_name})
                
                return result.fetchone() is not None
                
        except Exception as e:
            logger.error(f"Error checking if database exists: {e}")
            return False
    
    def create_database(self) -> bool:
        """
        Create the target database if it doesn't exist.
        
        Returns:
            True if database was created or already exists, False on error
        """
        if self.database_exists():
            logger.info(f"Database '{self.database_name}' already exists")
            return True
        
        try:
            # Connect to postgres database to create our target database
            conn_string = self._get_postgres_connection_string("postgres")
            engine = create_engine(conn_string)
            
            with engine.connect() as conn:
                # Set isolation level to autocommit for CREATE DATABASE
                conn.execute(text("COMMIT"))
                conn.execute(text(f"CREATE DATABASE \"{self.database_name}\""))
                logger.info(f"Database '{self.database_name}' created successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error creating database '{self.database_name}': {e}")
            return False
    
    def create_tables(self) -> bool:
        """
        Create all tables defined in the models.
        
        Returns:
            True if tables were created successfully, False on error
        """
        try:
            # Create engine for our target database
            engine = create_engine(self.database_url)
            
            # Import models here to avoid circular import issues
            # We'll import them only when needed for table creation
            try:
                from src.models.stock_data import StockData, StockSyncLog
                logger.info("Models imported successfully")
            except ImportError as e:
                logger.warning(f"Could not import models: {e}")
                logger.info("Creating tables using direct SQL instead")
                return self._create_tables_with_sql(engine)
            
            # Create all tables from Base metadata
            from src.database.connection import Base
            Base.metadata.create_all(bind=engine)
            logger.info("All database tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            # Fallback to SQL-based table creation
            try:
                engine = create_engine(self.database_url)
                return self._create_tables_with_sql(engine)
            except Exception as sql_error:
                logger.error(f"SQL-based table creation also failed: {sql_error}")
                return False
    
    def _create_tables_with_sql(self, engine) -> bool:
        """
        Create tables using direct SQL as a fallback method.
        
        Args:
            engine: SQLAlchemy engine
            
        Returns:
            True if tables were created successfully, False on error
        """
        try:
            with engine.connect() as conn:
                # Create stock_data table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS stock_data (
                        id SERIAL PRIMARY KEY,
                        symbol VARCHAR(20) NOT NULL,
                        price DOUBLE PRECISION NOT NULL,
                        volume INTEGER,
                        open_price DOUBLE PRECISION,
                        high_price DOUBLE PRECISION,
                        low_price DOUBLE PRECISION,
                        previous_close DOUBLE PRECISION,
                        change DOUBLE PRECISION,
                        change_percent DOUBLE PRECISION,
                        market_cap DOUBLE PRECISION,
                        pe_ratio DOUBLE PRECISION,
                        dividend_yield DOUBLE PRECISION,
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        sync_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        provider VARCHAR(50) NOT NULL DEFAULT 'yahoo',
                        status VARCHAR(20) NOT NULL DEFAULT 'success',
                        error_message TEXT,
                        is_trading_hours BOOLEAN NOT NULL DEFAULT TRUE,
                        trading_day VARCHAR(10)
                    )
                """))
                
                # Create stock_sync_logs table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS stock_sync_logs (
                        id SERIAL PRIMARY KEY,
                        sync_batch_id VARCHAR(50) NOT NULL,
                        provider VARCHAR(50) NOT NULL,
                        start_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        end_time TIMESTAMP WITH TIME ZONE,
                        total_symbols INTEGER NOT NULL DEFAULT 0,
                        successful_syncs INTEGER NOT NULL DEFAULT 0,
                        failed_syncs INTEGER NOT NULL DEFAULT 0,
                        status VARCHAR(20) NOT NULL DEFAULT 'running',
                        error_message TEXT,
                        is_trading_hours BOOLEAN NOT NULL DEFAULT TRUE
                    )
                """))
                
                # Create indexes
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_symbol_timestamp ON stock_data (symbol, timestamp)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp ON stock_data (timestamp)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_provider ON stock_data (provider)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_status ON stock_data (status)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_sync_batch_id ON stock_sync_logs (sync_batch_id)
                """))
                
                conn.commit()
                logger.info("Tables created successfully using SQL")
                return True
                
        except Exception as e:
            logger.error(f"Error creating tables with SQL: {e}")
            return False
    
    def get_table_info(self) -> Dict[str, Any]:
        """
        Get information about existing tables in the database.
        
        Returns:
            Dictionary containing table information
        """
        try:
            engine = create_engine(self.database_url)
            inspector = inspect(engine)
            
            tables = inspector.get_table_names()
            table_info = {}
            
            for table in tables:
                columns = inspector.get_columns(table)
                indexes = inspector.get_indexes(table)
                foreign_keys = inspector.get_foreign_keys(table)
                
                table_info[table] = {
                    'columns': [col['name'] for col in columns],
                    'indexes': [idx['name'] for idx in indexes],
                    'foreign_keys': [fk['name'] for fk in foreign_keys]
                }
            
            return table_info
            
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            return {}
    
    def run_migrations(self) -> bool:
        """
        Run database migrations.
        
        Returns:
            True if migrations completed successfully, False on error
        """
        try:
            # For now, this is a placeholder for future migration logic
            # You can extend this to handle versioned migrations
            logger.info("Running database migrations...")
            
            # Check if migrations table exists, create if not
            engine = create_engine(self.database_url)
            
            with engine.connect() as conn:
                # Create migrations table if it doesn't exist
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS migrations (
                        id SERIAL PRIMARY KEY,
                        version VARCHAR(50) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
            
            logger.info("Database migrations completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error running migrations: {e}")
            return False
    
    def initialize_database(self) -> bool:
        """
        Complete database initialization process.
        
        This method:
        1. Creates the database if it doesn't exist
        2. Creates all tables
        3. Runs any necessary migrations
        
        Returns:
            True if initialization was successful, False on error
        """
        try:
            logger.info("Starting database initialization...")
            
            # Step 1: Create database if it doesn't exist
            if not self.create_database():
                logger.error("Failed to create database")
                return False
            
            # Step 2: Create tables
            if not self.create_tables():
                logger.error("Failed to create tables")
                return False
            
            # Step 3: Run migrations
            if not self.run_migrations():
                logger.error("Failed to run migrations")
                return False
            
            logger.info("Database initialization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    def reset_database(self) -> bool:
        """
        Reset the database by dropping all tables and recreating them.
        
        WARNING: This will delete all data!
        
        Returns:
            True if reset was successful, False on error
        """
        try:
            logger.warning("Resetting database - all data will be lost!")
            
            engine = create_engine(self.database_url)
            
            # Drop all tables
            from src.database.connection import Base
            Base.metadata.drop_all(bind=engine)
            logger.info("All tables dropped successfully")
            
            # Recreate all tables
            if not self.create_tables():
                logger.error("Failed to recreate tables")
                return False
            
            logger.info("Database reset completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database reset failed: {e}")
            return False
    
    def get_database_status(self) -> Dict[str, Any]:
        """
        Get comprehensive database status information.
        
        Returns:
            Dictionary containing database status
        """
        try:
            status = {
                'database_name': self.database_name,
                'database_exists': self.database_exists(),
                'connection_string': self.database_url,
                'tables': self.get_table_info()
            }
            
            if status['database_exists']:
                # Test connection to the actual database
                engine = create_engine(self.database_url)
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT version()"))
                    version = result.fetchone()[0]
                    status['postgres_version'] = version
                    status['connection_status'] = 'Connected'
            else:
                status['postgres_version'] = 'Unknown'
                status['connection_status'] = 'Database does not exist'
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting database status: {e}")
            return {
                'error': str(e),
                'database_name': self.database_name,
                'connection_status': 'Error'
            }