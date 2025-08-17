# DatabaseMigrator

The `DatabaseMigrator` class is a comprehensive utility for managing PostgreSQL databases in the stock forecast application. It handles database creation, table initialization, and migration management.

## Features

- **Database Existence Check**: Verify if a database exists before attempting operations
- **Automatic Database Creation**: Create databases if they don't exist
- **Table Management**: Create all tables defined in SQLAlchemy models
- **Migration Support**: Framework for running database migrations
- **Status Monitoring**: Get comprehensive database status information
- **Error Handling**: Robust error handling with detailed logging

## Usage

### Basic Usage

```python
from src.migrator.database_migrator import DatabaseMigrator

# Initialize migrator with default settings
migrator = DatabaseMigrator()

# Complete database initialization (recommended for first-time setup)
if migrator.initialize_database():
    print("Database setup completed successfully!")
else:
    print("Database setup failed!")
```

### Step-by-Step Usage

```python
from src.migrator.database_migrator import DatabaseMigrator

migrator = DatabaseMigrator()

# 1. Check if database exists
if not migrator.database_exists():
    print("Database does not exist, creating...")
    
    # 2. Create database
    if migrator.create_database():
        print("Database created successfully!")
    else:
        print("Failed to create database!")
        exit(1)

# 3. Create tables
if migrator.create_tables():
    print("Tables created successfully!")
else:
    print("Failed to create tables!")
    exit(1)

# 4. Run migrations
if migrator.run_migrations():
    print("Migrations completed successfully!")
else:
    print("Failed to run migrations!")
    exit(1)
```

### Database Status

```python
# Get comprehensive database status
status = migrator.get_database_status()

print(f"Database: {status['database_name']}")
print(f"Exists: {status['database_exists']}")
print(f"Connection: {status['connection_status']}")
print(f"PostgreSQL Version: {status['postgres_version']}")

# Show table information
for table_name, table_info in status['tables'].items():
    print(f"Table: {table_name}")
    print(f"  Columns: {table_info['columns']}")
    print(f"  Indexes: {table_info['indexes']}")
```

### Advanced Operations

```python
# Reset database (WARNING: This will delete all data!)
if migrator.reset_database():
    print("Database reset completed!")

# Custom database URL
custom_migrator = DatabaseMigrator("postgresql://user:pass@host:port/dbname")
```

## Methods

### Core Methods

- `database_exists()`: Check if target database exists
- `create_database()`: Create database if it doesn't exist
- `create_tables()`: Create all tables defined in models
- `run_migrations()`: Run database migrations
- `initialize_database()`: Complete initialization process

### Utility Methods

- `get_table_info()`: Get information about existing tables
- `get_database_status()`: Get comprehensive database status
- `reset_database()`: Reset database (drop all tables and recreate)

## Configuration

The `DatabaseMigrator` uses configuration from `src.config.settings`:

- `postgres_host`: PostgreSQL server host
- `postgres_port`: PostgreSQL server port
- `postgres_user`: Database username
- `postgres_password`: Database password
- `postgres_db`: Database name
- `postgres_ssl_mode`: SSL mode for connections

## Example Script

Run the example script to see the migrator in action:

```bash
cd src/migrator
python example_usage.py
```

This will:
1. Check current database status
2. Initialize the database (create if needed, create tables, run migrations)
3. Display updated status and table information

## Error Handling

The migrator includes comprehensive error handling:

- Connection failures are logged and handled gracefully
- Database creation errors are caught and reported
- Table creation failures are logged with details
- All operations return boolean success indicators

## Dependencies

- `psycopg2`: PostgreSQL adapter for Python
- `sqlalchemy`: SQL toolkit and ORM
- `logging`: Python logging module

## Security Notes

- Database credentials are read from environment variables or settings
- SSL mode is configurable for secure connections
- Connection strings are parsed safely to extract database names

## Troubleshooting

### Common Issues

1. **Connection Refused**: Check if PostgreSQL is running and accessible
2. **Authentication Failed**: Verify username/password in settings
3. **Permission Denied**: Ensure user has CREATE DATABASE privileges
4. **Database Already Exists**: This is not an error - the migrator handles it gracefully

### Debug Mode

Enable debug logging to see detailed operation information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- Versioned migration support
- Rollback capabilities
- Schema comparison tools
- Automated backup before migrations
- Support for other database types
