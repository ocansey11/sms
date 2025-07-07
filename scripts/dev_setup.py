#!/usr/bin/env python3
"""
Development script for School Management System
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.db.database import init_db
from app.db.models import User, Class, Quiz, AttendanceRecord
from app.db.schemas import UserCreate, ClassCreate, QuizCreate
from app.services.auth_service import AuthService
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db_session

async def create_sample_data():
    """Create sample data for development"""
    print("Creating sample data...")
    
    async with get_db_session() as db:
        # Create admin user
        admin_data = UserCreate(
            email="admin@school.com",
            password="admin123",
            first_name="Admin",
            last_name="User",
            role="admin",
            phone="1234567890"
        )
        
        try:
            admin_user = await AuthService.register_user(db, admin_data)
            print(f"Created admin user: {admin_user.email}")
        except Exception as e:
            print(f"Admin user might already exist: {e}")
        
        # Create teacher user
        teacher_data = UserCreate(
            email="teacher@school.com",
            password="teacher123",
            first_name="Teacher",
            last_name="User",
            role="teacher",
            phone="1234567891"
        )
        
        try:
            teacher_user = await AuthService.register_user(db, teacher_data)
            print(f"Created teacher user: {teacher_user.email}")
        except Exception as e:
            print(f"Teacher user might already exist: {e}")
        
        # Create student user
        student_data = UserCreate(
            email="student@school.com",
            password="student123",
            first_name="Student",
            last_name="User",
            role="student",
            phone="1234567892"
        )
        
        try:
            student_user = await AuthService.register_user(db, student_data)
            print(f"Created student user: {student_user.email}")
        except Exception as e:
            print(f"Student user might already exist: {e}")
        
        # Create guardian user
        guardian_data = UserCreate(
            email="guardian@school.com",
            password="guardian123",
            first_name="Guardian",
            last_name="User",
            role="guardian",
            phone="1234567893"
        )
        
        try:
            guardian_user = await AuthService.register_user(db, guardian_data)
            print(f"Created guardian user: {guardian_user.email}")
        except Exception as e:
            print(f"Guardian user might already exist: {e}")
    
    print("Sample data creation completed!")

async def reset_database():
    """Reset the database"""
    print("Resetting database...")
    
    try:
        from app.db.models import Base
        from app.db.database import engine
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        
        print("Database reset completed!")
    except Exception as e:
        print(f"Error resetting database: {e}")

async def init_database():
    """Initialize the database"""
    print("Initializing database...")
    
    try:
        await init_db()
        print("Database initialization completed!")
    except Exception as e:
        print(f"Error initializing database: {e}")

async def check_database():
    """Check database connection and show basic info"""
    print("Checking database connection...")
    
    try:
        async with get_db_session() as db:
            from sqlalchemy import text
            
            # Test connection
            result = await db.execute(text("SELECT 1"))
            print("✓ Database connection successful")
            
            # Count users
            user_count = await db.execute(text("SELECT COUNT(*) FROM users"))
            count = user_count.scalar()
            print(f"✓ Total users in database: {count}")
            
            # Show user roles
            if count > 0:
                role_result = await db.execute(text("SELECT role, COUNT(*) FROM users GROUP BY role"))
                roles = role_result.fetchall()
                print("✓ User roles distribution:")
                for role, count in roles:
                    print(f"  - {role}: {count}")
    
    except Exception as e:
        print(f"✗ Database connection failed: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="School Management System Development Script")
    parser.add_argument("command", choices=[
        "init-db", "reset-db", "create-sample-data", "check-db"
    ], help="Command to run")
    
    args = parser.parse_args()
    
    if args.command == "init-db":
        asyncio.run(init_database())
    elif args.command == "reset-db":
        asyncio.run(reset_database())
    elif args.command == "create-sample-data":
        asyncio.run(create_sample_data())
    elif args.command == "check-db":
        asyncio.run(check_database())

if __name__ == "__main__":
    main()
