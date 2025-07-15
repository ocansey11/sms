#!/usr/bin/env python3
"""
Script to create demo users using the backend's user creation API
This ensures passwords are properly hashed and users are created correctly
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append('/app')

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import async_session_factory
from app.db import crud, schemas
from app.core.security import SecurityManager
from app.db.models import User
from app.db.crud import user

async def check_existing_users():
    """Check which demo users already exist"""
    demo_emails = [
        'admin@school.edu',
        'sarah.johnson@teacher.schoolsms.com',
        'mike.davis@teacher.schoolsms.com',
        'emma.smith@student.schoolsms.com',
        'noah.jones@student.schoolsms.com',
        'olivia.brown@student.schoolsms.com',
        'liam.wilson@student.schoolsms.com',
        'john.smith@email.com',
        'mary.jones@email.com',
        'david.brown@email.com',
        'lisa.wilson@email.com',
        'robert.taylor@email.com',
        'jennifer.martin@email.com'
    ]
    
    existing_users = []
    missing_users = []
    
    async with async_session_factory() as db:
        for email in demo_emails:
            result = await db.execute(select(User).where(User.email == email))
            if result.scalar_one_or_none():
                existing_users.append(email)
            else:
                missing_users.append(email)
    
    return existing_users, missing_users

async def create_demo_users():
    """Create demo users using the backend's user creation system"""
    
    print("Checking existing demo users...")
    existing_users, missing_users = await check_existing_users()
    
    if existing_users:
        print(f"✓ Found {len(existing_users)} existing demo users:")
        for email in existing_users:
            print(f"  - {email}")
    
    if not missing_users:
        print("✓ All demo users already exist!")
        return
    
    print(f"\n📝 Creating {len(missing_users)} missing users...")
    
    # Demo users data
    demo_users = [
        # Admin
        {
            'email': 'admin@school.edu',
            'password': 'admin123',
            'role': 'admin',
            'first_name': 'System',
            'last_name': 'Administrator'
        },
        # Teachers
        {
            'email': 'sarah.johnson@teacher.schoolsms.com',
            'password': 'teacher123',
            'role': 'teacher',
            'first_name': 'Sarah',
            'last_name': 'Johnson'
        },
        {
            'email': 'mike.davis@teacher.schoolsms.com',
            'password': 'teacher123',
            'role': 'teacher',
            'first_name': 'Mike',
            'last_name': 'Davis'
        },
        # Students
        {
            'email': 'emma.smith@student.schoolsms.com',
            'password': 'student123',
            'role': 'student',
            'first_name': 'Emma',
            'last_name': 'Smith'
        },
        {
            'email': 'noah.jones@student.schoolsms.com',
            'password': 'student123',
            'role': 'student',
            'first_name': 'Noah',
            'last_name': 'Jones'
        },
        {
            'email': 'olivia.brown@student.schoolsms.com',
            'password': 'student123',
            'role': 'student',
            'first_name': 'Olivia',
            'last_name': 'Brown'
        },
        {
            'email': 'liam.wilson@student.schoolsms.com',
            'password': 'student123',
            'role': 'student',
            'first_name': 'Liam',
            'last_name': 'Wilson'
        },
        # Guardians
        {
            'email': 'john.smith@email.com',
            'password': 'guardian123',
            'role': 'guardian',
            'first_name': 'John',
            'last_name': 'Smith'
        },
        {
            'email': 'mary.jones@email.com',
            'password': 'guardian123',
            'role': 'guardian',
            'first_name': 'Mary',
            'last_name': 'Jones'
        },
        {
            'email': 'david.brown@email.com',
            'password': 'guardian123',
            'role': 'guardian',
            'first_name': 'David',
            'last_name': 'Brown'
        },
        {
            'email': 'lisa.wilson@email.com',
            'password': 'guardian123',
            'role': 'guardian',
            'first_name': 'Lisa',
            'last_name': 'Wilson'
        },
        {
            'email': 'robert.taylor@email.com',
            'password': 'guardian123',
            'role': 'guardian',
            'first_name': 'Robert',
            'last_name': 'Taylor'
        },
        {
            'email': 'jennifer.martin@email.com',
            'password': 'guardian123',
            'role': 'guardian',
            'first_name': 'Jennifer',
            'last_name': 'Martin'
        }
    ]
    
    async with async_session_factory() as db:
        users_created = 0
        
        # Create only missing users
        for user_data in demo_users:
            if user_data['email'] in missing_users:
                try:
                    user_create = schemas.UserCreate(
                        email=user_data['email'],
                        password=user_data['password'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        role=user_data['role']
                    )
                    
                    # Use the CRUD function to create user (this will hash the password)
                    created_user = await user.create(db, obj_in=user_create)
                    print(f"✓ Created {user_data['role']}: {user_data['email']}")
                    users_created += 1
                    
                except Exception as e:
                    print(f"✗ Failed to create {user_data['email']}: {str(e)}")
    
    print(f"\n🎉 Created {users_created} new demo users!")
    
    # Show all demo credentials
    print("\n📋 All Demo Credentials:")
    print("👨‍💼 Admin: admin@school.edu / admin123")
    print("👩‍🏫 Teacher: sarah.johnson@teacher.schoolsms.com / teacher123")
    print("👨‍🏫 Teacher: mike.davis@teacher.schoolsms.com / teacher123")
    print("👩‍🎓 Student: emma.smith@student.schoolsms.com / student123")
    print("👨‍🎓 Student: noah.jones@student.schoolsms.com / student123")
    print("👩‍🎓 Student: olivia.brown@student.schoolsms.com / student123")
    print("👨‍🎓 Student: liam.wilson@student.schoolsms.com / student123")
    print("👨‍👩‍👧‍👦 Guardian: john.smith@email.com / guardian123")
    print("👨‍👩‍👧‍👦 Guardian: mary.jones@email.com / guardian123")
    print("👨‍👩‍👧‍👦 Guardian: david.brown@email.com / guardian123")
    print("👨‍👩‍👧‍👦 Guardian: lisa.wilson@email.com / guardian123")
    print("👨‍👩‍👧‍👦 Guardian: robert.taylor@email.com / guardian123")
    print("👨‍👩‍👧‍👦 Guardian: jennifer.martin@email.com / guardian123")

if __name__ == "__main__":
    asyncio.run(create_demo_users())
