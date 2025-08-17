from fastapi import APIRouter, HTTPException, Query
from src.services.yahoo_stock_api_service import YahooStockApiService
from src.services.stock_api_service import StockData
from typing import List, Optional
import yfinance as yf
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/yahoo", tags=["yahoo-stocks"])

# Initialize the Yahoo stock service
yahoo_service = YahooStockApiService()

@router.get("/health")
async def health_check():
    """Health check endpoint for the Yahoo stock router"""
    return {
        "status": "healthy",
        "service": "Yahoo Stock API Router",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/stock/{symbol}")
async def get_stock_data(symbol: str):
    """
    Get current stock data for a given symbol
    
    Args:
        symbol (str): Stock symbol (e.g., AAPL, MSFT, GOOGL)
        
    Returns:
        StockData: Current stock information
    """
    try:
        logger.info(f"Fetching stock data for symbol: {symbol}")
        stock_data = yahoo_service.get(symbol)
        
        # Convert datetime to string for JSON serialization
        response_data = {
            "symbol": stock_data.symbol,
            "price": stock_data.price,
            "volume": stock_data.volume,
            "timestamp": stock_data.timestamp.isoformat(),
            "open_price": stock_data.open_price,
            "high_price": stock_data.high_price,
            "low_price": stock_data.low_price,
            "previous_close": stock_data.previous_close,
            "change": stock_data.change,
            "change_percent": stock_data.change_percent
        }
        
        logger.info(f"Successfully retrieved stock data for {symbol}")
        return response_data
        
    except ValueError as e:
        logger.error(f"Error retrieving stock data for {symbol}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/stock/{symbol}/info")
async def get_stock_info(symbol: str):
    """
    Get detailed stock information for a given symbol
    
    Args:
        symbol (str): Stock symbol (e.g., AAPL, MSFT, GOOGL)
        
    Returns:
        dict: Detailed stock information
    """
    try:
        logger.info(f"Fetching detailed stock info for symbol: {symbol}")
        stock_info = yahoo_service.get_stock_info(symbol)
        
        logger.info(f"Successfully retrieved detailed info for {symbol}")
        return {
            "symbol": stock_info.symbol,
            "info": stock_info.info,
            "timestamp": stock_info.timestamp.isoformat()
        }
        
    except ValueError as e:
        logger.error(f"Error retrieving stock info for {symbol}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving stock info for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stock info: {str(e)}")

@router.get("/stock/{symbol}/history")
async def get_stock_history(
    symbol: str,
    period: str = Query("1mo", description="Data period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"),
    interval: str = Query("1d", description="Data interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
):
    """
    Get historical stock data for a given symbol
    
    Args:
        symbol (str): Stock symbol
        period (str): Data period
        interval (str): Data interval
        
    Returns:
        dict: Historical stock data
    """
    try:
        logger.info(f"Fetching historical data for {symbol} - period: {period}, interval: {interval}")
        stock_history = yahoo_service.get_stock_history(symbol, period, interval)
        
        logger.info(f"Successfully retrieved historical data for {symbol}")
        return {
            "symbol": stock_history.symbol,
            "period": stock_history.period,
            "interval": stock_history.interval,
            "data": stock_history.data,
            "count": stock_history.count,
            "timestamp": stock_history.timestamp.isoformat()
        }
        
    except ValueError as e:
        logger.error(f"Error retrieving historical data for {symbol}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving historical data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve historical data: {str(e)}")

@router.get("/stock/{symbol}/dividends")
async def get_stock_dividends(symbol: str):
    """
    Get dividend information for a given symbol
    
    Args:
        symbol (str): Stock symbol
        
    Returns:
        dict: Dividend information
    """
    try:
        logger.info(f"Fetching dividend data for symbol: {symbol}")
        stock_dividends = yahoo_service.get_stock_dividends(symbol)
        
        logger.info(f"Successfully retrieved dividend data for {symbol}")
        return {
            "symbol": stock_dividends.symbol,
            "dividends": stock_dividends.dividends,
            "count": stock_dividends.count,
            "timestamp": stock_dividends.timestamp.isoformat()
        }
        
    except ValueError as e:
        logger.error(f"Error retrieving dividend data for {symbol}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving dividend data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dividend data: {str(e)}")

@router.get("/stock/{symbol}/splits")
async def get_stock_splits(symbol: str):
    """
    Get stock split information for a given symbol
    
    Args:
        symbol (str): Stock symbol
        
    Returns:
        dict: Stock split information
    """
    try:
        logger.info(f"Fetching split data for symbol: {symbol}")
        stock_splits = yahoo_service.get_stock_splits(symbol)
        
        logger.info(f"Successfully retrieved split data for {symbol}")
        return {
            "symbol": stock_splits.symbol,
            "splits": stock_splits.splits,
            "count": stock_splits.count,
            "timestamp": stock_splits.timestamp.isoformat()
        }
        
    except ValueError as e:
        logger.error(f"Error retrieving split data for {symbol}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving split data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve split data: {str(e)}")

@router.get("/search")
async def search_stocks(query: str = Query(..., description="Search query for stocks")):
    """
    Search for stocks based on a query
    
    Args:
        query (str): Search query
        
    Returns:
        dict: Search results
    """
    try:
        logger.info(f"Searching for stocks with query: {query}")
        stock_search = yahoo_service.search_stocks(query)
        
        logger.info(f"Successfully searched for stocks with query: {query}")
        return {
            "query": stock_search.query,
            "results": stock_search.results,
            "timestamp": stock_search.timestamp.isoformat()
        }
        
    except ValueError as e:
        logger.error(f"Error searching for stocks with query '{query}': {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error searching for stocks with query '{query}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/batch/{symbols}")
async def get_batch_stock_data(symbols: str):
    """
    Get stock data for multiple symbols (comma-separated)
    
    Args:
        symbols (str): Comma-separated list of stock symbols
        
    Returns:
        dict: Stock data for all symbols
    """
    try:
        logger.info(f"Fetching batch stock data for symbols: {symbols}")
        batch_data = yahoo_service.get_batch_stock_data(symbols)
        
        logger.info(f"Successfully retrieved batch data for {batch_data.success_count} symbols")
        return {
            "symbols": batch_data.symbols,
            "results": batch_data.results,
            "errors": batch_data.errors,
            "success_count": batch_data.success_count,
            "error_count": batch_data.error_count,
            "timestamp": batch_data.timestamp.isoformat()
        }
        
    except ValueError as e:
        logger.error(f"Error in batch request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in batch request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch request failed: {str(e)}")