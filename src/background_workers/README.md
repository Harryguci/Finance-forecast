# StockSyncWorker

A background worker for syncing stock data based on configurable parameters.

## Features

- **Background Worker**: Runs as a scheduled background process
- **Configurable Frequency**: Syncs stock data at specified intervals (default: every 5 minutes)
- **Trading Hours**: Only syncs during configured trading hours (default: 9 AM - 4 PM)
- **Day Exclusions**: Excludes specified days of the week (default: Saturday and Sunday)
- **Provider Support**: Uses appropriate stock API service based on configuration
- **Multiple Symbols**: Syncs data for multiple stock symbols concurrently
- **Error Handling**: Robust error handling with logging and status reporting

## Configuration

The `StockSyncWorkerConfig` class allows you to configure:

- `provider`: Stock API provider (currently supports "yahoo")
- `frequency_minutes`: How often to sync data (in minutes)
- `hour_start`: Start of trading hours (24-hour format)
- `hour_end`: End of trading hours (24-hour format)
- `except_days`: Comma-separated list of days to exclude (e.g., "sat,sun")
- `stock_symbols`: List of stock symbols to sync

## Usage

### Basic Usage

```python
from src.background_workers.stock_sync_worker import StockSyncWorker, StockSyncWorkerConfig

# Create configuration
config = StockSyncWorkerConfig(
    provider="yahoo",
    frequency_minutes=5,
    hour_start=9,
    hour_end=16,
    except_days="sat,sun",
    stock_symbols=["FPT.VN", "VNM.VN", "TCB.VN"]
)

# Create and start worker
worker = StockSyncWorker(config)
worker.start()

# ... your application code ...

# Stop worker when done
worker.stop()
```

### Using Default Configuration

```python
# Use default configuration
worker = StockSyncWorker()
worker.start()
```

### Monitoring Worker Status

```python
# Check if worker is running
if worker.is_alive():
    print("Worker is running")
    
# Get detailed status
status = worker.get_status()
print(f"Trading time: {status['trading_time']}")
print(f"Next sync: {status['next_sync']}")
```

## Architecture

The worker runs in a separate thread and uses the `schedule` library for task scheduling. It:

1. **Initializes** with the provided configuration
2. **Selects** the appropriate stock API service
3. **Runs** a continuous loop that schedules sync jobs
4. **Checks** trading time conditions before each sync
5. **Executes** concurrent sync operations for all symbols
6. **Logs** all operations and errors
7. **Provides** status information and control methods

## Trading Time Logic

The worker only syncs data when:

- Current day is NOT in the `except_days` list
- Current time is between `hour_start` and `hour_end`
- Worker is running and healthy

## Error Handling

- **Service Errors**: Individual symbol sync failures don't stop other symbols
- **Network Issues**: Automatic retry with exponential backoff
- **Configuration Errors**: Graceful fallback to default values
- **Thread Safety**: Proper thread management and cleanup

## Logging

The worker provides comprehensive logging:

- **INFO**: Worker start/stop, sync operations, successful syncs
- **DEBUG**: Trading time checks, scheduling details
- **ERROR**: Sync failures, service errors, configuration issues

## Dependencies

- `schedule`: For task scheduling
- `asyncio`: For concurrent operations
- `threading`: For background execution
- `logging`: For operation logging

## Example Output

```
2024-01-15 10:00:00 - StockSyncWorker - INFO - Stock sync worker started
2024-01-15 10:00:00 - StockSyncWorker - INFO - Starting stock sync for 3 symbols
2024-01-15 10:00:01 - StockSyncWorker - INFO - Successfully synced FPT.VN: Price=100.5, Volume=1000000
2024-01-15 10:00:01 - StockSyncWorker - INFO - Successfully synced VNM.VN: Price=75.2, Volume=500000
2024-01-15 10:00:01 - StockSyncWorker - INFO - Successfully synced TCB.VN: Price=45.8, Volume=750000
2024-01-15 10:00:01 - StockSyncWorker - INFO - Stock sync completed: 3 successful, 0 errors
```

## Testing

Run the tests with:

```bash
python -m pytest test/test_stock_sync_worker.py -v
```

## Notes

- The worker runs as a daemon thread, so it will automatically stop when the main program exits
- Trading hours are based on the system's local timezone
- The worker gracefully handles service unavailability and network issues
- All sync operations are logged for monitoring and debugging
