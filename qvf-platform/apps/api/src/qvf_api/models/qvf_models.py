"""SQLAlchemy models for QVF operations."""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class QVFSession(Base):
    """Model for QVF calculation sessions."""
    
    __tablename__ = "qvf_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_name = Column(String(255), nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Configuration
    criteria_weights = Column(JSON)  # Store criteria weights as JSON
    configuration_type = Column(String(50), default="agile")  # agile, enterprise, startup
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Results summary
    total_work_items = Column(Integer, default=0)
    average_qvf_score = Column(Float)
    high_priority_count = Column(Integer, default=0)
    medium_priority_count = Column(Integer, default=0)
    low_priority_count = Column(Integer, default=0)
    
    # Relationship
    user = relationship("User", back_populates="qvf_sessions")


class WorkItemScore(Base):
    """Model for individual work item QVF scores."""
    
    __tablename__ = "work_item_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer)  # Foreign key to QVFSession (will add proper FK later)
    
    # Work item details
    work_item_id = Column(String(255), nullable=False)
    title = Column(String(500))
    description = Column(Text)
    
    # Input values
    business_value = Column(Integer)
    technical_complexity = Column(Integer)
    story_points = Column(Integer)
    priority = Column(String(50))
    risk_level = Column(Integer)
    
    # QVF calculated scores
    qvf_score = Column(Float)
    quality_score = Column(Float)
    value_score = Column(Float)
    framework_alignment = Column(Float)
    category = Column(String(50))  # High, Medium, Low
    
    # Detailed criteria scores (stored as JSON)
    criteria_scores = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QVFCalculationLog(Base):
    """Model for logging QVF calculations for audit and debugging."""
    
    __tablename__ = "qvf_calculation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer)  # Link to QVFSession
    
    # Calculation metadata
    calculation_method = Column(String(50))  # qvf_core, fallback
    qvf_core_available = Column(Boolean)
    ai_enhanced = Column(Boolean, default=False)
    
    # Performance metrics
    calculation_duration_ms = Column(Float)
    work_items_count = Column(Integer)
    
    # Error information (if any)
    has_error = Column(Boolean, default=False)
    error_message = Column(Text)
    
    # Request/response data for debugging
    input_data = Column(JSON)  # Sanitized input data
    output_summary = Column(JSON)  # Summary of output
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())