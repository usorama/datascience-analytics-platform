"""SQLAlchemy models for authentication and user management."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..database import Base


class UserRole(str, enum.Enum):
    """User roles for role-based access control."""
    EXECUTIVE = "executive"
    PRODUCT_OWNER = "product_owner"
    SCRUM_MASTER = "scrum_master"
    DEVELOPER = "developer"


class User(Base):
    """Model for user authentication and profile."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Role-based permissions
    role = Column(Enum(UserRole), nullable=False, default=UserRole.DEVELOPER)
    
    # Profile information
    organization = Column(String(255))
    team = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    qvf_sessions = relationship("QVFSession", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    """Model for tracking user sessions and tokens."""
    
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Token information
    token_jti = Column(String(255), unique=True, index=True, nullable=False)  # JWT ID
    access_token_hash = Column(String(255), nullable=False)
    refresh_token_hash = Column(String(255))
    
    # Session metadata
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(Text)
    device_info = Column(Text)
    
    # Token lifecycle
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_used_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Session status
    is_active = Column(Boolean, default=True)
    is_revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime(timezone=True))
    revoked_reason = Column(String(255))
    
    # Relationship
    user = relationship("User", back_populates="sessions")


class UserPreferences(Base):
    """Model for user preferences and settings."""
    
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # UI Preferences
    theme = Column(String(50), default="light")  # light, dark, auto
    dashboard_layout = Column(String(50), default="default")
    items_per_page = Column(Integer, default=25)
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    desktop_notifications = Column(Boolean, default=True)
    
    # QVF preferences
    default_qvf_configuration = Column(String(50), default="agile")
    auto_save_sessions = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", uselist=False)