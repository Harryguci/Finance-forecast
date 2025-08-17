"""
Stock Data Service

This module provides database operations for stock data including saving synchronized data
and logging sync operations for analysis purposes.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import uuid

from src.models import StockData, StockSyncLog
from src.database.connection import get_db_session

logger = logging.getLogger(__name__)


class StockDataService:
    """Service for managing stock data in the database."""
    
    def __init__(self):
        self.logger = logger
    
    def save_stock_data(self, stock_data: Dict[str, Any], provider: str = "yahoo") -> Optional[StockData]:
        """
        Save stock data to the database.
        
        Args:
            stock_data: Dictionary containing stock information
            provider: Data provider name (e.g., 'yahoo')
            
        Returns:
            StockData object if successful, None otherwise
        """
        try:
            # Get database session
            session = next(get_db_session())
            
            # Create StockData object
            stock_record = StockData(
                symbol=stock_data.get("symbol"),
                price=stock_data.get("price"),
                volume=stock_data.get("volume"),
                open_price=stock_data.get("open_price"),
                high_price=stock_data.get("high_price"),
                low_price=stock_data.get("low_price"),
                previous_close=stock_data.get("previous_close"),
                change=stock_data.get("change"),
                change_percent=stock_data.get("change_percent"),
                market_cap=stock_data.get("market_cap"),
                pe_ratio=stock_data.get("pe_ratio"),
                dividend_yield=stock_data.get("dividend_yield"),
                timestamp=stock_data.get("timestamp", datetime.now()),
                provider=provider,
                status=stock_data.get("status", "success"),
                error_message=stock_data.get("error_message"),
                is_trading_hours=stock_data.get("is_trading_hours", True),
                trading_day=stock_data.get("trading_day")
            )
            
            # Add and commit
            session.add(stock_record)
            session.commit()
            session.refresh(stock_record)
            
            self.logger.info(f"Successfully saved stock data for {stock_data.get('symbol')}")
            return stock_record
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error saving stock data: {str(e)}")
            if session:
                session.rollback()
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error saving stock data: {str(e)}")
            if session:
                session.rollback()
            return None
        finally:
            if session:
                session.close()
    
    def create_sync_log(self, provider: str, total_symbols: int) -> Optional[StockSyncLog]:
        """
        Create a new sync log entry.
        
        Args:
            provider: Data provider name
            total_symbols: Total number of symbols to sync
            
        Returns:
            StockSyncLog object if successful, None otherwise
        """
        try:
            session = next(get_db_session())
            
            sync_log = StockSyncLog(
                sync_batch_id=str(uuid.uuid4()),
                provider=provider,
                total_symbols=total_symbols,
                status="running"
            )
            
            session.add(sync_log)
            session.commit()
            session.refresh(sync_log)
            
            self.logger.info(f"Created sync log with batch ID: {sync_log.sync_batch_id}")
            return sync_log
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error creating sync log: {str(e)}")
            if session:
                session.rollback()
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error creating sync log: {str(e)}")
            if session:
                session.rollback()
            return None
        finally:
            if session:
                session.close()
    
    def update_sync_log(self, batch_id: str, **kwargs) -> bool:
        """
        Update an existing sync log entry.
        
        Args:
            batch_id: Sync batch ID to update
            **kwargs: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = next(get_db_session())
            
            sync_log = session.query(StockSyncLog).filter(
                StockSyncLog.sync_batch_id == batch_id
            ).first()
            
            if not sync_log:
                self.logger.warning(f"Sync log with batch ID {batch_id} not found")
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(sync_log, key):
                    setattr(sync_log, key, value)
            
            session.commit()
            self.logger.info(f"Updated sync log {batch_id}")
            return True
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error updating sync log: {str(e)}")
            if session:
                session.rollback()
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error updating sync log: {str(e)}")
            if session:
                session.rollback()
            return False
        finally:
            if session:
                session.close()
    
    def get_stock_data_history(self, symbol: str, limit: int = 100) -> List[StockData]:
        """
        Get historical stock data for a specific symbol.
        
        Args:
            symbol: Stock symbol
            limit: Maximum number of records to return
            
        Returns:
            List of StockData objects
        """
        try:
            session = next(get_db_session())
            
            stock_data = session.query(StockData).filter(
                StockData.symbol == symbol
            ).order_by(
                StockData.timestamp.desc()
            ).limit(limit).all()
            
            return stock_data
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error retrieving stock data: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving stock data: {str(e)}")
            return []
        finally:
            if session:
                session.close()
    
    def get_sync_logs(self, limit: int = 50) -> List[StockSyncLog]:
        """
        Get recent sync log entries.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of StockSyncLog objects
        """
        try:
            session = next(get_db_session())
            
            sync_logs = session.query(StockSyncLog).order_by(
                StockSyncLog.start_time.desc()
            ).limit(limit).all()
            
            return sync_logs
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error retrieving sync logs: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving sync logs: {str(e)}")
            return []
        finally:
            if session:
                session.close()
    
    def get_sync_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get sync statistics for the specified number of days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary containing sync statistics
        """
        try:
            session = next(get_db_session())
            
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get sync logs for the period
            sync_logs = session.query(StockSyncLog).filter(
                StockSyncLog.start_time >= cutoff_date
            ).all()
            
            # Calculate statistics
            total_syncs = len(sync_logs)
            successful_syncs = sum(log.successful_syncs for log in sync_logs)
            failed_syncs = sum(log.failed_syncs for log in sync_logs)
            total_symbols = sum(log.total_symbols for log in sync_logs)
            
            # Get stock data count for the period
            stock_data_count = session.query(StockData).filter(
                StockData.sync_timestamp >= cutoff_date
            ).count()
            
            return {
                "period_days": days,
                "total_sync_operations": total_syncs,
                "total_symbols_synced": total_symbols,
                "successful_syncs": successful_syncs,
                "failed_syncs": failed_syncs,
                "success_rate": (successful_syncs / total_symbols * 100) if total_symbols > 0 else 0,
                "total_stock_records": stock_data_count,
                "average_records_per_sync": stock_data_count / total_syncs if total_syncs > 0 else 0
            }
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error calculating sync statistics: {str(e)}")
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error calculating sync statistics: {str(e)}")
            return {}
        finally:
            if session:
                session.close()
