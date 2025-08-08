#!/usr/bin/env python3
"""Basic test of authentication functions without server."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_auth_functions():
    """Test basic authentication functions."""
    print("Testing basic authentication functions...")
    print("=" * 50)
    
    try:
        # Test password hashing
        print("1. Testing password hashing...")
        from qvf_api.auth import get_password_hash, verify_password
        
        test_password = "test123"
        hashed = get_password_hash(test_password)
        print(f"   ✅ Password hashed successfully: {hashed[:20]}...")
        
        # Test password verification
        if verify_password(test_password, hashed):
            print("   ✅ Password verification successful")
        else:
            print("   ❌ Password verification failed")
            return False
            
        # Test wrong password
        if not verify_password("wrong_password", hashed):
            print("   ✅ Wrong password correctly rejected")
        else:
            print("   ❌ Wrong password should be rejected")
            return False
            
    except Exception as e:
        print(f"   ❌ Password hashing error: {e}")
        return False
    
    try:
        # Test JWT token creation
        print("2. Testing JWT token creation...")
        from qvf_api.auth import create_access_token, decode_token
        
        test_data = {"sub": "1", "username": "test", "role": "developer"}
        token = create_access_token(test_data)
        print(f"   ✅ JWT token created: {token[:20]}...")
        
        # Test token decoding
        decoded = decode_token(token)
        print(f"   ✅ Token decoded successfully")
        print(f"   ✅ Subject: {decoded.get('sub')}")
        print(f"   ✅ Username: {decoded.get('username')}")
        print(f"   ✅ Role: {decoded.get('role')}")
        
    except Exception as e:
        print(f"   ❌ JWT token error: {e}")
        return False
    
    try:
        # Test database models
        print("3. Testing database models...")
        from qvf_api.models.auth_models import User, UserRole, UserSession
        
        print(f"   ✅ User model imported successfully")
        print(f"   ✅ UserRole enum: {list(UserRole)}")
        print(f"   ✅ UserSession model imported successfully")
        
    except Exception as e:
        print(f"   ❌ Database models error: {e}")
        return False
    
    try:
        # Test database initialization
        print("4. Testing database initialization...")
        from qvf_api.init_db import initialize_database
        
        # This will create tables and test users
        initialize_database()
        print("   ✅ Database initialized successfully")
        
        # Verify users were created
        from qvf_api.database import SessionLocal
        from qvf_api.models.auth_models import User
        
        db = SessionLocal()
        try:
            user_count = db.query(User).count()
            print(f"   ✅ Found {user_count} users in database")
            
            # List users
            users = db.query(User).all()
            for user in users:
                print(f"   ✅ User: {user.username} ({user.role.value}) - {user.email}")
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"   ❌ Database initialization error: {e}")
        return False
    
    print("=" * 50)
    print("✅ ALL BASIC AUTHENTICATION TESTS PASSED!")
    print("\nThe authentication system is ready for use.")
    print("\nTo start the API server:")
    print("  python3 /Users/umasankrudhya/Projects/ds-package/qvf-platform/start_api.py")
    print("\nTest user credentials:")
    print("  Executive: executive / executive123")
    print("  Product Owner: product_owner / po123") 
    print("  Scrum Master: scrum_master / sm123")
    print("  Developer: developer / dev123")
    print("  Admin: admin / admin123")
    
    return True

if __name__ == "__main__":
    os.chdir('/Users/umasankrudhya/Projects/ds-package/qvf-platform/apps/api')
    success = test_basic_auth_functions()
    sys.exit(0 if success else 1)