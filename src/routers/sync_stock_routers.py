from dataclasses import dataclass
import logging
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from src.background_workers.stock_sync_worker import StockSyncWorker, StockSyncWorkerConfig
from src.analysis.stock_analysis import StockAnalyzer
from src.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/sync-stock", tags=["sync-stock"])

# Global worker instance
_worker: Optional[StockSyncWorker] = None

# Pydantic models for request/response
class StartSyncRequest(BaseModel):
    provider: str = "yahoo"
    frequency_minutes: int = 5
    hour_start: int = 9
    hour_end: int = 16
    except_days: str = "sat,sun"
    stock_symbols: List[str] = ["FPT.VN"]

class SyncStockStatus(BaseModel):
    is_running: bool
    is_alive: bool
    config: Dict[str, Any]
    trading_time: bool
    next_sync: str
    last_sync_time: Optional[datetime] = None
    last_sync_status: Optional[str] = None
    last_sync_error: Optional[str] = None
    last_sync_error_time: Optional[datetime] = None
    last_sync_error_count: Optional[int] = None
    last_sync_error_message: Optional[str] = None

class SyncStatistics(BaseModel):
    period_days: int
    total_sync_operations: int
    total_symbols_synced: int
    successful_syncs: int
    failed_syncs: int
    success_rate: float
    total_stock_records: int
    average_records_per_sync: float

def get_worker() -> StockSyncWorker:
    """Get or create the global worker instance."""
    global _worker
    if _worker is None:
        config = StockSyncWorkerConfig(
            provider=settings.provider if hasattr(settings, 'provider') else "yahoo",
            frequency_minutes=settings.frequency_minutes,
            hour_start=settings.hour_start,
            hour_end=settings.hour_end,
            except_days=settings.except_days,
            stock_symbols=settings.stock_symbols if hasattr(settings, 'stock_symbols') else ["FPT.VN"]
        )
        _worker = StockSyncWorker(config)
        logger.info("Created new StockSyncWorker instance")
    return _worker

@router.get("/health", response_model=SyncStockStatus)
async def sync_stock_health():
    """Get the health status of the stock sync worker."""
    try:
        worker = get_worker()
        status = worker.get_status()
        
        # Get additional information from recent sync logs
        analyzer = StockAnalyzer()
        recent_logs = analyzer.get_sync_logs(limit=1)
        
        # Extract additional status information
        last_sync_info = {}
        if recent_logs:
            last_log = recent_logs[0]
            last_sync_info = {
                "last_sync_time": last_log.start_time,
                "last_sync_status": last_log.status,
                "last_sync_error": last_log.error_message,
                "last_sync_error_time": last_log.end_time if last_log.status == "failed" else None,
                "last_sync_error_count": last_log.failed_syncs,
                "last_sync_error_message": last_log.error_message
            }
        
        return SyncStockStatus(
            is_running=status["is_running"],
            is_alive=status["is_alive"],
            config=status["config"],
            trading_time=status["trading_time"],
            next_sync=status["next_sync"],
            **last_sync_info
        )
        
    except Exception as e:
        logger.error(f"Error getting sync stock health: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get worker status: {str(e)}")

@router.post("/start")
async def start_sync_stock():
    """Start the stock sync worker."""
    try:
        worker = get_worker()
        
        if worker.is_running:
            return {"message": "Stock sync worker is already running", "status": "already_running"}
        
        worker.start()
        
        return {
            "message": "Stock sync worker started successfully",
            "status": "started",
            "worker_status": worker.get_status()
        }
        
    except Exception as e:
        logger.error(f"Error starting sync stock worker: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start worker: {str(e)}")

@router.post("/stop")
async def stop_sync_stock():
    """Stop the stock sync worker."""
    try:
        worker = get_worker()
        
        if not worker.is_running:
            return {"message": "Stock sync worker is not running", "status": "not_running"}
        
        worker.stop()
        
        return {
            "message": "Stock sync worker stopped successfully",
            "status": "stopped",
            "worker_status": worker.get_status()
        }
        
    except Exception as e:
        logger.error(f"Error stopping sync stock worker: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop worker: {str(e)}")

@router.get("/status", response_model=Dict[str, Any])
async def get_sync_status():
    """Get detailed status of the stock sync worker."""
    try:
        worker = get_worker()
        return worker.get_status()
        
    except Exception as e:
        logger.error(f"Error getting sync status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.get("/statistics", response_model=SyncStatistics)
async def get_sync_statistics(days: int = Query(30, ge=1, le=365, description="Number of days to analyze")):
    """Get sync statistics for analysis."""
    try:
        worker = get_worker()
        stats = worker.get_sync_statistics(days)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return SyncStatistics(**stats)
        
    except Exception as e:
        logger.error(f"Error getting sync statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.get("/history/{symbol}")
async def get_stock_history(
    symbol: str,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return")
):
    """Get historical stock data for a specific symbol."""
    try:
        worker = get_worker()
        history = worker.get_stock_history(symbol, limit)
        
        return {
            "symbol": symbol,
            "records_count": len(history),
            "data": [
                {
                    "id": record.id,
                    "price": record.price,
                    "volume": record.volume,
                    "timestamp": record.timestamp,
                    "status": record.status,
                    "provider": record.provider,
                    "is_trading_hours": record.is_trading_hours,
                    "trading_day": record.trading_day
                }
                for record in history
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting stock history for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stock history: {str(e)}")

@router.get("/logs")
async def get_sync_logs(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of log entries to return")
):
    """Get recent sync log entries."""
    try:
        worker = get_worker()
        logs = worker.get_recent_sync_logs(limit)
        
        return {
            "logs_count": len(logs),
            "logs": [
                {
                    "id": log.id,
                    "sync_batch_id": log.sync_batch_id,
                    "provider": log.provider,
                    "start_time": log.start_time,
                    "end_time": log.end_time,
                    "total_symbols": log.total_symbols,
                    "successful_syncs": log.successful_syncs,
                    "failed_syncs": log.failed_syncs,
                    "status": log.status,
                    "error_message": log.error_message,
                    "is_trading_hours": log.is_trading_hours
                }
                for log in logs
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting sync logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get sync logs: {str(e)}")

@router.post("/restart")
async def restart_sync_stock():
    """Restart the stock sync worker."""
    try:
        worker = get_worker()
        
        # Stop if running
        if worker.is_running:
            worker.stop()
        
        # Start again
        worker.start()
        
        return {
            "message": "Stock sync worker restarted successfully",
            "status": "restarted",
            "worker_status": worker.get_status()
        }
        
    except Exception as e:
        logger.error(f"Error restarting sync stock worker: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to restart worker: {str(e)}")

@router.get("/config")
async def get_worker_config():
    """Get the current worker configuration."""
    try:
        worker = get_worker()
        status = worker.get_status()
        return {
            "configuration": status["config"],
            "trading_time": status["trading_time"],
            "next_sync": status["next_sync"]
        }
        
    except Exception as e:
        logger.error(f"Error getting worker config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")

@router.post("/config")
async def update_worker_config(request: StartSyncRequest):
    """Update the worker configuration and restart if needed."""
    try:
        global _worker
        
        # Stop current worker if running
        if _worker and _worker.is_running:
            _worker.stop()
        
        # Create new worker with updated config
        config = StockSyncWorkerConfig(
            provider=request.provider,
            frequency_minutes=request.frequency_minutes,
            hour_start=request.hour_start,
            hour_end=request.hour_end,
            except_days=request.except_days,
            stock_symbols=request.stock_symbols
        )
        
        _worker = StockSyncWorker(config)
        
        # Start the new worker
        _worker.start()
        
        return {
            "message": "Worker configuration updated and started successfully",
            "status": "updated_and_started",
            "new_config": request.dict(),
            "worker_status": _worker.get_status()
        }
        
    except Exception as e:
        logger.error(f"Error updating worker config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")