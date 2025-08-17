#!/usr/bin/env python3
"""
Test script for Yahoo Stock API endpoints
Run this script to test the various endpoints of the Yahoo stock router
"""

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:5500/api/yahoo"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✅ Health check passed\n")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}\n")
        return False

def test_get_stock_data(symbol="FPT.VN"):
    """Test getting stock data for a symbol"""
    print(f"🔍 Testing Get Stock Data for {symbol}...")
    try:
        response = requests.get(f"{BASE_URL}/stock/{symbol}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print(f"✅ Stock data retrieval for {symbol} passed\n")
        return True
    except Exception as e:
        print(f"❌ Stock data retrieval for {symbol} failed: {e}\n")
        return False

def test_get_stock_info(symbol="FPT.VN"):
    """Test getting detailed stock info"""
    print(f"🔍 Testing Get Stock Info for {symbol}...")
    try:
        response = requests.get(f"{BASE_URL}/stock/{symbol}/info")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Symbol: {data.get('symbol')}")
        print(f"Info keys count: {len(data.get('info', {}))}")
        print(f"✅ Stock info retrieval for {symbol} passed\n")
        return True
    except Exception as e:
        print(f"❌ Stock info retrieval for {symbol} failed: {e}\n")
        return False

def test_get_stock_history(symbol="FPT.VN", period="1mo", interval="1d"):
    """Test getting stock history"""
    print(f"🔍 Testing Get Stock History for {symbol}...")
    try:
        response = requests.get(f"{BASE_URL}/stock/{symbol}/history", params={
            "period": period,
            "interval": interval
        })
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Symbol: {data.get('symbol')}")
        print(f"Period: {data.get('period')}")
        print(f"Interval: {data.get('interval')}")
        print(f"Data points: {data.get('count')}")
        print(f"✅ Stock history retrieval for {symbol} passed\n")
        return True
    except Exception as e:
        print(f"❌ Stock history retrieval for {symbol} failed: {e}\n")
        return False

def test_get_stock_dividends(symbol="KO"):
    """Test getting stock dividends"""
    print(f"🔍 Testing Get Stock Dividends for {symbol}...")
    try:
        response = requests.get(f"{BASE_URL}/stock/{symbol}/dividends")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Symbol: {data.get('symbol')}")
        print(f"Dividend count: {data.get('count')}")
        print(f"✅ Stock dividends retrieval for {symbol} passed\n")
        return True
    except Exception as e:
        print(f"❌ Stock dividends retrieval for {symbol} failed: {e}\n")
        return False

def test_get_stock_splits(symbol="AAPL"):
    """Test getting stock splits"""
    print(f"🔍 Testing Get Stock Splits for {symbol}...")
    try:
        response = requests.get(f"{BASE_URL}/stock/{symbol}/splits")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Symbol: {data.get('symbol')}")
        print(f"Split count: {data.get('count')}")
        print(f"✅ Stock splits retrieval for {symbol} passed\n")
        return True
    except Exception as e:
        print(f"❌ Stock splits retrieval for {symbol} failed: {e}\n")
        return False

def test_search_stocks(query="FPT.VN"):
    """Test stock search"""
    print(f"🔍 Testing Stock Search for '{query}'...")
    try:
        response = requests.get(f"{BASE_URL}/search", params={"query": query})
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Query: {data.get('query')}")
        print(f"Results: {data.get('results')}")
        print(f"✅ Stock search for '{query}' passed\n")
        return True
    except Exception as e:
        print(f"❌ Stock search for '{query}' failed: {e}\n")
        return False

def test_batch_stock_data(symbols="AAPL,MSFT,GOOGL"):
    """Test batch stock data retrieval"""
    print(f"🔍 Testing Batch Stock Data for {symbols}...")
    try:
        response = requests.get(f"{BASE_URL}/batch/{symbols}")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Symbols: {data.get('symbols')}")
        print(f"Success count: {data.get('success_count')}")
        print(f"Error count: {data.get('error_count')}")
        print(f"✅ Batch stock data retrieval passed\n")
        return True
    except Exception as e:
        print(f"❌ Batch stock data retrieval failed: {e}\n")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Yahoo Stock API Tests")
    print("=" * 50)
    
    tests = [
        # test_health_check,
        test_get_stock_data,
        # test_get_stock_info,
        # test_get_stock_history,
        # test_get_stock_dividends,
        # test_get_stock_splits,
        # test_search_stocks,
        # test_batch_stock_data
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Yahoo Stock API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the API server and network connection.")

if __name__ == "__main__":
    print("Make sure the FastAPI server is running on http://localhost:5500")
    print("You can start it with: python -m src.main")
    print()
    
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("Make sure the server is running and accessible")
