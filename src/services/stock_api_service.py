from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class StockData:
    """Data class representing stock data returned by the API service."""
    symbol: str
    price: float
    volume: int
    timestamp: datetime
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    previous_close: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None

@dataclass
class StockInfo:
    """Data class representing detailed stock information."""
    symbol: str
    info: Dict[str, Any]
    timestamp: datetime

@dataclass
class StockHistory:
    """Data class representing historical stock data."""
    symbol: str
    period: str
    interval: str
    data: List[Dict[str, Any]]
    count: int
    timestamp: datetime

@dataclass
class StockDividends:
    """Data class representing stock dividend information."""
    symbol: str
    dividends: List[Dict[str, Any]]
    count: int
    timestamp: datetime

@dataclass
class StockSplits:
    """Data class representing stock split information."""
    symbol: str
    splits: List[Dict[str, Any]]
    count: int
    timestamp: datetime

@dataclass
class StockSearch:
    """Data class representing stock search results."""
    query: str
    results: List[Dict[str, Any]]
    timestamp: datetime

@dataclass
class StockBatchData:
    """Data class representing batch stock data."""
    symbols: List[str]
    results: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    success_count: int
    error_count: int
    timestamp: datetime

class StockApiService(ABC):
    def __init__(self):
        self.base_url = "https://api.stockapi.com"

    @abstractmethod
    def get(self, symbol: str) -> StockData:
        """
        Abstract method to get stock data for a given symbol.
        
        Args:
            symbol (str): The stock symbol to retrieve data for
            
        Returns:
            The stock data (implementation specific)
        """
        pass

    def get_stock_info(self, symbol: str) -> StockInfo:
        """
        Get detailed stock information for a given symbol.
        
        Args:
            symbol (str): The stock symbol to retrieve info for
            
        Returns:
            StockInfo: Detailed stock information
        """
        pass

    def get_stock_history(self, symbol: str, period: str, interval: str) -> StockHistory:
        """
        Get historical stock data for a given symbol.
        
        Args:
            symbol (str): The stock symbol
            period (str): Data period (e.g., 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval (str): Data interval (e.g., 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            StockHistory: Historical stock data
        """
        pass

    def get_stock_dividends(self, symbol: str) -> StockDividends:
        """
        Get dividend information for a given symbol.
        
        Args:
            symbol (str): The stock symbol
            
        Returns:
            StockDividends: Dividend information
        """
        pass

    def get_stock_splits(self, symbol: str) -> StockSplits:
        """
        Get stock split information for a given symbol.
        
        Args:
            symbol (str): The stock symbol
            
        Returns:
            StockSplits: Stock split information
        """
        pass

    def search_stocks(self, query: str) -> StockSearch:
        """
        Search for stocks based on a query.
        
        Args:
            query (str): Search query
            
        Returns:
            StockSearch: Search results
        """
        pass

    def get_batch_stock_data(self, symbols: str) -> StockBatchData:
        """
        Get stock data for multiple symbols (comma-separated).
        
        Args:
            symbols (str): Comma-separated list of stock symbols
            
        Returns:
            StockBatchData: Stock data for all symbols
        """
        pass