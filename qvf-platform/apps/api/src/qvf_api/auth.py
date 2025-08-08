"""Authentication utilities for JWT token management and password hashing."""

from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
import hashlib
import secrets
import logging

from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .database import get_db
from .config import get_settings
from .models.auth_models import User, UserSession, UserRole

logger = logging.getLogger(__name__)
settings = get_settings()

# Password hashing context with bcrypt configuration
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception:
    # Fallback for bcrypt version compatibility
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass


class AuthorizationError(Exception):
    """Custom exception for authorization errors."""
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    
    # Add standard JWT claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_urlsafe(32),  # JWT ID for session tracking
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(user_id: int) -> str:
    """Create JWT refresh token."""
    data = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": secrets.token_urlsafe(32),
    }
    expire = datetime.now(timezone.utc) + timedelta(days=30)  # 30 days for refresh token
    data.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    
    encoded_jwt = jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError as e:
        logger.warning(f"Token decode error: {e}")
        raise AuthenticationError("Invalid token")


def hash_token(token: str) -> str:
    """Create a hash of the token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password."""
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user:
        logger.warning(f"Authentication failed: User not found for {username}")
        return None
    
    if not user.is_active:
        logger.warning(f"Authentication failed: Inactive user {username}")
        return None
    
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed: Invalid password for {username}")
        return None
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    logger.info(f"User authenticated successfully: {username}")
    return user


def create_user_session(
    db: Session,
    user: User,
    access_token: str,
    refresh_token: str,
    ip_address: str = None,
    user_agent: str = None
) -> UserSession:
    """Create a new user session."""
    # Decode token to get JTI and expiration
    token_payload = decode_token(access_token)
    
    session = UserSession(
        user_id=user.id,
        token_jti=token_payload["jti"],
        access_token_hash=hash_token(access_token),
        refresh_token_hash=hash_token(refresh_token) if refresh_token else None,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=datetime.fromtimestamp(token_payload["exp"], tz=timezone.utc),
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    logger.info(f"Created session for user {user.username}: {session.id}")
    return session


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        
        if user_id is None or jti is None:
            raise credentials_exception
            
    except AuthenticationError:
        raise credentials_exception
    
    # Check if session is still active
    session = db.query(UserSession).filter(
        UserSession.token_jti == jti,
        UserSession.is_active == True,
        UserSession.is_revoked == False
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise credentials_exception
    
    # Update session last used
    session.last_used_at = datetime.now(timezone.utc)
    db.commit()
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(required_role: UserRole):
    """Decorator to require specific user role."""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role.value}"
            )
        return current_user
    return role_checker


def require_roles(*required_roles: UserRole):
    """Decorator to require one of multiple user roles."""
    def roles_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in required_roles:
            roles_str = ", ".join([role.value for role in required_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {roles_str}"
            )
        return current_user
    return roles_checker


def revoke_user_session(db: Session, token_jti: str, reason: str = "Manual logout") -> bool:
    """Revoke a user session."""
    session = db.query(UserSession).filter(UserSession.token_jti == token_jti).first()
    if session:
        session.is_revoked = True
        session.is_active = False
        session.revoked_at = datetime.now(timezone.utc)
        session.revoked_reason = reason
        db.commit()
        logger.info(f"Session revoked: {token_jti} - {reason}")
        return True
    return False


def revoke_all_user_sessions(db: Session, user_id: int, reason: str = "Security logout") -> int:
    """Revoke all active sessions for a user."""
    sessions = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.is_active == True
    ).all()
    
    count = 0
    for session in sessions:
        session.is_revoked = True
        session.is_active = False
        session.revoked_at = datetime.now(timezone.utc)
        session.revoked_reason = reason
        count += 1
    
    db.commit()
    logger.info(f"Revoked {count} sessions for user {user_id} - {reason}")
    return count


def cleanup_expired_sessions(db: Session) -> int:
    """Clean up expired sessions."""
    expired_sessions = db.query(UserSession).filter(
        UserSession.expires_at < datetime.now(timezone.utc),
        UserSession.is_active == True
    ).all()
    
    count = 0
    for session in expired_sessions:
        session.is_active = False
        session.revoked_reason = "Token expired"
        count += 1
    
    db.commit()
    logger.info(f"Cleaned up {count} expired sessions")
    return count