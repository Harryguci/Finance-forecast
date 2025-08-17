from src.services.stock_api_service import (
    StockApiService, StockData, StockInfo, StockHistory, 
    StockDividends, StockSplits, StockSearch, StockBatchData
)
import yfinance as yf
from datetime import datetime
from typing import Optional, List, Dict, Any

class YahooStockApiService(StockApiService):
    def __init__(self):
        super().__init__()
        self.base_url = "https://finance.yahoo.com"
    
    def get(self, symbol: str) -> StockData:
        """
        Get stock data from Yahoo Finance API.
        
        Args:
            symbol (str): The stock symbol to retrieve data for
            
        Returns:
            StockData: The stock data from Yahoo Finance
            
        Raises:
            ValueError: If symbol is invalid or data cannot be retrieved
        """
        try:
            # Create a Ticker object for the symbol
            ticker = yf.Ticker(symbol)
            
            # Get current stock info
            info = ticker.info
            
            # Get current price and volume
            current_price = info.get('currentPrice', 0.0)
            volume = info.get('volume', 0)
            
            # Get OHLC data
            open_price = info.get('open', None)
            high_price = info.get('dayHigh', None)
            low_price = info.get('dayLow', None)
            previous_close = info.get('previousClose', None)
            
            # Calculate change and change percent
            change = None
            change_percent = None
            if previous_close and current_price:
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
            
            # Create and return StockData object
            return StockData(
                symbol=symbol.upper(),
                price=current_price,
                volume=volume,
                timestamp=datetime.now(),
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                previous_close=previous_close,
                change=change,
                change_percent=change_percent
            )
            
        except Exception as e:
            raise ValueError(f"Failed to retrieve stock data for {symbol}: {str(e)}")

    def get_stock_info(self, symbol: str) -> StockInfo:
        """
        Get detailed stock information from Yahoo Finance API.
        
        Args:
            symbol (str): The stock symbol to retrieve info for
            
        Returns:
            StockInfo: Detailed stock information
            
        Raises:
            ValueError: If symbol is invalid or data cannot be retrieved
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Filter out None values and convert to serializable format
            filtered_info = {}
            for key, value in info.items():
                if value is not None:
                    if isinstance(value, (int, float, str, bool)):
                        filtered_info[key] = value
                    elif hasattr(value, 'isoformat'):  # Handle datetime objects
                        filtered_info[key] = value.isoformat()
            
            return StockInfo(
                symbol=symbol.upper(),
                info=filtered_info,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            raise ValueError(f"Failed to retrieve stock info for {symbol}: {str(e)}")

    def get_stock_history(self, symbol: str, period: str, interval: str) -> StockHistory:
        """
        Get historical stock data from Yahoo Finance API.
        
        Args:
            symbol (str): The stock symbol
            period (str): Data period (e.g., 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval (str): Data interval (e.g., 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            StockHistory: Historical stock data
            
        Raises:
            ValueError: If symbol is invalid or data cannot be retrieved
        """
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period=period, interval=interval)
            
            # Convert DataFrame to serializable format
            history_data = []
            for index, row in history.iterrows():
                history_data.append({
                    "date": index.isoformat(),
                    "open": float(row['Open']) if 'Open' in row else None,
                    "high": float(row['High']) if 'High' in row else None,
                    "low": float(row['Low']) if 'Low' in row else None,
                    "close": float(row['Close']) if 'Close' in row else None,
                    "volume": int(row['Volume']) if 'Volume' in row else None
                })
            
            return StockHistory(
                symbol=symbol.upper(),
                period=period,
                interval=interval,
                data=history_data,
                count=len(history_data),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            raise ValueError(f"Failed to retrieve historical data for {symbol}: {str(e)}")

    def get_stock_dividends(self, symbol: str) -> StockDividends:
        """
        Get dividend information from Yahoo Finance API.
        
        Args:
            symbol (str): The stock symbol
            
        Returns:
            StockDividends: Dividend information
            
        Raises:
            ValueError: If symbol is invalid or data cannot be retrieved
        """
        try:
            ticker = yf.Ticker(symbol)
            dividends = ticker.dividends
            
            # Convert Series to serializable format
            dividend_data = []
            for date, amount in dividends.items():
                dividend_data.append({
                    "date": date.isoformat(),
                    "amount": float(amount)
                })
            
            return StockDividends(
                symbol=symbol.upper(),
                dividends=dividend_data,
                count=len(dividend_data),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            raise ValueError(f"Failed to retrieve dividend data for {symbol}: {str(e)}")

    def get_stock_splits(self, symbol: str) -> StockSplits:
        """
        Get stock split information from Yahoo Finance API.
        
        Args:
            symbol (str): The stock symbol
            
        Returns:
            StockSplits: Stock split information
            
        Raises:
            ValueError: If symbol is invalid or data cannot be retrieved
        """
        try:
            ticker = yf.Ticker(symbol)
            splits = ticker.splits
            
            # Convert Series to serializable format
            split_data = []
            for date, ratio in splits.items():
                split_data.append({
                    "date": date.isoformat(),
                    "ratio": float(ratio)
                })
            
            return StockSplits(
                symbol=symbol.upper(),
                splits=split_data,
                count=len(split_data),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            raise ValueError(f"Failed to retrieve split data for {symbol}: {str(e)}")

    def search_stocks(self, query: str) -> StockSearch:
        """
        Search for stocks based on a query using Yahoo Finance API.
        
        Args:
            query (str): Search query
            
        Returns:
            StockSearch: Search results
            
        Raises:
            ValueError: If search fails
        """
        try:
            ticker = yf.Ticker(query)
            info = ticker.info
            
            if not info or 'symbol' not in info:
                return StockSearch(
                    query=query,
                    results=[],
                    timestamp=datetime.now()
                )
            
            # Return basic info for the found stock
            result = {
                "symbol": info.get('symbol', query.upper()),
                "name": info.get('longName', info.get('shortName', 'Unknown')),
                "exchange": info.get('exchange', 'Unknown'),
                "type": info.get('quoteType', 'Unknown')
            }
            
            return StockSearch(
                query=query,
                results=[result],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            raise ValueError(f"Search failed for query '{query}': {str(e)}")

    def get_batch_stock_data(self, symbols: str) -> StockBatchData:
        """
        Get stock data for multiple symbols (comma-separated) from Yahoo Finance API.
        
        Args:
            symbols (str): Comma-separated list of stock symbols
            
        Returns:
            StockBatchData: Stock data for all symbols
            
        Raises:
            ValueError: If no valid symbols provided or batch request fails
        """
        try:
            symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
            
            if not symbol_list:
                raise ValueError("No valid symbols provided")
            
            if len(symbol_list) > 10:
                raise ValueError("Maximum 10 symbols allowed per request")
            
            results = []
            errors = []
            
            for symbol in symbol_list:
                try:
                    stock_data = self.get(symbol)
                    results.append({
                        "symbol": stock_data.symbol,
                        "price": stock_data.price,
                        "volume": stock_data.volume,
                        "timestamp": stock_data.timestamp.isoformat(),
                        "change": stock_data.change,
                        "change_percent": stock_data.change_percent
                    })
                except Exception as e:
                    errors.append({
                        "symbol": symbol,
                        "error": str(e)
                    })
            
            return StockBatchData(
                symbols=symbol_list,
                results=results,
                errors=errors,
                success_count=len(results),
                error_count=len(errors),
                timestamp=datetime.now()
            )
            
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Batch request failed: {str(e)}")


