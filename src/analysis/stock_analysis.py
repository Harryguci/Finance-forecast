"""
Stock Data Analysis

This module provides analysis functions for the stored stock data, including
trends, statistics, and performance metrics.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
from sqlalchemy import func, desc

from src.database.connection import get_db_session
from src.models import StockData, StockSyncLog

logger = logging.getLogger(__name__)


class StockAnalyzer:
    """Analyzer for stock data stored in the database."""
    
    def __init__(self):
        self.logger = logger
    
    def get_price_trends(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """
        Analyze price trends for a specific symbol over a period.
        
        Args:
            symbol: Stock symbol to analyze
            days: Number of days to analyze
            
        Returns:
            Dictionary containing trend analysis
        """
        try:
            session = next(get_db_session())
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get stock data for the period
            stock_records = session.query(StockData).filter(
                StockData.symbol == symbol,
                StockData.timestamp >= cutoff_date,
                StockData.status == "success"
            ).order_by(StockData.timestamp.asc()).all()
            
            if not stock_records:
                return {"error": f"No data found for {symbol} in the last {days} days"}
            
            # Convert to pandas DataFrame for analysis
            df = pd.DataFrame([
                {
                    'timestamp': record.timestamp,
                    'price': record.price,
                    'volume': record.volume,
                    'change': record.change,
                    'change_percent': record.change_percent
                }
                for record in stock_records
            ])
            
            # Calculate trends
            price_change = df['price'].iloc[-1] - df['price'].iloc[0]
            price_change_percent = (price_change / df['price'].iloc[0]) * 100
            
            # Calculate moving averages
            df['price_ma_5'] = df['price'].rolling(window=5).mean()
            df['price_ma_10'] = df['price'].rolling(window=10).mean()
            
            # Volume analysis
            avg_volume = df['volume'].mean() if 'volume' in df.columns else 0
            max_volume = df['volume'].max() if 'volume' in df.columns else 0
            
            # Price volatility
            price_volatility = df['price'].std()
            
            return {
                "symbol": symbol,
                "period_days": days,
                "data_points": len(stock_records),
                "start_price": df['price'].iloc[0],
                "end_price": df['price'].iloc[-1],
                "price_change": round(price_change, 4),
                "price_change_percent": round(price_change_percent, 2),
                "highest_price": df['price'].max(),
                "lowest_price": df['price'].min(),
                "average_price": round(df['price'].mean(), 4),
                "price_volatility": round(price_volatility, 4),
                "average_volume": int(avg_volume),
                "max_volume": int(max_volume),
                "trend": "upward" if price_change > 0 else "downward" if price_change < 0 else "stable",
                "last_updated": stock_records[-1].timestamp.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing price trends for {symbol}: {str(e)}")
            return {"error": str(e)}
        finally:
            if session:
                session.close()
    
    def get_sync_performance_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get performance metrics for stock sync operations.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary containing performance metrics
        """
        try:
            session = next(get_db_session())
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get sync logs for the period
            sync_logs = session.query(StockSyncLog).filter(
                StockSyncLog.start_time >= cutoff_date
            ).all()
            
            if not sync_logs:
                return {"error": f"No sync logs found in the last {days} days"}
            
            # Calculate metrics
            total_syncs = len(sync_logs)
            completed_syncs = sum(1 for log in sync_logs if log.status == "completed")
            failed_syncs = sum(1 for log in sync_logs if log.status == "failed")
            running_syncs = sum(1 for log in sync_logs if log.status == "running")
            
            total_symbols = sum(log.total_symbols for log in sync_logs)
            successful_syncs = sum(log.successful_syncs for log in sync_logs)
            failed_symbol_syncs = sum(log.failed_syncs for log in sync_logs)
            
            # Calculate success rates
            sync_success_rate = (completed_syncs / total_syncs * 100) if total_syncs > 0 else 0
            symbol_success_rate = (successful_syncs / total_symbols * 100) if total_symbols > 0 else 0
            
            # Get average sync duration
            completed_logs = [log for log in sync_logs if log.end_time and log.start_time]
            if completed_logs:
                avg_duration = sum(
                    (log.end_time - log.start_time).total_seconds() 
                    for log in completed_logs
                ) / len(completed_logs)
            else:
                avg_duration = 0
            
            return {
                "period_days": days,
                "total_sync_operations": total_syncs,
                "completed_syncs": completed_syncs,
                "failed_syncs": failed_syncs,
                "running_syncs": running_syncs,
                "sync_success_rate": round(sync_success_rate, 2),
                "total_symbols_synced": total_symbols,
                "successful_symbol_syncs": successful_syncs,
                "failed_symbol_syncs": failed_symbol_syncs,
                "symbol_success_rate": round(symbol_success_rate, 2),
                "average_sync_duration_seconds": round(avg_duration, 2),
                "last_sync": max(log.start_time for log in sync_logs).isoformat() if sync_logs else None
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating sync performance metrics: {str(e)}")
            return {"error": str(e)}
        finally:
            if session:
                session.close()
    
    def get_trading_hours_analysis(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """
        Analyze stock data during trading hours vs non-trading hours.
        
        Args:
            symbol: Stock symbol to analyze
            days: Number of days to analyze
            
        Returns:
            Dictionary containing trading hours analysis
        """
        try:
            session = next(get_db_session())
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get stock data for the period
            trading_hours_data = session.query(StockData).filter(
                StockData.symbol == symbol,
                StockData.timestamp >= cutoff_date,
                StockData.status == "success",
                StockData.is_trading_hours == True
            ).all()
            
            non_trading_hours_data = session.query(StockData).filter(
                StockData.symbol == symbol,
                StockData.timestamp >= cutoff_date,
                StockData.status == "success",
                StockData.is_trading_hours == False
            ).all()
            
            def analyze_data(data_list):
                if not data_list:
                    return {"count": 0, "avg_price": 0, "price_volatility": 0}
                
                prices = [record.price for record in data_list]
                return {
                    "count": len(data_list),
                    "avg_price": round(sum(prices) / len(prices), 4),
                    "price_volatility": round(pd.Series(prices).std(), 4)
                }
            
            trading_analysis = analyze_data(trading_hours_data)
            non_trading_analysis = analyze_data(non_trading_hours_data)
            
            return {
                "symbol": symbol,
                "period_days": days,
                "trading_hours": trading_analysis,
                "non_trading_hours": non_trading_analysis,
                "total_records": trading_analysis["count"] + non_trading_analysis["count"]
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing trading hours for {symbol}: {str(e)}")
            return {"error": str(e)}
        finally:
            if session:
                session.close()
    
    def get_daily_summary(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get a summary of stock data for a specific date.
        
        Args:
            date: Date to analyze (defaults to today)
            
        Returns:
            Dictionary containing daily summary
        """
        try:
            session = next(get_db_session())
            
            if date is None:
                date = datetime.now().date()
            
            # Get stock data for the date
            start_datetime = datetime.combine(date, datetime.min.time())
            end_datetime = datetime.combine(date, datetime.max.time())
            
            stock_records = session.query(StockData).filter(
                StockData.timestamp >= start_datetime,
                StockData.timestamp <= end_datetime,
                StockData.status == "success"
            ).all()
            
            if not stock_records:
                return {"error": f"No data found for {date.strftime('%Y-%m-%d')}"}
            
            # Group by symbol
            symbols_data = {}
            for record in stock_records:
                if record.symbol not in symbols_data:
                    symbols_data[record.symbol] = []
                symbols_data[record.symbol].append(record)
            
            # Calculate summary for each symbol
            summary = {}
            for symbol, records in symbols_data.items():
                prices = [r.price for r in records]
                volumes = [r.volume for r in records if r.volume]
                
                summary[symbol] = {
                    "records_count": len(records),
                    "first_price": prices[0],
                    "last_price": prices[-1],
                    "highest_price": max(prices),
                    "lowest_price": min(prices),
                    "average_price": round(sum(prices) / len(prices), 4),
                    "price_change": round(prices[-1] - prices[0], 4),
                    "price_change_percent": round(((prices[-1] - prices[0]) / prices[0]) * 100, 2) if prices[0] != 0 else 0,
                    "total_volume": sum(volumes) if volumes else 0,
                    "average_volume": round(sum(volumes) / len(volumes), 0) if volumes else 0
                }
            
            return {
                "date": date.strftime('%Y-%m-%d'),
                "total_records": len(stock_records),
                "symbols_count": len(symbols_data),
                "symbols_summary": summary
            }
            
        except Exception as e:
            self.logger.error(f"Error generating daily summary: {str(e)}")
            return {"error": str(e)}
        finally:
            if session:
                session.close()


def main():
    """Example usage of the StockAnalyzer."""
    analyzer = StockAnalyzer()
    
    # Example analyses
    print("=== Stock Data Analysis Examples ===\n")
    
    # Get sync performance metrics
    print("1. Sync Performance Metrics (Last 30 days):")
    metrics = analyzer.get_sync_performance_metrics(30)
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*50 + "\n")
    
    # Get price trends for a symbol (if data exists)
    print("2. Price Trends Analysis:")
    trends = analyzer.get_price_trends("FPT.VN", 7)  # Last 7 days
    for key, value in trends.items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*50 + "\n")
    
    # Get daily summary
    print("3. Today's Summary:")
    summary = analyzer.get_daily_summary()
    for key, value in summary.items():
        if key == "symbols_summary":
            print(f"   {key}:")
            for symbol, symbol_data in value.items():
                print(f"     {symbol}: {symbol_data}")
        else:
            print(f"   {key}: {value}")


if __name__ == "__main__":
    main()
