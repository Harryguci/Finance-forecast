#!/usr/bin/env python3
"""
Example usage of StockSyncWorker

This script demonstrates how to use the StockSyncWorker class
to run a background worker that syncs stock data.
"""

import asyncio
import time
from stock_sync_worker import StockSyncWorker, StockSyncWorkerConfig

def main():
    """Main function to demonstrate StockSyncWorker usage."""
    
    # Create a custom configuration
    config = StockSyncWorkerConfig(
        provider="yahoo",
        frequency_minutes=2,  # Sync every 2 minutes for demo
        hour_start=9,
        hour_end=17,
        except_days="sat,sun",
        stock_symbols=["FPT.VN", "VNM.VN", "TCB.VN"]
    )
    
    # Create and start the worker
    worker = StockSyncWorker(config)
    
    print("Starting StockSyncWorker...")
    print(f"Configuration: {config}")
    print(f"Status: {worker.get_status()}")
    
    # Start the worker
    worker.start()
    
    try:
        # Let the worker run for a while
        print("\nWorker is running. Press Ctrl+C to stop...")
        
        # Monitor the worker status
        for i in range(10):  # Monitor for 10 iterations
            time.sleep(30)  # Wait 30 seconds between checks
            status = worker.get_status()
            print(f"\nStatus check {i+1}:")
            print(f"  Running: {status['is_running']}")
            print(f"  Alive: {status['is_alive']}")
            print(f"  Trading time: {status['trading_time']}")
            print(f"  Next sync: {status['next_sync']}")
            
    except KeyboardInterrupt:
        print("\nStopping worker...")
    
    finally:
        # Stop the worker
        worker.stop()
        print("Worker stopped.")

if __name__ == "__main__":
    main()
