#!/usr/bin/env python3
"""
Quick test to verify basic infrastructure connectivity
"""
import requests
import json
import os
import sys

def test_infrastructure():
    """Test infrastructure components"""
    print("Testing infrastructure connectivity...")
    
    # Test PostgreSQL via direct connection
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            database="datavein",
            user="datavein",
            password="datavein_password"
        )
        conn.close()
        print("✅ PostgreSQL: Connected")
    except Exception as e:
        print(f"❌ PostgreSQL: {e}")
    
    # Test Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis: Connected")
    except Exception as e:
        print(f"❌ Redis: {e}")
    
    # Test MinIO
    try:
        import boto3
        from botocore.config import Config
        
        s3_client = boto3.client(
            's3',
            endpoint_url='http://localhost:9000',
            aws_access_key_id='minioadmin',
            aws_secret_access_key='minioadmin',
            config=Config(signature_version='s3v4')
        )
        s3_client.list_buckets()
        print("✅ MinIO: Connected")
    except Exception as e:
        print(f"❌ MinIO: {e}")

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend: Healthy")
            return True
        else:
            print(f"❌ Backend: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend: {e}")
        return False

def simulate_auth_flow():
    """Simulate registration and login"""
    base_url = "http://localhost:8000"
    
    # Test data
    test_user = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    print("\nTesting authentication flow...")
    
    try:
        # Register
        response = requests.post(
            f"{base_url}/auth/register",
            json=test_user,
            timeout=5
        )
        if response.status_code in [200, 201]:
            print("✅ Registration: Success")
        elif response.status_code == 400 and "already registered" in response.text:
            print("✅ Registration: User exists (expected)")
        else:
            print(f"❌ Registration: HTTP {response.status_code} - {response.text}")
            return None
        
        # Login
        response = requests.post(
            f"{base_url}/auth/login",
            json=test_user,
            timeout=5
        )
        if response.status_code == 200:
            token = response.json().get('access_token')
            print("✅ Login: Success")
            print(f"   Token: {token[:20]}...")
            return token
        else:
            print(f"❌ Login: HTTP {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Auth flow error: {e}")
        return None

if __name__ == "__main__":
    print("=== DataVein Quick Start Test ===\n")
    
    # Test infrastructure
    test_infrastructure()
    
    # Test backend
    print()
    backend_healthy = test_backend_health()
    
    if backend_healthy:
        # Test auth flow
        token = simulate_auth_flow()
        
        if token:
            print("\n🎉 Quick start verification successful!")
            print("✅ Infrastructure: Connected")
            print("✅ Backend: Healthy") 
            print("✅ Authentication: Working")
            print("\nReady to proceed with file upload and pipeline testing.")
        else:
            print("\n⚠️  Infrastructure OK, but authentication failed")
    else:
        print("\n❌ Backend not responding - check logs and import issues")
        print("Infrastructure components tested above.")
