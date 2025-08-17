# Stock Forecast API

A comprehensive FastAPI-based application for stock data retrieval and forecasting using Yahoo Finance API.

## Features

- **Real-time Stock Data**: Get current stock prices, volume, and market data
- **Historical Data**: Retrieve historical OHLCV data with customizable periods and intervals
- **Dividend Information**: Access dividend history and payout data
- **Stock Splits**: Get information about stock splits
- **Stock Search**: Search for stocks by company name or symbol
- **Batch Operations**: Retrieve data for multiple stocks in a single request
- **Comprehensive Error Handling**: Robust error handling with detailed logging

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd stock_forecast
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

Start the FastAPI server:
```bash
python -m src.main
```

The server will run on `http://localhost:5500`

### API Endpoints

#### Base URL: `/api/yahoo`

#### 1. Health Check
```
GET /api/yahoo/health
```
Returns the health status of the Yahoo stock router.

#### 2. Get Stock Data
```
GET /api/yahoo/stock/{symbol}
```
Returns current stock data for a given symbol.

**Example:**
```bash
curl http://localhost:5500/api/yahoo/stock/AAPL
```

**Response:**
```json
{
  "symbol": "AAPL",
  "price": 150.25,
  "volume": 1234567,
  "timestamp": "2024-01-15T10:30:00",
  "open_price": 149.50,
  "high_price": 151.00,
  "low_price": 148.75,
  "previous_close": 149.00,
  "change": 1.25,
  "change_percent": 0.84
}
```

#### 3. Get Detailed Stock Info
```
GET /api/yahoo/stock/{symbol}/info
```
Returns comprehensive stock information including company details, financial metrics, and market data.

**Example:**
```bash
curl http://localhost:5500/api/yahoo/stock/MSFT/info
```

#### 4. Get Historical Data
```
GET /api/yahoo/stock/{symbol}/history?period={period}&interval={interval}
```

**Parameters:**
- `period`: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
- `interval`: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

**Example:**
```bash
curl "http://localhost:5500/api/yahoo/stock/GOOGL/history?period=1mo&interval=1d"
```

#### 5. Get Dividends
```
GET /api/yahoo/stock/{symbol}/dividends
```
Returns dividend history for a stock.

**Example:**
```bash
curl http://localhost:5500/api/yahoo/stock/KO/dividends
```

#### 6. Get Stock Splits
```
GET /api/yahoo/stock/{symbol}/splits
```
Returns stock split history.

**Example:**
```bash
curl http://localhost:5500/api/yahoo/stock/AAPL/splits
```

#### 7. Search Stocks
```
GET /api/yahoo/search?query={query}
```
Search for stocks by company name or symbol.

**Example:**
```bash
curl "http://localhost:5500/api/yahoo/search?query=Apple"
```

#### 8. Batch Stock Data
```
GET /api/yahoo/batch/{symbols}
```
Get stock data for multiple symbols (comma-separated, max 10 symbols).

**Example:**
```bash
curl http://localhost:5500/api/yahoo/batch/AAPL,MSFT,GOOGL
```

## Testing

### Using the Test Script

A comprehensive test script is provided to test all endpoints:

```bash
python test_yahoo_api.py
```

**Prerequisites:**
- The FastAPI server must be running
- `requests` library must be installed

### Manual Testing

You can also test endpoints manually using curl, Postman, or any HTTP client:

```bash
# Test health check
curl http://localhost:5500/api/yahoo/health

# Test stock data retrieval
curl http://localhost:5500/api/yahoo/stock/AAPL

# Test with query parameters
curl "http://localhost:5500/api/yahoo/stock/GOOGL/history?period=1wk&interval=1d"
```

## API Documentation

Once the server is running, you can access:

- **Interactive API Docs**: `http://localhost:5500/docs`
- **ReDoc Documentation**: `http://localhost:5500/redoc`
- **OpenAPI Schema**: `http://localhost:5500/openapi.json`

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid parameters or symbols
- **500 Internal Server Error**: Server-side errors or API failures
- **Detailed Error Messages**: Clear error descriptions for debugging

## Logging

All API operations are logged with:
- Request details
- Response status
- Error information
- Timestamps

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **yfinance**: Yahoo Finance API client
- **uvicorn**: ASGI server
- **requests**: HTTP client (for testing)

## Architecture

```
src/
├── main.py                 # FastAPI application entry point
├── routers/
│   └── yahoo_stock_routes.py  # Yahoo stock API endpoints
├── services/
│   ├── stock_api_service.py   # Abstract base service
│   └── yahoo_stock_api_service.py  # Yahoo Finance implementation
└── models/                 # Data models
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the API documentation
2. Review the error logs
3. Open an issue in the repository

## Future Enhancements

- Real-time WebSocket support
- Caching layer for improved performance
- Rate limiting and API key management
- Additional data sources
- Machine learning forecasting models
