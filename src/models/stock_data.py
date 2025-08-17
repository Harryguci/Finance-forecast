"""
Stock Data Models

This module contains SQLAlchemy models for storing stock synchronized data.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Index
from sqlalchemy.sql import func
from src.database.connection import Base


class StockData(Base):
    """Model for storing stock synchronized data."""
    
    __tablename__ = "stock_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=True)
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    previous_close = Column(Float, nullable=True)
    change = Column(Float, nullable=True)
    change_percent = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    sync_timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    provider = Column(String(50), nullable=False, default="yahoo")
    status = Column(String(20), nullable=False, default="success")
    error_message = Column(Text, nullable=True)
    
    # Additional fields for analysis
    is_trading_hours = Column(Boolean, nullable=False, default=True)
    trading_day = Column(String(10), nullable=True)  # Mon, Tue, etc.
    
    # Create indexes for better query performance
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_timestamp', 'timestamp'),
        Index('idx_provider', 'provider'),
        Index('idx_status', 'status'),
    )
    
    def __repr__(self):
        return f"<StockData(symbol='{self.symbol}', price={self.price}, timestamp='{self.timestamp}')>"


class StockSyncLog(Base):
    """Model for logging stock sync operations."""
    
    __tablename__ = "stock_sync_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    sync_batch_id = Column(String(50), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False, default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    
    # Statistics
    total_symbols = Column(Integer, nullable=False, default=0)
    successful_syncs = Column(Integer, nullable=False, default=0)
    failed_syncs = Column(Integer, nullable=False, default=0)
    
    # Status and error info
    status = Column(String(20), nullable=False, default="running")
    error_message = Column(Text, nullable=True)
    
    # Trading time info
    is_trading_hours = Column(Boolean, nullable=False, default=True)
    
    def __repr__(self):
        return f"<StockSyncLog(batch_id='{self.sync_batch_id}', status='{self.status}', successful={self.successful_syncs}/{self.total_symbols}')>"
