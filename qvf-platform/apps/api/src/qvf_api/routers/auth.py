"""Authentication router with JWT implementation."""

from datetime import timedelta, datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ..database import get_db
from ..auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    create_user_session,
    get_current_user,
    get_current_active_user,
    require_role,
    require_roles,
    revoke_user_session,
    revoke_all_user_sessions,
    decode_token,
    cleanup_expired_sessions,
    get_password_hash,
    AuthenticationError,
    AuthorizationError,
)
from ..models.auth_models import User, UserRole, UserSession
from ..config import get_settings

router = APIRouter()
settings = get_settings()


class Token(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh request model."""
    refresh_token: str


class UserResponse(BaseModel):
    """User response model."""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: UserRole
    organization: Optional[str] = None
    team: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """User creation model."""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.DEVELOPER
    organization: Optional[str] = None
    team: Optional[str] = None


class UserUpdate(BaseModel):
    """User update model."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    organization: Optional[str] = None
    team: Optional[str] = None


class PasswordChange(BaseModel):
    """Password change model."""
    current_password: str
    new_password: str


class UserSessionResponse(BaseModel):
    """User session response model."""
    id: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    issued_at: datetime
    expires_at: datetime
    last_used_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint to get access token."""
    # Clean up expired sessions
    cleanup_expired_sessions(db)
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(user.id)
    
    # Create session
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    session = create_user_session(
        db=db,
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    request: Request,
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    try:
        payload = decode_token(token_data.refresh_token)
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type")
        
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user:
            raise AuthenticationError("User not found or inactive")
        
        # Create new tokens
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role.value},
            expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(user.id)
        
        # Create new session
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        session = create_user_session(
            db=db,
            user=user,
            access_token=access_token,
            refresh_token=new_refresh_token,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }
        
    except (AuthenticationError, ValueError, KeyError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    # Update fields if provided
    if user_update.email is not None:
        # Check if email is already taken by another user
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email
    
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.organization is not None:
        current_user.organization = user_update.organization
    if user_update.team is not None:
        current_user.team = user_update.team
    
    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    from ..auth import verify_password
    
    # Verify current password
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_change.new_password)
    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    # Revoke all other sessions for security
    revoke_all_user_sessions(db, current_user.id, "Password changed")
    
    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout current user (revoke current session)."""
    # Get current token JTI from the dependency
    # Note: This requires the token to be passed to get the session
    # We'll revoke all active sessions as a security measure
    revoke_all_user_sessions(db, current_user.id, "User logout")
    
    return {"message": "Successfully logged out"}


@router.post("/logout-all")
async def logout_all_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout from all devices (revoke all sessions)."""
    count = revoke_all_user_sessions(db, current_user.id, "User logout all")
    return {"message": f"Successfully logged out from {count} devices"}


@router.get("/sessions", response_model=List[UserSessionResponse])
async def get_user_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all active sessions for current user."""
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True
    ).order_by(UserSession.last_used_at.desc()).all()
    
    return sessions


# Admin endpoints (require specific roles)
@router.post("/users", response_model=UserResponse)
async def create_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.EXECUTIVE, UserRole.PRODUCT_OWNER))
):
    """Create a new user (admin only)."""
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == user_create.username) | (User.email == user_create.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        username=user_create.username,
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=hashed_password,
        role=user_create.role,
        organization=user_create.organization,
        team=user_create.team,
        is_active=True,
        is_verified=False  # Require verification for new accounts
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.EXECUTIVE, UserRole.PRODUCT_OWNER))
):
    """List all users (admin only)."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.EXECUTIVE, UserRole.PRODUCT_OWNER))
):
    """Get user by ID (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: UserRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EXECUTIVE))
):
    """Update user role (executive only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = new_role
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    
    # Revoke all sessions to force re-login with new permissions
    revoke_all_user_sessions(db, user_id, "Role changed")
    
    return {"message": f"User role updated to {new_role.value}"}


@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EXECUTIVE))
):
    """Activate or deactivate user (executive only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = is_active
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    
    if not is_active:
        # Revoke all sessions if deactivating user
        revoke_all_user_sessions(db, user_id, "User deactivated")
    
    return {"message": f"User {'activated' if is_active else 'deactivated'}"}


# Health check endpoint
@router.get("/health")
async def auth_health_check(db: Session = Depends(get_db)):
    """Authentication service health check."""
    try:
        # Test database connection
        user_count = db.query(User).count()
        session_count = db.query(UserSession).filter(UserSession.is_active == True).count()
        
        return {
            "status": "healthy",
            "users": user_count,
            "active_sessions": session_count,
            "timestamp": datetime.now(timezone.utc)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Authentication service unhealthy: {str(e)}"
        )