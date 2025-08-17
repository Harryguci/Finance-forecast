#!/usr/bin/env python3
"""
Test script to verify the fixed StockSyncWorker properly executes _sync_all_stocks
"""

import asyncio
import time
import logging
from src.background_workers.stock_sync_worker import StockSyncWorker, StockSyncWorkerConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sync_worker():
    """Test the fixed sync worker."""
    
    # Create a test configuration with very frequent syncs for testing
    config = StockSyncWorkerConfig(
        provider="yahoo",
        frequency_minutes=1,  # Every minute for testing
        hour_start=0,         # Allow all hours for testing
        hour_end=23,
        except_days="",       # Allow all days for testing
        stock_symbols=["FPT.VN", "VNM.VN"]  # Test with multiple symbols
    )
    
    # Create the worker
    worker = StockSyncWorker(config)
    
    try:
        logger.info("Starting worker...")
        worker.start()
        
        # Wait a bit for the worker to start
        time.sleep(2)
        
        # Check status
        status = worker.get_status()
        logger.info(f"Worker status: {status}")
        
        # Test manual sync
        logger.info("Testing manual sync...")
        worker.trigger_manual_sync()
        
        # Wait for scheduled sync to run
        logger.info("Waiting for scheduled sync to run...")
        time.sleep(70)  # Wait a bit more than 1 minute
        
        # Check status again
        status = worker.get_status()
        logger.info(f"Worker status after waiting: {status}")
        
        # Get recent sync logs
        try:
            logs = worker.get_recent_sync_logs(5)
            logger.info(f"Recent sync logs: {len(logs)} entries")
            for log in logs:
                logger.info(f"Log: {log}")
        except Exception as e:
            logger.warning(f"Could not get sync logs: {e}")
        
        # Keep running for a bit more to see scheduled syncs
        logger.info("Keeping worker running for a few more minutes to observe scheduled syncs...")
        time.sleep(180)  # 3 more minutes
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error during test: {e}")
    finally:
        logger.info("Stopping worker...")
        worker.stop()
        logger.info("Test completed")

if __name__ == "__main__":
    test_sync_worker()
