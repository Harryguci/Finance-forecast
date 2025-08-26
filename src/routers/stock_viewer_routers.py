"""
Stock Viewer Router

This module provides FastAPI endpoints for the stock viewer page, including:
- Serving the HTML page
- Providing stock data for specific symbols
- Historical data retrieval
- Real-time data updates
"""

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import logging
import os
from pathlib import Path

from src.services.stock_data_service import StockDataService
from src.services.yahoo_stock_api_service import YahooStockApiService
from src.models.stock_data import StockData
from src.database.connection import get_db_session
from sqlalchemy.orm import Session
from sqlalchemy import desc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stock-viewer", tags=["stock-viewer"])

# Initialize services
stock_data_service = StockDataService()
yahoo_service = YahooStockApiService()

# Define the symbols we're tracking
TRACKED_SYMBOLS = ['FPT.VN', 'GOOG', 'SSI.VN']

@router.get("/", response_class=HTMLResponse)
async def get_stock_viewer_page():
    """
    Serve the main stock viewer HTML page
    """
    try:
        # Get the path to the HTML file
        pages_dir = Path(__file__).parent.parent / "pages"
        html_file = pages_dir / "stock_viewer.html"
        
        if not html_file.exists():
            raise HTTPException(status_code=404, detail="Stock viewer page not found")
        
        # Read and return the HTML content
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Error serving stock viewer page: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to serve stock viewer page")

@router.get("/static/css")
async def get_css():
    """Serve the CSS file"""
    try:
        pages_dir = Path(__file__).parent.parent / "pages"
        css_file = pages_dir / "stock_viewer.css"
        
        if not css_file.exists():
            raise HTTPException(status_code=404, detail="CSS file not found")
        
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        return Response(content=css_content, media_type="text/css")
        
    except Exception as e:
        logger.error(f"Error serving CSS file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to serve CSS file")

@router.get("/static/js")
async def get_js():
    """Serve the JavaScript file"""
    try:
        pages_dir = Path(__file__).parent.parent / "pages"
        js_file = pages_dir / "stock_viewer.js"
        
        if not js_file.exists():
            raise HTTPException(status_code=404, detail="JavaScript file not found")
        
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        return Response(content=js_content, media_type="application/javascript")
        
    except Exception as e:
        logger.error(f"Error serving JavaScript file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to serve JavaScript file")

@router.get("/api/stock-data")
async def get_stock_data(
    symbols: Optional[str] = Query(None, description="Comma-separated list of stock symbols"),
    time_range: str = Query("1d", description="Time range: 1d, 1w, 1m, 3m"),
    limit: Optional[int] = Query(None, ge=1, description="Max historical records per symbol to return")
):
    """
    Get all historical stock data for tracked symbols
    
    Args:
        symbols: Optional comma-separated list of symbols (defaults to tracked symbols)
        time_range: Time range for data retrieval
        
    Returns:
        dict: All historical stock data for requested symbols
    """
    try:
        # Use provided symbols or default to tracked symbols
        if symbols:
            symbol_list = [s.strip() for s in symbols.split(',')]
        else:
            symbol_list = TRACKED_SYMBOLS
        
        logger.info(f"Fetching all historical stock data for symbols: {symbol_list}")
        
        # Get all historical data from database
        db_data = await get_all_stock_data_from_db(symbol_list, limit=limit)
        
        # If we don't have recent data, fetch from Yahoo API
        current_time = datetime.now(timezone.utc)
        data_to_return = {}
        
        for symbol in symbol_list:
            if symbol in db_data and db_data[symbol]:
                # Convert all historical records to dictionaries
                data_to_return[symbol] = [convert_stock_data_to_dict(record) for record in db_data[symbol]]
                
                # Check if we have recent data (within last 5 minutes)
                latest_record = db_data[symbol][0]  # First record is most recent due to desc ordering
                data_age = current_time - latest_record.timestamp
                if data_age.total_seconds() < 300:  # 5 minutes
                    continue
            
            # Fetch fresh data from Yahoo API if we don't have recent data
            try:
                fresh_data = yahoo_service.get(symbol)
                fresh_dict = convert_stock_data_to_dict(fresh_data)
                
                # Save to database
                stock_data_service.save_stock_data(
                    fresh_dict,
                    provider="yahoo"
                )
                
                # Add fresh data to the beginning of the list
                if symbol in data_to_return:
                    data_to_return[symbol].insert(0, fresh_dict)
                else:
                    data_to_return[symbol] = [fresh_dict]
                
            except Exception as e:
                logger.warning(f"Failed to fetch fresh data for {symbol}: {str(e)}")
                # Use database data if available, even if old
                if symbol not in data_to_return and symbol in db_data:
                    data_to_return[symbol] = [convert_stock_data_to_dict(record) for record in db_data[symbol]]
                elif symbol not in data_to_return:
                    data_to_return[symbol] = [create_error_stock_data(symbol, str(e))]
        
        logger.info(f"Successfully retrieved historical stock data for {len(data_to_return)} symbols")
        return {
            "data": data_to_return,
            "timestamp": current_time.isoformat(),
            "time_range": time_range,
            "symbols": symbol_list
        }
        
    except Exception as e:
        logger.error(f"Error retrieving stock data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stock data: {str(e)}")

@router.get("/api/stock-data/{symbol}")
async def get_single_stock_data(
    symbol: str,
    time_range: str = Query("1d", description="Time range: 1d, 1w, 1m, 3m")
):
    """
    Get stock data for a specific symbol
    
    Args:
        symbol: Stock symbol
        time_range: Time range for data retrieval
        
    Returns:
        dict: Stock data for the specified symbol
    """
    try:
        logger.info(f"Fetching stock data for symbol: {symbol}")
        
        # Get latest data from database
        db_data = await get_latest_stock_data_from_db([symbol])
        
        if symbol in db_data:
            # Ensure both datetimes are timezone-aware
            db_timestamp = db_data[symbol].timestamp
            if db_timestamp and db_timestamp.tzinfo is None:
                db_timestamp = db_timestamp.replace(tzinfo=timezone.utc)
            
            data_age = datetime.now(timezone.utc) - db_timestamp
            if data_age.total_seconds() < 300:  # 5 minutes
                return {
                    "data": convert_stock_data_to_dict(db_data[symbol]),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "time_range": time_range,
                    "source": "database"
                }
        
        # Fetch fresh data from Yahoo API
        try:
            fresh_data = yahoo_service.get(symbol)
            stock_dict = convert_stock_data_to_dict(fresh_data)
            
            # Save to database
            stock_data_service.save_stock_data(stock_dict, provider="yahoo")
            
            return {
                "data": stock_dict,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "time_range": time_range,
                "source": "yahoo_api"
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {str(e)}")
            if symbol in db_data:
                return {
                    "data": convert_stock_data_to_dict(db_data[symbol]),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "time_range": time_range,
                    "source": "database_old",
                    "warning": f"Using cached data: {str(e)}"
                }
            else:
                raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
        
    except Exception as e:
        logger.error(f"Error retrieving stock data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stock data: {str(e)}")

@router.get("/api/stock-data/{symbol}/history")
async def get_stock_history(
    symbol: str,
    period: str = Query("1mo", description="Data period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"),
    interval: str = Query("1d", description="Data interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
):
    """
    Get historical stock data for a symbol
    
    Args:
        symbol: Stock symbol
        period: Data period
        interval: Data interval
        
    Returns:
        dict: Historical stock data
    """
    try:
        logger.info(f"Fetching historical data for {symbol}, period: {period}, interval: {interval}")
        
        # Get historical data from Yahoo API
        historical_data = yahoo_service.get_stock_history(symbol, period, interval)
        
        return {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data": historical_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving historical data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve historical data: {str(e)}")

@router.get("/api/symbols")
async def get_tracked_symbols():
    """
    Get list of tracked stock symbols
    
    Returns:
        dict: List of tracked symbols
    """
    return {
        "symbols": TRACKED_SYMBOLS,
        "count": len(TRACKED_SYMBOLS),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/api/status")
async def get_sync_status():
    """
    Get current sync status and data freshness
    
    Returns:
        dict: Sync status information
    """
    try:
        # Get latest data from database
        db_data = await get_latest_stock_data_from_db(TRACKED_SYMBOLS)
        
        current_time = datetime.now(timezone.utc)
        status_info = {
            "timestamp": current_time.isoformat(),
            "symbols": {},
            "overall_status": "healthy"
        }
        
        for symbol in TRACKED_SYMBOLS:
            if symbol in db_data:
                # Ensure both datetimes are timezone-aware
                db_timestamp = db_data[symbol].timestamp
                if db_timestamp and db_timestamp.tzinfo is None:
                    db_timestamp = db_timestamp.replace(tzinfo=timezone.utc)
                
                data_age = current_time - db_timestamp
                age_minutes = data_age.total_seconds() / 60
                
                status_info["symbols"][symbol] = {
                    "last_update": db_timestamp.isoformat(),
                    "age_minutes": round(age_minutes, 2),
                    "status": "fresh" if age_minutes < 5 else "stale",
                    "provider": db_data[symbol].provider
                }
                
                if age_minutes > 15:  # More than 15 minutes old
                    status_info["overall_status"] = "warning"
            else:
                status_info["symbols"][symbol] = {
                    "last_update": None,
                    "age_minutes": None,
                    "status": "missing",
                    "provider": None
                }
                status_info["overall_status"] = "error"
        
        return status_info
        
    except Exception as e:
        logger.error(f"Error getting sync status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get sync status: {str(e)}")

# Helper functions

async def get_latest_stock_data_from_db(symbols: List[str]) -> Dict[str, StockData]:
    """Get the latest stock data from database for given symbols"""
    try:
        session = next(get_db_session())
        
        # Get latest data for each symbol
        latest_data = {}
        for symbol in symbols:
            latest_record = session.query(StockData)\
                .filter(StockData.symbol == symbol)\
                .order_by(desc(StockData.timestamp))\
                .first()
            
            if latest_record:
                latest_data[symbol] = latest_record
        
        return latest_data
        
    except Exception as e:
        logger.error(f"Error getting data from database: {str(e)}")
        return {}
    finally:
        if session:
            session.close()

async def get_all_stock_data_from_db(symbols: List[str], limit: Optional[int] = 50) -> Dict[str, List[StockData]]:
    """Get historical stock data from database for given symbols with optional limit per symbol"""
    try:
        session = next(get_db_session())
        
        all_data = {}
        for symbol in symbols:
            query = session.query(StockData)\
                .filter(StockData.symbol == symbol)\
                .order_by(desc(StockData.timestamp))
            if limit is not None:
                query = query.limit(limit)
            historical_records = query.all()
            
            if historical_records:
                all_data[symbol] = historical_records
        
        return all_data
        
    except Exception as e:
        logger.error(f"Error getting historical data from database: {str(e)}")
        return {}
    finally:
        if session:
            session.close()

def convert_stock_data_to_dict(stock_data: StockData) -> Dict[str, Any]:
    """Convert StockData model to dictionary"""
    return {
        "symbol": stock_data.symbol,
        "price": stock_data.price,
        "volume": stock_data.volume,
        "open_price": stock_data.open_price,
        "high_price": stock_data.high_price,
        "low_price": stock_data.low_price,
        "previous_close": stock_data.previous_close,
        "change": stock_data.change,
        "change_percent": stock_data.change_percent,
        "market_cap": stock_data.market_cap,
        "pe_ratio": stock_data.pe_ratio,
        "dividend_yield": stock_data.dividend_yield,
        "timestamp": stock_data.timestamp.isoformat() if stock_data.timestamp else None,
        "sync_timestamp": stock_data.sync_timestamp.isoformat() if stock_data.sync_timestamp else None,
        "provider": stock_data.provider,
        "status": stock_data.status,
        "error_message": stock_data.error_message,
        "is_trading_hours": stock_data.is_trading_hours,
        "trading_day": stock_data.trading_day
    }

def create_error_stock_data(symbol: str, error_message: str) -> Dict[str, Any]:
    """Create error stock data when API fails"""
    return {
        "symbol": symbol,
        "price": None,
        "volume": None,
        "open_price": None,
        "high_price": None,
        "low_price": None,
        "previous_close": None,
        "change": None,
        "change_percent": None,
        "market_cap": None,
        "pe_ratio": None,
        "dividend_yield": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sync_timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": "yahoo",
        "status": "error",
        "error_message": error_message,
        "is_trading_hours": True,
        "trading_day": datetime.now(timezone.utc).strftime("%a")
    }

@router.get("/test")
async def get_test_page():
    """Serve a test page to verify static files are working"""
    try:
        # Look for test file in the root directory
        root_dir = Path(__file__).parent.parent.parent
        test_file = root_dir / "test_static_files.html"
        
        if not test_file.exists():
            raise HTTPException(status_code=404, detail="Test file not found")
        
        with open(test_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Error serving test page: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to serve test page")

@router.get("/health")
async def health_check():
    """Health check endpoint for the stock viewer router"""
    return {
        "status": "healthy",
        "service": "Stock Viewer Router",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tracked_symbols": TRACKED_SYMBOLS
    }