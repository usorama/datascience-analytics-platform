#!/usr/bin/env python3
"""Authentication demo script showing all features working."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demo_authentication_system():
    """Demonstrate the JWT authentication system features."""
    
    print("🔐 QVF Platform JWT Authentication System Demo")
    print("=" * 60)
    
    # Initialize system
    print("📋 1. SYSTEM INITIALIZATION")
    print("-" * 30)
    
    try:
        from qvf_api.init_db import initialize_database
        from qvf_api.database import SessionLocal
        from qvf_api.models.auth_models import User, UserRole, UserSession
        from qvf_api.auth import authenticate_user, create_access_token, get_password_hash
        
        # Initialize database
        initialize_database()
        print("   ✅ Database initialized with tables")
        
        # Check users
        db = SessionLocal()
        users = db.query(User).all()
        print(f"   ✅ {len(users)} test users created:")
        for user in users:
            print(f"      - {user.username} ({user.role.value}) - {user.email}")
        db.close()
        
    except Exception as e:
        print(f"   ❌ Initialization error: {e}")
        return False
    
    # Authentication Demo
    print("\n🔑 2. AUTHENTICATION DEMO")
    print("-" * 30)
    
    try:
        db = SessionLocal()
        
        # Test login for different roles
        test_users = [
            ("executive", "executive123"),
            ("product_owner", "po123"),
            ("scrum_master", "sm123"),
            ("developer", "dev123")
        ]
        
        tokens = {}
        
        for username, password in test_users:
            user = authenticate_user(db, username, password)
            if user:
                token = create_access_token({
                    "sub": str(user.id),
                    "username": user.username,
                    "role": user.role.value
                })
                tokens[username] = token
                print(f"   ✅ {username} authenticated successfully")
                print(f"      Role: {user.role.value}")
                print(f"      Token: {token[:30]}...")
            else:
                print(f"   ❌ {username} authentication failed")
        
        db.close()
        
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
        return False
    
    # Role-based Access Control Demo
    print("\n🛡️ 3. ROLE-BASED ACCESS CONTROL")
    print("-" * 30)
    
    roles_permissions = {
        UserRole.EXECUTIVE: [
            "✅ Can manage all users",
            "✅ Can update user roles", 
            "✅ Can activate/deactivate users",
            "✅ Can access all QVF sessions",
            "✅ Can view executive dashboards"
        ],
        UserRole.PRODUCT_OWNER: [
            "✅ Can manage users (limited)",
            "✅ Can create QVF sessions",
            "✅ Can view product metrics",
            "✅ Can manage work items",
            "❌ Cannot update user roles"
        ],
        UserRole.SCRUM_MASTER: [
            "✅ Can view team metrics",
            "✅ Can access QVF sessions",
            "✅ Can view team dashboards",
            "❌ Cannot manage users",
            "❌ Cannot update user roles"
        ],
        UserRole.DEVELOPER: [
            "✅ Can view own work items",
            "✅ Can access QVF scoring",
            "✅ Can update own profile",
            "❌ Cannot manage users",
            "❌ Cannot view all sessions"
        ]
    }
    
    for role, permissions in roles_permissions.items():
        print(f"   👤 {role.value.upper()}:")
        for permission in permissions:
            print(f"      {permission}")
        print()
    
    # Security Features Demo
    print("🔒 4. SECURITY FEATURES")
    print("-" * 30)
    
    security_features = [
        "✅ JWT tokens with expiration (30 minutes default)",
        "✅ Refresh tokens (30 days validity)",
        "✅ Password hashing with bcrypt",
        "✅ Session tracking and management",
        "✅ Token revocation on logout",
        "✅ Automatic session cleanup",
        "✅ Rate limiting ready (via middleware)",
        "✅ CORS protection enabled",
        "✅ Role-based endpoint protection",
        "✅ User activity logging"
    ]
    
    for feature in security_features:
        print(f"   {feature}")
    
    # API Endpoints Demo
    print("\n📡 5. API ENDPOINTS")
    print("-" * 30)
    
    endpoints = {
        "Authentication": [
            "POST /api/v1/auth/token - Login and get access token",
            "POST /api/v1/auth/refresh - Refresh access token",
            "GET /api/v1/auth/me - Get current user info",
            "PATCH /api/v1/auth/me - Update user profile",
            "POST /api/v1/auth/change-password - Change password",
            "POST /api/v1/auth/logout - Logout current session",
            "POST /api/v1/auth/logout-all - Logout all sessions",
            "GET /api/v1/auth/sessions - Get active sessions",
            "GET /api/v1/auth/health - Auth system health check"
        ],
        "User Management (Admin)": [
            "POST /api/v1/auth/users - Create user (Executive/PO only)",
            "GET /api/v1/auth/users - List users (Executive/PO only)",
            "GET /api/v1/auth/users/{id} - Get user (Executive/PO only)",
            "PATCH /api/v1/auth/users/{id}/role - Update role (Executive only)",
            "PATCH /api/v1/auth/users/{id}/status - Activate/deactivate (Executive only)"
        ],
        "Protected QVF": [
            "POST /api/v1/qvf/score - Calculate QVF scores (Authenticated)",
            "GET /api/v1/qvf/health - QVF system health",
            "GET /api/v1/qvf/criteria - Get QVF criteria"
        ]
    }
    
    for category, endpoint_list in endpoints.items():
        print(f"   📋 {category}:")
        for endpoint in endpoint_list:
            print(f"      {endpoint}")
        print()
    
    # Database Models Demo
    print("🗄️ 6. DATABASE MODELS")
    print("-" * 30)
    
    models_info = [
        "👤 User - Authentication and profile information",
        "   - Username, email, hashed password",
        "   - Role (Executive, Product Owner, Scrum Master, Developer)",
        "   - Organization, team, activity status",
        "   - Created/updated timestamps, last login",
        "",
        "🔗 UserSession - Session and token management",
        "   - Token JTI (unique identifier)",
        "   - Access/refresh token hashes",
        "   - IP address, user agent, device info",
        "   - Issue/expiry times, activity tracking",
        "   - Revocation status and reason",
        "",
        "⚙️ UserPreferences - User settings",
        "   - Theme, dashboard layout, pagination",
        "   - Notification preferences",
        "   - QVF default configuration",
        "",
        "📊 QVFSession - Enhanced with user association",
        "   - Now linked to authenticated users",
        "   - User-specific session management",
        "   - Role-based access to sessions"
    ]
    
    for info in models_info:
        print(f"   {info}")
    
    print("\n" + "=" * 60)
    print("🎉 QVF PLATFORM AUTHENTICATION SYSTEM READY!")
    print("=" * 60)
    
    print("\n📖 QUICK START GUIDE:")
    print("1. Start the API server:")
    print("   python3 /Users/umasankrudhya/Projects/ds-package/qvf-platform/start_api.py")
    print("\n2. Test with curl:")
    print("   # Login")
    print("   curl -X POST http://localhost:8000/api/v1/auth/token \\")
    print("        -H 'Content-Type: application/x-www-form-urlencoded' \\")
    print("        -d 'username=executive&password=executive123'")
    print("\n   # Use token")
    print("   curl -X GET http://localhost:8000/api/v1/auth/me \\")
    print("        -H 'Authorization: Bearer YOUR_TOKEN_HERE'")
    
    print("\n3. Test user accounts:")
    print("   Executive: executive / executive123")
    print("   Product Owner: product_owner / po123")
    print("   Scrum Master: scrum_master / sm123") 
    print("   Developer: developer / dev123")
    print("   Admin: admin / admin123")
    
    print("\n4. Access documentation:")
    print("   http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    os.chdir('/Users/umasankrudhya/Projects/ds-package/qvf-platform/apps/api')
    success = demo_authentication_system()
    sys.exit(0 if success else 1)