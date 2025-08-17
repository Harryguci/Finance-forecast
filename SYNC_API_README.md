# Stock Sync API Endpoints

This document describes the API endpoints for controlling and monitoring the stock sync worker.

## Base URL

```
http://127.0.0.1:5500/api/sync-stock
```

## API Endpoints

### 1. Health Check

**GET** `/health`

Get the health status of the stock sync worker.

**Response:**
```json
{
  "is_running": false,
  "is_alive": false,
  "config": {
    "provider": "yahoo",
    "frequency_minutes": 5,
    "hour_start": 9,
    "hour_end": 16,
    "except_days": ["sat", "sun"],
    "stock_symbols": ["FPT.VN"]
  },
  "trading_time": true,
  "next_sync": "Every 5 minutes during trading hours",
  "last_sync_time": "2024-01-15T10:30:00",
  "last_sync_status": "completed",
  "last_sync_error": null,
  "last_sync_error_time": null,
  "last_sync_error_count": 0,
  "last_sync_error_message": null
}
```

### 2. Start Worker

**POST** `/start`

Start the stock sync worker.

**Response:**
```json
{
  "message": "Stock sync worker started successfully",
  "status": "started",
  "worker_status": {
    "is_running": true,
    "is_alive": true,
    "config": {...},
    "trading_time": true,
    "next_sync": "Every 5 minutes during trading hours"
  }
}
```

### 3. Stop Worker

**POST** `/stop`

Stop the stock sync worker.

**Response:**
```json
{
  "message": "Stock sync worker stopped successfully",
  "status": "stopped",
  "worker_status": {
    "is_running": false,
    "is_alive": false,
    "config": {...},
    "trading_time": true,
    "next_sync": "Worker is stopped"
  }
}
```

### 4. Get Status

**GET** `/status`

Get detailed status of the stock sync worker.

**Response:**
```json
{
  "is_running": true,
  "is_alive": true,
  "config": {
    "provider": "yahoo",
    "frequency_minutes": 5,
    "hour_start": 9,
    "hour_end": 16,
    "except_days": ["sat", "sun"],
    "stock_symbols": ["FPT.VN"]
  },
  "trading_time": true,
  "next_sync": "Every 5 minutes during trading hours"
}
```

### 5. Get Statistics

**GET** `/statistics?days=30`

Get sync statistics for analysis.

**Query Parameters:**
- `days` (optional): Number of days to analyze (1-365, default: 30)

**Response:**
```json
{
  "period_days": 30,
  "total_sync_operations": 144,
  "total_symbols_synced": 1440,
  "successful_syncs": 1380,
  "failed_syncs": 60,
  "success_rate": 95.83,
  "total_stock_records": 1380,
  "average_records_per_sync": 9.58
}
```

### 6. Get Stock History

**GET** `/history/{symbol}?limit=100`

Get historical stock data for a specific symbol.

**Path Parameters:**
- `symbol`: Stock symbol (e.g., "FPT.VN")

**Query Parameters:**
- `limit` (optional): Maximum number of records (1-1000, default: 100)

**Response:**
```json
{
  "symbol": "FPT.VN",
  "records_count": 50,
  "data": [
    {
      "id": 1234,
      "price": 45.67,
      "volume": 1000000,
      "timestamp": "2024-01-15T10:30:00",
      "status": "success",
      "provider": "yahoo",
      "is_trading_hours": true,
      "trading_day": "mon"
    }
  ]
}
```

### 7. Get Sync Logs

**GET** `/logs?limit=50`

Get recent sync log entries.

**Query Parameters:**
- `limit` (optional): Maximum number of log entries (1-500, default: 50)

**Response:**
```json
{
  "logs_count": 10,
  "logs": [
    {
      "id": 567,
      "sync_batch_id": "uuid-1234-5678",
      "provider": "yahoo",
      "start_time": "2024-01-15T10:30:00",
      "end_time": "2024-01-15T10:30:15",
      "total_symbols": 1,
      "successful_syncs": 1,
      "failed_syncs": 0,
      "status": "completed",
      "error_message": null,
      "is_trading_hours": true
    }
  ]
}
```

### 8. Restart Worker

**POST** `/restart`

Restart the stock sync worker.

**Response:**
```json
{
  "message": "Stock sync worker restarted successfully",
  "status": "restarted",
  "worker_status": {
    "is_running": true,
    "is_alive": true,
    "config": {...},
    "trading_time": true,
    "next_sync": "Every 5 minutes during trading hours"
  }
}
```

### 9. Get Configuration

**GET** `/config`

Get the current worker configuration.

**Response:**
```json
{
  "configuration": {
    "provider": "yahoo",
    "frequency_minutes": 5,
    "hour_start": 9,
    "hour_end": 16,
    "except_days": ["sat", "sun"],
    "stock_symbols": ["FPT.VN"]
  },
  "trading_time": true,
  "next_sync": "Every 5 minutes during trading hours"
}
```

### 10. Update Configuration

**POST** `/config`

Update the worker configuration and restart if needed.

**Request Body:**
```json
{
  "provider": "yahoo",
  "frequency_minutes": 3,
  "hour_start": 9,
  "hour_end": 16,
  "except_days": "sat,sun",
  "stock_symbols": ["FPT.VN", "VNM.VN", "TCB.VN"]
}
```

**Response:**
```json
{
  "message": "Worker configuration updated and started successfully",
  "status": "updated_and_started",
  "new_config": {
    "provider": "yahoo",
    "frequency_minutes": 3,
    "hour_start": 9,
    "hour_end": 16,
    "except_days": "sat,sun",
    "stock_symbols": ["FPT.VN", "VNM.VN", "TCB.VN"]
  },
  "worker_status": {
    "is_running": true,
    "is_alive": true,
    "config": {...},
    "trading_time": true,
    "next_sync": "Every 3 minutes during trading hours"
  }
}
```

## Usage Examples

### Using cURL

```bash
# Check worker health
curl -X GET "http://127.0.0.1:5500/api/sync-stock/health"

# Start the worker
curl -X POST "http://127.0.0.1:5500/api/sync-stock/start"

# Stop the worker
curl -X POST "http://127.0.0.1:5500/api/sync-stock/stop"

# Get sync statistics for last 7 days
curl -X GET "http://127.0.0.1:5500/api/sync-stock/statistics?days=7"

# Update configuration
curl -X POST "http://127.0.0.1:5500/api/sync-stock/config" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "yahoo",
    "frequency_minutes": 2,
    "stock_symbols": ["FPT.VN", "VNM.VN"]
  }'
```

### Using Python requests

```python
import requests

BASE_URL = "http://127.0.0.1:5500/api/sync-stock"

# Start the worker
response = requests.post(f"{BASE_URL}/start")
if response.status_code == 200:
    print("Worker started successfully")

# Get status
response = requests.get(f"{BASE_URL}/status")
status = response.json()
print(f"Worker running: {status['is_running']}")

# Get statistics
response = requests.get(f"{BASE_URL}/statistics?days=30")
stats = response.json()
print(f"Success rate: {stats['success_rate']}%")

# Stop the worker
response = requests.post(f"{BASE_URL}/stop")
if response.status_code == 200:
    print("Worker stopped successfully")
```

### Using JavaScript/Node.js

```javascript
const BASE_URL = 'http://127.0.0.1:5500/api/sync-stock';

// Start the worker
async function startWorker() {
    try {
        const response = await fetch(`${BASE_URL}/start`, {
            method: 'POST'
        });
        const data = await response.json();
        console.log('Worker started:', data.message);
    } catch (error) {
        console.error('Error starting worker:', error);
    }
}

// Get worker status
async function getStatus() {
    try {
        const response = await fetch(`${BASE_URL}/status`);
        const status = await response.json();
        console.log('Worker status:', status);
    } catch (error) {
        console.error('Error getting status:', error);
    }
}

// Stop the worker
async function stopWorker() {
    try {
        const response = await fetch(`${BASE_URL}/stop`, {
            method: 'POST'
        });
        const data = await response.json();
        console.log('Worker stopped:', data.message);
    } catch (error) {
        console.error('Error stopping worker:', error);
    }
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200**: Success
- **400**: Bad Request (invalid parameters)
- **404**: Not Found (no data available)
- **500**: Internal Server Error

Error responses include a detail message:

```json
{
  "detail": "Failed to start worker: Database connection error"
}
```

## Testing

Use the provided test script to verify all endpoints:

```bash
python test_sync_endpoints.py
```

Make sure the FastAPI server is running before testing.

## Notes

- The worker automatically saves all synchronized stock data to PostgreSQL
- Sync operations are logged with detailed metrics
- The worker respects trading hours and excluded days
- Configuration changes require a worker restart
- All endpoints are thread-safe and handle concurrent requests

## Integration

These endpoints can be integrated with:

- Monitoring dashboards
- CI/CD pipelines
- Automated trading systems
- Data analysis tools
- Alert systems
