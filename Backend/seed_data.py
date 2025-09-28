"""
Seed data for StudHelper Backend development
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Class, ClassMembership
from app.utils.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_seed_data():
    """Create seed data for development"""
    db = SessionLocal()
    
    try:
        # Create demo teacher
        teacher = User(
            email="teacher@studhelper.com",
            username="demo_teacher",
            full_name="Demo Teacher",
            hashed_password=get_password_hash("teacher123"),
            is_active=True
        )
        db.add(teacher)
        db.flush()
        
        # Create demo student
        student = User(
            email="student@studhelper.com",
            username="demo_student",
            full_name="Demo Student",
            hashed_password=get_password_hash("student123"),
            is_active=True
        )
        db.add(student)
        db.flush()
        
        # Create demo class
        demo_class = Class(
            name="Introduction to Physics",
            description="A comprehensive introduction to physics concepts",
            class_code="PHYS101",
            owner_id=teacher.id,
            is_active=True
        )
        db.add(demo_class)
        db.flush()
        
        # Add teacher as manager
        teacher_membership = ClassMembership(
            user_id=teacher.id,
            class_id=demo_class.id,
            is_manager=True,
            can_read=True,
            can_chat=True,
            can_share_class=True,
            can_upload_documents=True,
            max_concurrent_chats=10,
            is_sponsored=False,
            daily_token_limit=5_000_000,
            weekly_token_limit=25_000_000,
            monthly_token_limit=75_000_000
        )
        db.add(teacher_membership)
        
        # Add student as member
        student_membership = ClassMembership(
            user_id=student.id,
            class_id=demo_class.id,
            is_manager=False,
            can_read=True,
            can_chat=True,
            can_share_class=False,
            can_upload_documents=True,
            max_concurrent_chats=3,
            is_sponsored=True,  # Teacher sponsors student
            daily_token_limit=1_000_000,
            weekly_token_limit=5_000_000,
            monthly_token_limit=15_000_000
        )
        db.add(student_membership)
        
        db.commit()
        
        logger.info("✅ Seed data created successfully!")
        logger.info("Demo accounts:")
        logger.info("  Teacher: teacher@studhelper.com / teacher123")
        logger.info("  Student: student@studhelper.com / student123")
        logger.info("  Class Code: PHYS101")
        
    except Exception as e:
        logger.error(f"❌ Error creating seed data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_seed_data()

