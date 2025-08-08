"""Database initialization script with test users for each role."""

import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from .database import SessionLocal, init_database
from .models.auth_models import User, UserRole, UserPreferences
from .auth import get_password_hash

logger = logging.getLogger(__name__)


def create_test_users(db: Session) -> None:
    """Create test users for each role if they don't exist."""
    
    test_users = [
        {
            "username": "executive",
            "email": "executive@qvf.com",
            "password": "executive123",
            "full_name": "Executive User",
            "role": UserRole.EXECUTIVE,
            "organization": "QVF Platform",
            "team": "Executive Team",
            "is_verified": True,
        },
        {
            "username": "product_owner",
            "email": "po@qvf.com",
            "password": "po123",
            "full_name": "Product Owner",
            "role": UserRole.PRODUCT_OWNER,
            "organization": "QVF Platform",
            "team": "Product Team",
            "is_verified": True,
        },
        {
            "username": "scrum_master",
            "email": "sm@qvf.com",
            "password": "sm123",
            "full_name": "Scrum Master",
            "role": UserRole.SCRUM_MASTER,
            "organization": "QVF Platform",
            "team": "Agile Team",
            "is_verified": True,
        },
        {
            "username": "developer",
            "email": "dev@qvf.com",
            "password": "dev123",
            "full_name": "Developer User",
            "role": UserRole.DEVELOPER,
            "organization": "QVF Platform",
            "team": "Development Team",
            "is_verified": True,
        },
        {
            "username": "admin",
            "email": "admin@qvf.com",
            "password": "admin123",
            "full_name": "System Administrator",
            "role": UserRole.EXECUTIVE,
            "organization": "QVF Platform",
            "team": "Admin Team",
            "is_verified": True,
        }
    ]
    
    created_count = 0
    for user_data in test_users:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == user_data["username"]) | 
            (User.email == user_data["email"])
        ).first()
        
        if existing_user:
            logger.info(f"User {user_data['username']} already exists, skipping...")
            continue
        
        # Create new user
        hashed_password = get_password_hash(user_data.pop("password"))
        user = User(
            **user_data,
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create user preferences
        preferences = UserPreferences(
            user_id=user.id,
            theme="light",
            dashboard_layout="default",
            items_per_page=25,
            email_notifications=True,
            desktop_notifications=True,
            default_qvf_configuration="agile",
            auto_save_sessions=True,
        )
        
        db.add(preferences)
        db.commit()
        
        logger.info(f"Created user: {user.username} ({user.role.value})")
        created_count += 1
    
    logger.info(f"Created {created_count} new test users")
    return created_count


def create_sample_qvf_session(db: Session) -> None:
    """Create a sample QVF session for testing."""
    from .models.qvf_models import QVFSession, WorkItemScore
    
    # Get a user to associate with the session
    user = db.query(User).filter(User.role == UserRole.PRODUCT_OWNER).first()
    if not user:
        logger.warning("No product owner found, skipping sample QVF session creation")
        return
    
    # Check if sample session already exists
    existing_session = db.query(QVFSession).filter(
        QVFSession.session_name == "Sample QVF Session"
    ).first()
    
    if existing_session:
        logger.info("Sample QVF session already exists, skipping...")
        return
    
    # Create sample QVF session
    session = QVFSession(
        session_name="Sample QVF Session",
        description="A sample QVF session for testing and demonstration purposes",
        user_id=user.id,
        criteria_weights={
            "business_value": 0.25,
            "technical_complexity": 0.20,
            "risk_level": 0.15,
            "customer_impact": 0.20,
            "strategic_alignment": 0.20
        },
        configuration_type="agile",
        is_active=True,
        total_work_items=0,
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Create some sample work item scores
    sample_work_items = [
        {
            "work_item_id": "WI-001",
            "title": "User Authentication System",
            "description": "Implement JWT-based authentication with role-based access control",
            "business_value": 9,
            "technical_complexity": 7,
            "story_points": 8,
            "priority": "High",
            "risk_level": 6,
            "qvf_score": 8.2,
            "quality_score": 8.5,
            "value_score": 8.0,
            "framework_alignment": 8.1,
            "category": "High",
        },
        {
            "work_item_id": "WI-002",
            "title": "Dashboard UI Components",
            "description": "Create reusable dashboard components for data visualization",
            "business_value": 7,
            "technical_complexity": 5,
            "story_points": 5,
            "priority": "Medium",
            "risk_level": 3,
            "qvf_score": 6.8,
            "quality_score": 7.2,
            "value_score": 6.5,
            "framework_alignment": 6.7,
            "category": "Medium",
        },
        {
            "work_item_id": "WI-003",
            "title": "Database Optimization",
            "description": "Optimize database queries for better performance",
            "business_value": 6,
            "technical_complexity": 8,
            "story_points": 13,
            "priority": "Medium",
            "risk_level": 7,
            "qvf_score": 6.2,
            "quality_score": 6.8,
            "value_score": 5.5,
            "framework_alignment": 6.3,
            "category": "Medium",
        }
    ]
    
    for item_data in sample_work_items:
        work_item = WorkItemScore(
            session_id=session.id,
            **item_data,
            criteria_scores={
                "business_value": item_data["business_value"],
                "technical_complexity": item_data["technical_complexity"],
                "risk_level": item_data["risk_level"],
            }
        )
        db.add(work_item)
    
    # Update session totals
    session.total_work_items = len(sample_work_items)
    session.high_priority_count = 1
    session.medium_priority_count = 2
    session.low_priority_count = 0
    session.average_qvf_score = 7.07  # Average of the sample scores
    
    db.commit()
    
    logger.info(f"Created sample QVF session with {len(sample_work_items)} work items")


def initialize_database() -> None:
    """Initialize the database with tables and test data."""
    logger.info("Initializing database...")
    
    try:
        # Create tables
        init_database()
        logger.info("Database tables created successfully")
        
        # Create test users
        db = SessionLocal()
        try:
            user_count = create_test_users(db)
            create_sample_qvf_session(db)
            
            logger.info(f"Database initialization complete. Created {user_count} test users")
            
            # Log test user credentials for convenience
            logger.info("Test user credentials:")
            logger.info("  Executive: executive / executive123")
            logger.info("  Product Owner: product_owner / po123")
            logger.info("  Scrum Master: scrum_master / sm123")
            logger.info("  Developer: developer / dev123")
            logger.info("  Admin: admin / admin123")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def reset_database() -> None:
    """Reset the database by dropping and recreating all tables."""
    logger.warning("Resetting database - all data will be lost!")
    
    try:
        from .database import Base, engine
        
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        logger.info("Dropped all database tables")
        
        # Reinitialize
        initialize_database()
        logger.info("Database reset complete")
        
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        raise


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize database
    initialize_database()