"""
Test Script for Sync Stock API Endpoints

This script demonstrates how to use the sync stock API endpoints to control
the stock sync worker and retrieve data.
"""

import requests
import json
import time
from datetime import datetime

# API base URL
BASE_URL = "http://127.0.0.1:5500/api/sync-stock"

def print_response(response, title):
    """Print API response in a formatted way."""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, default=str))

def test_sync_endpoints():
    """Test all sync stock API endpoints."""
    
    print("Testing Stock Sync API Endpoints")
    print("Make sure the FastAPI server is running on http://127.0.0.1:5500")
    
    try:
        # 1. Check health status
        print("\n1. Checking worker health...")
        response = requests.get(f"{BASE_URL}/health")
        print_response(response, "Worker Health Status")
        
        # 2. Get current status
        print("\n2. Getting current worker status...")
        response = requests.get(f"{BASE_URL}/status")
        print_response(response, "Current Worker Status")
        
        # 3. Get worker configuration
        print("\n3. Getting worker configuration...")
        response = requests.get(f"{BASE_URL}/config")
        print_response(response, "Worker Configuration")
        
        # 4. Start the worker
        print("\n4. Starting the stock sync worker...")
        response = requests.post(f"{BASE_URL}/start")
        print_response(response, "Start Worker Response")
        
        # Wait a moment for worker to start
        time.sleep(2)
        
        # 5. Check status again
        print("\n5. Checking status after start...")
        response = requests.get(f"{BASE_URL}/status")
        print_response(response, "Status After Start")
        
        # 6. Get sync statistics (if any data exists)
        print("\n6. Getting sync statistics...")
        response = requests.get(f"{BASE_URL}/statistics?days=7")
        print_response(response, "Sync Statistics (Last 7 days)")
        
        # 7. Get recent sync logs
        print("\n7. Getting recent sync logs...")
        response = requests.get(f"{BASE_URL}/logs?limit=5")
        print_response(response, "Recent Sync Logs")
        
        # 8. Get stock history for a symbol
        print("\n8. Getting stock history...")
        response = requests.get(f"{BASE_URL}/history/FPT.VN?limit=10")
        print_response(response, "Stock History for FPT.VN")
        
        # 9. Update worker configuration
        print("\n9. Updating worker configuration...")
        new_config = {
            "provider": "yahoo",
            "frequency_minutes": 3,
            "hour_start": 9,
            "hour_end": 16,
            "except_days": "sat,sun",
            "stock_symbols": ["FPT.VN", "VNM.VN", "TCB.VN"]
        }
        response = requests.post(f"{BASE_URL}/config", json=new_config)
        print_response(response, "Configuration Update Response")
        
        # Wait a moment
        time.sleep(2)
        
        # 10. Check final status
        print("\n10. Final status check...")
        response = requests.get(f"{BASE_URL}/status")
        print_response(response, "Final Worker Status")
        
        # 11. Stop the worker
        print("\n11. Stopping the worker...")
        response = requests.post(f"{BASE_URL}/stop")
        print_response(response, "Stop Worker Response")
        
        print("\n" + "="*50)
        print("All tests completed!")
        print("="*50)
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the FastAPI server is running on http://127.0.0.1:5500")
    except Exception as e:
        print(f"Error during testing: {str(e)}")

def test_individual_endpoints():
    """Test individual endpoints with more detailed output."""
    
    print("\n" + "="*60)
    print("Testing Individual Endpoints")
    print("="*60)
    
    endpoints = [
        ("GET", "/health", "Worker Health Check"),
        ("GET", "/status", "Worker Status"),
        ("GET", "/config", "Worker Configuration"),
        ("GET", "/statistics?days=30", "Sync Statistics"),
        ("GET", "/logs?limit=10", "Sync Logs"),
        ("GET", "/history/FPT.VN?limit=5", "Stock History"),
    ]
    
    for method, endpoint, description in endpoints:
        try:
            print(f"\nTesting: {description}")
            print(f"Endpoint: {method} {endpoint}")
            
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            else:
                response = requests.post(f"{BASE_URL}{endpoint}")
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2, default=str)}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("-" * 40)

if __name__ == "__main__":
    print("Stock Sync API Test Script")
    print("=" * 60)
    
    # Test all endpoints
    test_sync_endpoints()
    
    # Test individual endpoints
    test_individual_endpoints()
    
    print("\nTest script completed!")
    print("\nTo use the API manually:")
    print(f"1. Health check: GET {BASE_URL}/health")
    print(f"2. Start worker: POST {BASE_URL}/start")
    print(f"3. Stop worker: POST {BASE_URL}/stop")
    print(f"4. Get status: GET {BASE_URL}/status")
    print(f"5. Get statistics: GET {BASE_URL}/statistics?days=7")
    print(f"6. Get logs: GET {BASE_URL}/logs?limit=10")
    print(f"7. Get history: GET {BASE_URL}/history/FPT.VN?limit=100")
