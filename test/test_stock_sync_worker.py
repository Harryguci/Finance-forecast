#!/usr/bin/env python3
"""
Tests for StockSyncWorker

This module contains tests for the StockSyncWorker class.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio
from datetime import datetime, time
from src.background_workers.stock_sync_worker import StockSyncWorker, StockSyncWorkerConfig
from src.services.stock_api_service import StockData

class TestStockSyncWorker(unittest.TestCase):
    """Test cases for StockSyncWorker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = StockSyncWorkerConfig(
            provider="yahoo",
            frequency_minutes=5,
            hour_start=9,
            hour_end=16,
            except_days="sat,sun",
            stock_symbols=["FPT.VN", "VNM.VN"]
        )
        
        # Mock the service
        self.mock_service = Mock()
        self.worker = StockSyncWorker(self.config)
        self.worker.service = self.mock_service
    
    def test_initialization(self):
        """Test worker initialization."""
        self.assertEqual(self.worker.config, self.config)
        self.assertFalse(self.worker.is_running)
        self.assertEqual(self.worker.except_days, ["sat", "sun"])
        self.assertEqual(self.worker.trading_start, time(9))
        self.assertEqual(self.worker.trading_end, time(16))
    
    def test_get_service_yahoo(self):
        """Test getting Yahoo service."""
        with patch('src.background_workers.stock_sync_worker.YahooStockApiService') as mock_yahoo:
            mock_instance = Mock()
            mock_yahoo.return_value = mock_instance
            
            worker = StockSyncWorker(StockSyncWorkerConfig(provider="yahoo"))
            self.assertEqual(worker.service, mock_instance)
    
    def test_get_service_unknown(self):
        """Test getting unknown service falls back to Yahoo."""
        with patch('src.background_workers.stock_sync_worker.YahooStockApiService') as mock_yahoo:
            mock_instance = Mock()
            mock_yahoo.return_value = mock_instance
            
            worker = StockSyncWorker(StockSyncWorkerConfig(provider="unknown"))
            self.assertEqual(worker.service, mock_instance)
    
    def test_is_trading_time_weekday_trading_hours(self):
        """Test trading time check during weekday trading hours."""
        with patch('src.background_workers.stock_sync_worker.datetime') as mock_datetime:
            # Mock Monday 10:00 AM
            mock_now = Mock()
            mock_now.time.return_value = time(10, 0)
            mock_now.strftime.return_value = "Mon"
            mock_datetime.now.return_value = mock_now
            
            self.assertTrue(self.worker._is_trading_time())
    
    def test_is_trading_time_weekday_before_trading(self):
        """Test trading time check before trading hours."""
        with patch('src.background_workers.stock_sync_worker.datetime') as mock_datetime:
            # Mock Monday 8:00 AM
            mock_now = Mock()
            mock_now.time.return_value = time(8, 0)
            mock_now.strftime.return_value = "Mon"
            mock_datetime.now.return_value = mock_now
            
            self.assertFalse(self.worker._is_trading_time())
    
    def test_is_trading_time_weekday_after_trading(self):
        """Test trading time check after trading hours."""
        with patch('src.background_workers.stock_sync_worker.datetime') as mock_datetime:
            # Mock Monday 6:00 PM
            mock_now = Mock()
            mock_now.time.return_value = time(18, 0)
            mock_now.strftime.return_value = "Mon"
            mock_datetime.now.return_value = mock_now
            
            self.assertFalse(self.worker._is_trading_time())
    
    def test_is_trading_time_weekend(self):
        """Test trading time check on weekend."""
        with patch('src.background_workers.stock_sync_worker.datetime') as mock_datetime:
            # Mock Saturday 10:00 AM
            mock_now = Mock()
            mock_now.time.return_value = time(10, 0)
            mock_now.strftime.return_value = "Sat"
            mock_datetime.now.return_value = mock_now
            
            self.assertFalse(self.worker._is_trading_time())
    
    @patch('asyncio.gather')
    async def test_sync_stock_data_success(self, mock_gather):
        """Test successful stock data sync."""
        # Mock successful stock data
        mock_stock_data = StockData(
            symbol="FPT.VN",
            price=100.0,
            volume=1000000,
            timestamp=datetime.now()
        )
        
        self.mock_service.get.return_value = mock_stock_data
        
        result = await self.worker._sync_stock_data("FPT.VN")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["symbol"], "FPT.VN")
        self.assertEqual(result["price"], 100.0)
        self.assertEqual(result["volume"], 1000000)
    
    @patch('asyncio.gather')
    async def test_sync_stock_data_error(self, mock_gather):
        """Test stock data sync with error."""
        # Mock service error
        self.mock_service.get.side_effect = Exception("API Error")
        
        result = await self.worker._sync_stock_data("FPT.VN")
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["symbol"], "FPT.VN")
        self.assertIn("API Error", result["error"])
    
    @patch('asyncio.gather')
    async def test_sync_all_stocks_trading_time(self, mock_gather):
        """Test syncing all stocks during trading time."""
        # Mock trading time
        with patch.object(self.worker, '_is_trading_time', return_value=True):
            # Mock successful sync results
            mock_gather.return_value = [
                {"status": "success", "symbol": "FPT.VN"},
                {"status": "success", "symbol": "VNM.VN"}
            ]
            
            await self.worker._sync_all_stocks()
            
            # Verify gather was called with correct tasks
            mock_gather.assert_called_once()
            tasks = mock_gather.call_args[0][0]
            self.assertEqual(len(tasks), 2)
    
    @patch('asyncio.gather')
    async def test_sync_all_stocks_non_trading_time(self, mock_gather):
        """Test syncing all stocks outside trading time."""
        # Mock non-trading time
        with patch.object(self.worker, '_is_trading_time', return_value=False):
            await self.worker._sync_all_stocks()
            
            # Verify gather was not called
            mock_gather.assert_not_called()
    
    def test_worker_lifecycle(self):
        """Test worker start/stop lifecycle."""
        # Test start
        self.worker.start()
        self.assertTrue(self.worker.is_running)
        self.assertIsNotNone(self.worker.worker_thread)
        
        # Test stop
        self.worker.stop()
        self.assertFalse(self.worker.is_running)
    
    def test_get_status(self):
        """Test getting worker status."""
        status = self.worker.get_status()
        
        self.assertIn("is_running", status)
        self.assertIn("is_alive", status)
        self.assertIn("config", status)
        self.assertIn("trading_time", status)
        self.assertIn("next_sync", status)
        
        self.assertEqual(status["config"]["provider"], "yahoo")
        self.assertEqual(status["config"]["frequency_minutes"], 5)

if __name__ == "__main__":
    unittest.main()
