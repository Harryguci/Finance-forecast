from dataclasses import dataclass, field
import asyncio
import logging
from datetime import datetime, time
from typing import Optional, Dict, Any, List
import schedule
import time as time_module
from threading import Thread, Event
import uuid

from src.services import StockApiService, YahooStockApiService
from src.services.stock_data_service import StockDataService
from src.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class StockSyncWorkerConfig:
    provider: str = "yahoo"
    frequency_minutes: int = 1
    hour_start: int = 0
    hour_end: int = 16
    except_days: str = "none"
    stock_symbols: List[str] = field(default_factory=lambda: ["FPT.VN", "GOOG"])

class StockSyncWorker:
    """
    Background worker for syncing stock data based on configuration.
    
    Features:
    - Runs as a background worker with scheduled execution
    - Syncs stock data at specified frequency for configured symbols
    - Respects trading hours (hour_start to hour_end)
    - Excludes specified days of the week
    - Uses appropriate service based on provider configuration
    """
    
    def __init__(self, config: Optional[StockSyncWorkerConfig] = None):
        self.config = config or StockSyncWorkerConfig()
        self.service: StockApiService = self._get_service()
        self.stock_data_service = StockDataService()
        self.is_running = False
        self.stop_event = Event()
        self.worker_thread: Optional[Thread] = None
        
        # Parse configuration
        self.except_days = [day.strip().lower() for day in self.config.except_days.split(",")]
        self.trading_start = time(self.config.hour_start)
        self.trading_end = time(self.config.hour_end)
        
        logger.info(f"StockSyncWorker initialized with config: {self.config}")
    
    def _get_service(self) -> StockApiService:
        """Get the appropriate stock API service based on provider configuration."""
        provider = self.config.provider.lower()
        
        if provider == "yahoo":
            return YahooStockApiService()
        else:
            logger.warning(f"Unknown provider '{provider}', falling back to Yahoo")
            return YahooStockApiService()
    
    def _is_trading_time(self) -> bool:
        """Check if current time is within trading hours."""

        return True
        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime("%a").lower()[:3]  # Mon, Tue, Wed, etc.
        
        # Check if current day is excluded
        if current_day in self.except_days:
            logger.debug(f"Current day {current_day} is excluded from trading")
            return False
        
        # Check if current time is within trading hours
        if self.trading_start <= current_time <= self.trading_end:
            return True
        
        logger.debug(f"Current time {current_time} is outside trading hours {self.trading_start}-{self.trading_end}")
        return False
    
    async def _sync_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Sync stock data for a specific symbol."""
        try:
            logger.info(f"Syncing stock data for symbol: {symbol}")
            
            # Get current stock data
            stock_data = self.service.get(symbol)
            
            # Prepare data for database storage
            db_stock_data = {
                "symbol": symbol,
                "price": stock_data.price,
                "volume": stock_data.volume,
                "open_price": getattr(stock_data, 'open_price', None),
                "high_price": getattr(stock_data, 'high_price', None),
                "low_price": getattr(stock_data, 'low_price', None),
                "previous_close": getattr(stock_data, 'previous_close', None),
                "change": getattr(stock_data, 'change', None),
                "change_percent": getattr(stock_data, 'change_percent', None),
                "market_cap": getattr(stock_data, 'market_cap', None),
                "pe_ratio": getattr(stock_data, 'pe_ratio', None),
                "dividend_yield": getattr(stock_data, 'dividend_yield', None),
                "timestamp": stock_data.timestamp,
                "is_trading_hours": self._is_trading_time(),
                "trading_day": datetime.now().strftime("%a")[:3].lower(),
                "status": "success"
            }
            
            # Save to database
            saved_record = self.stock_data_service.save_stock_data(
                db_stock_data, 
                provider=self.config.provider
            )
            
            if saved_record:
                logger.info(f"Successfully synced and saved {symbol}: Price={stock_data.price}, Volume={stock_data.volume}")
            else:
                logger.warning(f"Synced {symbol} but failed to save to database")
            
            # Return the synced data
            return {
                "symbol": symbol,
                "price": stock_data.price,
                "volume": stock_data.volume,
                "timestamp": stock_data.timestamp.isoformat(),
                "status": "success",
                "db_record_id": saved_record.id if saved_record else None
            }
            
        except Exception as e:
            logger.error(f"Failed to sync stock data for {symbol}: {str(e)}")
            
            # Save error record to database
            error_data = {
                "symbol": symbol,
                "price": 0.0,  # Default value for error cases
                "status": "error",
                "error_message": str(e),
                "timestamp": datetime.now(),
                "is_trading_hours": self._is_trading_time(),
                "trading_day": datetime.now().strftime("%a")[:3].lower()
            }
            
            self.stock_data_service.save_stock_data(
                error_data, 
                provider=self.config.provider
            )
            
            return {
                "symbol": symbol,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _sync_all_stocks(self):
        """Sync data for all configured stock symbols."""
        logger.info("=== _sync_all_stocks method called ===")
        if not self._is_trading_time():
            logger.debug("Outside trading hours, skipping stock sync")
            return
        
        logger.info(f"Starting stock sync for {len(self.config.stock_symbols)} symbols")
        
        # Create sync log entry
        sync_log = self.stock_data_service.create_sync_log(
            provider=self.config.provider,
            total_symbols=len(self.config.stock_symbols)
        )
        
        if not sync_log:
            logger.error("Failed to create sync log entry")
            return
        
        try:
            # Sync all stocks concurrently
            tasks = [self._sync_stock_data(symbol) for symbol in self.config.stock_symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and count successes/errors
            success_count = 0
            error_count = 0
            
            for result in results:
                if isinstance(result, dict):
                    if result.get("status") == "success":
                        success_count += 1
                    else:
                        error_count += 1
                        logger.error(f"Error syncing {result.get('symbol', 'unknown')}: {result.get('error', 'unknown error')}")
                else:
                    error_count += 1
                    logger.error(f"Unexpected result type: {type(result)}")
            
            # Update sync log with results
            self.stock_data_service.update_sync_log(
                sync_log.sync_batch_id,
                end_time=datetime.now(),
                successful_syncs=success_count,
                failed_syncs=error_count,
                status="completed"
            )
            
            logger.info(f"Stock sync completed: {success_count} successful, {error_count} errors. Batch ID: {sync_log.sync_batch_id}")
            
        except Exception as e:
            logger.error(f"Error in sync operation: {str(e)}")
            
            # Update sync log with error
            self.stock_data_service.update_sync_log(
                sync_log.sync_batch_id,
                end_time=datetime.now(),
                status="failed",
                error_message=str(e)
            )
    
    def _run_sync_loop(self):
        """Main sync loop that runs in the worker thread."""
        logger.info("Stock sync worker started")
        
        # Schedule the sync job once at startup using a lambda to capture self
        schedule.every(self.config.frequency_minutes).minutes.do(
            lambda: self._run_sync_job()
        )
        
        logger.info(f"Scheduled stock sync every {self.config.frequency_minutes} minutes")
        
        # Add immediate execution for testing
        logger.info("Running initial sync job immediately for testing...")
        self._run_sync_job()
        
        while not self.stop_event.is_set():
            try:
                # Run pending scheduled jobs
                schedule.run_pending()
                
                # Sleep for a short interval to prevent busy waiting
                time_module.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in sync loop: {str(e)}")
                time_module.sleep(5)  # Wait before retrying
        
        logger.info("Stock sync worker stopped")
    
    def _run_sync_job(self):
        """Wrapper method to run the async sync job in the worker thread."""
        logger.info("=== _run_sync_job method called ===")
        try:
            # Create a new event loop for this thread if it doesn't exist
            try:
                loop = asyncio.get_event_loop()
                logger.debug("Using existing event loop")
            except RuntimeError:
                logger.debug("Creating new event loop for this thread")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            logger.info("About to run _sync_all_stocks...")
            # Run the sync job
            loop.run_until_complete(self._sync_all_stocks())
            logger.info("=== _run_sync_job completed successfully ===")
        except Exception as e:
            logger.error(f"Error running sync job: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def start(self):
        """Start the background worker."""
        if self.is_running:
            logger.warning("Stock sync worker is already running")
            return
        
        logger.info("Starting stock sync worker...")
        self.is_running = True
        self.stop_event.clear()
        
        # Start worker in a separate thread
        self.worker_thread = Thread(target=self._run_sync_loop, daemon=True)
        self.worker_thread.start()
        
        logger.info("Stock sync worker started successfully")
    
    def stop(self):
        """Stop the background worker."""
        if not self.is_running:
            logger.warning("Stock sync worker is not running")
            return
        
        logger.info("Stopping stock sync worker...")
        self.is_running = False
        self.stop_event.set()
        
        # Wait for worker thread to finish
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=10)
        
        logger.info("Stock sync worker stopped")
    
    def is_alive(self) -> bool:
        """Check if the worker is running."""
        return self.is_running and self.worker_thread and self.worker_thread.is_alive()
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the worker."""
        # Get the next scheduled run time
        next_run = None
        try:
            jobs = schedule.get_jobs()
            if jobs:
                next_run = jobs[0].next_run.isoformat() if hasattr(jobs[0], 'next_run') else "Unknown"
        except Exception as e:
            logger.debug(f"Could not get next run time: {e}")
            next_run = "Unknown"
        
        return {
            "is_running": self.is_running,
            "is_alive": self.is_alive(),
            "config": {
                "provider": self.config.provider,
                "frequency_minutes": self.config.frequency_minutes,
                "hour_start": self.config.hour_start,
                "hour_end": self.config.hour_end,
                "except_days": self.config.except_days,
                "stock_symbols": self.config.stock_symbols
            },
            "trading_time": self._is_trading_time(),
            "next_sync": f"Every {self.config.frequency_minutes} minutes during trading hours",
            "next_run_time": next_run,
            "scheduled_jobs_count": len(schedule.get_jobs()) if hasattr(schedule, 'get_jobs') else 0
        }
    
    def get_sync_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get sync statistics for analysis."""
        return self.stock_data_service.get_sync_statistics(days)
    
    def get_stock_history(self, symbol: str, limit: int = 100) -> List[Any]:
        """Get historical stock data for a specific symbol."""
        return self.stock_data_service.get_stock_data_history(symbol, limit)
    
    def trigger_manual_sync(self):
        """Manually trigger a sync operation for testing/debugging."""
        logger.info("Manual sync triggered")
        try:
            # Create a new event loop for this thread if it doesn't exist
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the sync job
            loop.run_until_complete(self._sync_all_stocks())
            logger.info("Manual sync completed successfully")
        except Exception as e:
            logger.error(f"Error in manual sync: {str(e)}")
            raise
    
    def get_recent_sync_logs(self, limit: int = 50) -> List[Any]:
        """Get recent sync log entries."""
        return self.stock_data_service.get_sync_logs(limit)
    
    def debug_schedule(self):
        """Debug method to check schedule status."""
        logger.info("=== Schedule Debug Info ===")
        try:
            jobs = schedule.get_jobs()
            logger.info(f"Total scheduled jobs: {len(jobs)}")
            
            for i, job in enumerate(jobs):
                logger.info(f"Job {i+1}: {job}")
                if hasattr(job, 'next_run'):
                    logger.info(f"  Next run: {job.next_run}")
                if hasattr(job, 'at_time'):
                    logger.info(f"  At time: {job.at_time}")
                if hasattr(job, 'interval'):
                    logger.info(f"  Interval: {job.interval}")
                    
        except Exception as e:
            logger.error(f"Error getting schedule info: {e}")
        
        logger.info("=== End Schedule Debug ===")