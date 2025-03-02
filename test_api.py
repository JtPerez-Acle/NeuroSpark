#!/usr/bin/env python3
"""
Simple test script for API endpoints
"""
import requests
import json
import sys

def test_wallet_endpoint(address):
    """Test the wallet endpoint with given address"""
    url = f"http://localhost:8000/blockchain/wallets/{address}"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Success! Wallet data:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error making request: {str(e)}")

def generate_transaction():
    """Generate a new transaction and return sender address"""
    url = "http://localhost:8000/generate/transaction"
    
    try:
        response = requests.post(url, json={}, timeout=5)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            sender = data["sender"]["address"]
            print(f"Generated transaction with sender: {sender}")
            return sender
        else:
            print(f"Error response: {response.text}")
            return None
    except Exception as e:
        print(f"Error making request: {str(e)}")
        return None

def main():
    """Main function"""
    print("Testing API endpoints...")
    
    # Test root endpoint first to verify server is up
    response = requests.get("http://localhost:8000/")
    print(f"Root endpoint status: {response.status_code}")
    
    # Generate a transaction first
    sender_address = generate_transaction()
    
    if sender_address:
        print("\nTesting wallet endpoint with generated address...")
        test_wallet_endpoint(sender_address)
    else:
        print("No sender address available to test wallet endpoint")

if __name__ == "__main__":
    main()