# Database Setup and Stock Data Storage

This guide explains how to set up PostgreSQL for storing stock synchronized data and how to use the updated StockSyncWorker.

## PostgreSQL Configuration

The application is configured to use PostgreSQL for storing stock data. The configuration is defined in `src/config/settings.py`.

### Database Settings

```python
# PostgreSQL specific settings
postgres_host: str = "localhost"
postgres_port: int = 5432
postgres_user: str = "root"
postgres_password: str = "123456"
postgres_db: str = "STOCK_FORECAST"
postgres_ssl_mode: str = "prefer"
postgres_pool_size: int = 10
postgres_max_overflow: int = 20
postgres_pool_timeout: int = 30
postgres_pool_recycle: int = 3600
```

### Environment Variables

You can override these settings using environment variables:

```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/stock_forecast"
export POSTGRES_HOST="your_host"
export POSTGRES_USER="your_username"
export POSTGRES_PASSWORD="your_password"
export POSTGRES_DB="your_database"
```

## Database Schema

The application creates two main tables:

### 1. stock_data

Stores individual stock data records:

- `id`: Primary key
- `symbol`: Stock symbol (e.g., "FPT.VN")
- `price`: Current stock price
- `volume`: Trading volume
- `open_price`, `high_price`, `low_price`: OHLC data
- `previous_close`: Previous closing price
- `change`, `change_percent`: Price change information
- `market_cap`, `pe_ratio`, `dividend_yield`: Fundamental data
- `timestamp`: When the data was recorded
- `sync_timestamp`: When the data was synced
- `provider`: Data source (e.g., "yahoo")
- `status`: Sync status ("success" or "error")
- `error_message`: Error details if sync failed
- `is_trading_hours`: Whether sync occurred during trading hours
- `trading_day`: Day of the week

### 2. stock_sync_logs

Logs sync operations for analysis:

- `id`: Primary key
- `sync_batch_id`: Unique identifier for each sync batch
- `provider`: Data provider
- `start_time`, `end_time`: Sync operation timing
- `total_symbols`: Number of symbols to sync
- `successful_syncs`, `failed_syncs`: Success/failure counts
- `status`: Operation status ("running", "completed", "failed")
- `error_message`: Error details if operation failed

## Database Initialization

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up PostgreSQL Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE stock_forecast;

-- Create user (optional)
CREATE USER stock_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE stock_forecast TO stock_user;
```

### 3. Initialize Database Tables

```bash
cd src/database
python init_database.py
```

This will create all necessary tables in your PostgreSQL database.

## Using the Updated StockSyncWorker

### Basic Usage

```python
from src.background_workers.stock_sync_worker import StockSyncWorker, StockSyncWorkerConfig

# Create configuration
config = StockSyncWorkerConfig(
    provider="yahoo",
    frequency_minutes=5,
    stock_symbols=["FPT.VN", "VNM.VN", "TCB.VN"]
)

# Initialize worker
worker = StockSyncWorker(config)

# Start the worker
worker.start()

# Check status
status = worker.get_status()
print(f"Worker running: {status['is_running']}")
print(f"Trading time: {status['trading_time']}")

# Stop the worker
worker.stop()
```

### Data Analysis

The worker now provides methods for analyzing stored data:

```python
# Get sync statistics
stats = worker.get_sync_statistics(days=30)
print(f"Success rate: {stats.get('success_rate', 0)}%")

# Get stock history
history = worker.get_stock_history("FPT.VN", limit=100)
print(f"Historical records: {len(history)}")

# Get recent sync logs
logs = worker.get_recent_sync_logs(limit=10)
for log in logs:
    print(f"Batch {log.sync_batch_id}: {log.status}")
```

### Advanced Analysis

Use the `StockAnalyzer` class for detailed analysis:

```python
from src.analysis.stock_analysis import StockAnalyzer

analyzer = StockAnalyzer()

# Price trends analysis
trends = analyzer.get_price_trends("FPT.VN", days=30)
print(f"Price change: {trends['price_change_percent']}%")

# Sync performance metrics
metrics = analyzer.get_sync_performance_metrics(days=7)
print(f"Sync success rate: {metrics['sync_success_rate']}%")

# Trading hours analysis
trading_analysis = analyzer.get_trading_hours_analysis("FPT.VN", days=30)
print(f"Trading hours records: {trading_analysis['trading_hours']['count']}")

# Daily summary
summary = analyzer.get_daily_summary()
print(f"Today's records: {summary['total_records']}")
```

## Monitoring and Logging

### Database Monitoring

Monitor your database for:

1. **Table sizes**: Check if tables are growing as expected
2. **Index performance**: Ensure indexes are being used efficiently
3. **Connection pool**: Monitor connection usage

```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check recent sync logs
SELECT 
    sync_batch_id,
    provider,
    start_time,
    end_time,
    status,
    successful_syncs,
    failed_syncs
FROM stock_sync_logs 
ORDER BY start_time DESC 
LIMIT 10;
```

### Application Logging

The application logs all operations to help with debugging:

- Stock sync operations
- Database operations
- Error conditions
- Performance metrics

Check the logs directory for detailed information.

## Performance Considerations

### Database Optimization

1. **Indexes**: The application creates indexes on frequently queried columns
2. **Connection pooling**: Uses SQLAlchemy connection pooling for efficiency
3. **Batch operations**: Sync operations are logged in batches

### Data Retention

Consider implementing data retention policies:

```sql
-- Example: Delete data older than 1 year
DELETE FROM stock_data 
WHERE timestamp < NOW() - INTERVAL '1 year';

-- Example: Archive old sync logs
-- (Implement based on your requirements)
```

### Scaling

For high-frequency trading data:

1. **Partitioning**: Consider partitioning tables by date
2. **Compression**: Use PostgreSQL table compression
3. **Read replicas**: Use read replicas for analysis queries

## Troubleshooting

### Common Issues

1. **Connection errors**: Check PostgreSQL service and credentials
2. **Permission errors**: Ensure database user has proper privileges
3. **Table creation failures**: Check PostgreSQL version compatibility

### Debug Mode

Enable debug logging in `src/config/settings.py`:

```python
debug: bool = True
```

This will show SQL queries and detailed error information.

## Example Workflow

1. **Setup**: Initialize database and start worker
2. **Monitoring**: Watch sync operations and data collection
3. **Analysis**: Use analysis tools to gain insights
4. **Optimization**: Adjust sync frequency and symbols based on needs
5. **Maintenance**: Regular database maintenance and cleanup

The updated StockSyncWorker now provides a robust foundation for collecting, storing, and analyzing stock data with comprehensive logging and error handling.
