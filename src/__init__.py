"""
Stock Forecast Application

A FastAPI-based application for stock data retrieval and forecasting using various APIs.
"""

__version__ = "1.0.0"
__author__ = "Stock Forecast Team"

# Import main components
from .services import YahooStockApiService, StockApiService
from .routers import yahoo_stock_router

__all__ = [
    'YahooStockApiService',
    'StockApiService', 
    'yahoo_stock_router'
]
