#!/usr/bin/env python3
"""
Debug script to monitor the StockSyncWorker and identify issues
"""

import time
import logging
from src.background_workers.stock_sync_worker import StockSyncWorker, StockSyncWorkerConfig

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_worker():
    """Debug the sync worker by monitoring its behavior."""
    
    # Create a test configuration
    config = StockSyncWorkerConfig(
        provider="yahoo",
        frequency_minutes=2,  # Every 2 minutes for testing
        hour_start=0,         # Allow all hours for testing
        hour_end=23,
        except_days="",       # Allow all days for testing
        stock_symbols=["FPT.VN"]
    )
    
    # Create the worker
    worker = StockSyncWorker(config)
    
    try:
        logger.info("=== Starting Debug Session ===")
        logger.info(f"Configuration: {config}")
        
        # Start the worker
        logger.info("Starting worker...")
        worker.start()
        
        # Monitor the worker for several cycles
        for cycle in range(5):
            logger.info(f"\n=== Cycle {cycle + 1} ===")
            
            # Get current status
            status = worker.get_status()
            logger.info(f"Status: {status}")
            
            # Check if worker is alive
            is_alive = worker.is_alive()
            logger.info(f"Worker alive: {is_alive}")
            
            # Wait for next cycle
            logger.info("Waiting 2 minutes for next cycle...")
            time.sleep(120)
            
            # Check if any syncs happened
            try:
                logs = worker.get_recent_sync_logs(3)
                logger.info(f"Recent sync logs: {len(logs)} entries")
                for log in logs:
                    logger.info(f"Log entry: {log}")
            except Exception as e:
                logger.warning(f"Could not get sync logs: {e}")
        
        logger.info("=== Debug Session Completed ===")
        
    except Exception as e:
        logger.error(f"Error during debug: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("Stopping worker...")
        worker.stop()
        logger.info("Debug completed")

if __name__ == "__main__":
    debug_worker()
