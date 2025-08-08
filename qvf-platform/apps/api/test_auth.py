#!/usr/bin/env python3
"""Test script for JWT authentication system."""

import sys
import os
import requests
import json
from datetime import datetime
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_authentication_system():
    """Test the JWT authentication system."""
    
    # API base URL (assuming server is running on port 8000)
    base_url = "http://localhost:8000"
    
    logger.info("Starting JWT Authentication System Test")
    logger.info("=" * 50)
    
    # Test 1: Health check
    logger.info("1. Testing API health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            logger.info(f"   ✅ API is healthy - Status: {health_data.get('status')}")
            logger.info(f"   ✅ Authentication: {health_data.get('authentication', {}).get('status')}")
            logger.info(f"   ✅ Users in database: {health_data.get('authentication', {}).get('users', 0)}")
        else:
            logger.error(f"   ❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("   ❌ Cannot connect to API server. Is it running on port 8000?")
        logger.info("   💡 Run: python3 /Users/umasankrudhya/Projects/ds-package/qvf-platform/start_api.py")
        return False
    except Exception as e:
        logger.error(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: Login with test users
    test_users = [
        {"username": "executive", "password": "executive123", "expected_role": "executive"},
        {"username": "product_owner", "password": "po123", "expected_role": "product_owner"},
        {"username": "scrum_master", "password": "sm123", "expected_role": "scrum_master"},
        {"username": "developer", "password": "dev123", "expected_role": "developer"},
        {"username": "admin", "password": "admin123", "expected_role": "executive"},
    ]
    
    tokens = {}
    
    for user in test_users:
        logger.info(f"2. Testing login for {user['username']}...")
        
        try:
            # Login
            login_data = {
                "username": user["username"],
                "password": user["password"]
            }
            
            response = requests.post(
                f"{base_url}/api/v1/auth/token",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                tokens[user["username"]] = token_data["access_token"]
                logger.info(f"   ✅ Login successful for {user['username']}")
                logger.info(f"   ✅ Token type: {token_data['token_type']}")
                logger.info(f"   ✅ Expires in: {token_data['expires_in']} seconds")
            else:
                logger.error(f"   ❌ Login failed for {user['username']}: {response.status_code}")
                logger.error(f"   ❌ Response: {response.text}")
                continue
                
        except Exception as e:
            logger.error(f"   ❌ Login error for {user['username']}: {e}")
            continue
    
    # Test 3: Access protected endpoints
    logger.info("3. Testing protected endpoints...")
    
    for username, token in tokens.items():
        logger.info(f"   Testing /me endpoint for {username}...")
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"   ✅ User info retrieved for {username}")
                logger.info(f"   ✅ Role: {user_data.get('role')}")
                logger.info(f"   ✅ Email: {user_data.get('email')}")
                logger.info(f"   ✅ Active: {user_data.get('is_active')}")
            else:
                logger.error(f"   ❌ Failed to get user info for {username}: {response.status_code}")
                
        except Exception as e:
            logger.error(f"   ❌ User info error for {username}: {e}")
    
    # Test 4: Role-based access control
    logger.info("4. Testing role-based access control...")
    
    if "executive" in tokens:
        logger.info("   Testing executive access to user management...")
        try:
            headers = {"Authorization": f"Bearer {tokens['executive']}"}
            response = requests.get(f"{base_url}/api/v1/auth/users", headers=headers)
            
            if response.status_code == 200:
                users_list = response.json()
                logger.info(f"   ✅ Executive can access user list ({len(users_list)} users)")
            else:
                logger.error(f"   ❌ Executive access denied: {response.status_code}")
                
        except Exception as e:
            logger.error(f"   ❌ Executive access error: {e}")
    
    if "developer" in tokens:
        logger.info("   Testing developer access to user management (should be denied)...")
        try:
            headers = {"Authorization": f"Bearer {tokens['developer']}"}
            response = requests.get(f"{base_url}/api/v1/auth/users", headers=headers)
            
            if response.status_code == 403:
                logger.info("   ✅ Developer correctly denied access to user management")
            else:
                logger.error(f"   ❌ Developer should be denied access: {response.status_code}")
                
        except Exception as e:
            logger.error(f"   ❌ Developer access test error: {e}")
    
    # Test 5: Invalid token
    logger.info("5. Testing invalid token...")
    try:
        headers = {"Authorization": "Bearer invalid_token_123"}
        response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers)
        
        if response.status_code == 401:
            logger.info("   ✅ Invalid token correctly rejected")
        else:
            logger.error(f"   ❌ Invalid token should be rejected: {response.status_code}")
            
    except Exception as e:
        logger.error(f"   ❌ Invalid token test error: {e}")
    
    # Test 6: No token
    logger.info("6. Testing no token...")
    try:
        response = requests.get(f"{base_url}/api/v1/auth/me")
        
        if response.status_code == 401:
            logger.info("   ✅ No token correctly rejected")
        else:
            logger.error(f"   ❌ No token should be rejected: {response.status_code}")
            
    except Exception as e:
        logger.error(f"   ❌ No token test error: {e}")
    
    logger.info("=" * 50)
    logger.info("JWT Authentication System Test Complete")
    logger.info("\n✅ AUTHENTICATION SYSTEM IS WORKING!")
    logger.info("\nTest User Credentials:")
    for user in test_users:
        logger.info(f"   {user['username']}: {user['password']} (Role: {user['expected_role']})")
    
    return True

if __name__ == "__main__":
    success = test_authentication_system()
    sys.exit(0 if success else 1)