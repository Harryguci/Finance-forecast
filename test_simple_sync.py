#!/usr/bin/env python3
"""
Simple test script to verify that _run_sync_job and _sync_all_stocks are being called
"""

import time
import logging
from src.background_workers.stock_sync_worker import StockSyncWorker, StockSyncWorkerConfig

# Configure logging to see all messages
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_simple_sync():
    """Simple test to verify sync methods are called."""
    
    # Create a test configuration
    config = StockSyncWorkerConfig(
        provider="yahoo",
        frequency_minutes=1,  # Every minute for testing
        hour_start=0,         # Allow all hours for testing
        hour_end=23,
        except_days="",       # Allow all days for testing
        stock_symbols=["FPT.VN"]
    )
    
    logger.info("=== Starting Simple Sync Test ===")
    logger.info(f"Config: {config}")
    
    # Create the worker
    worker = StockSyncWorker(config)
    
    try:
        # Start the worker
        logger.info("Starting worker...")
        worker.start()
        
        # Wait a bit for the worker to start and run initial sync
        logger.info("Waiting for initial sync to complete...")
        time.sleep(5)
        
        # Check status
        status = worker.get_status()
        logger.info(f"Worker status: {status}")
        
        # Debug schedule
        logger.info("Checking schedule status...")
        worker.debug_schedule()
        
        # Wait for scheduled sync to run
        logger.info("Waiting for scheduled sync to run...")
        time.sleep(70)  # Wait a bit more than 1 minute
        
        # Check status again
        status = worker.get_status()
        logger.info(f"Worker status after waiting: {status}")
        
        # Debug schedule again
        logger.info("Checking schedule status after waiting...")
        worker.debug_schedule()
        
        logger.info("=== Test completed successfully ===")
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("Stopping worker...")
        worker.stop()
        logger.info("Test completed")

if __name__ == "__main__":
    test_simple_sync()
