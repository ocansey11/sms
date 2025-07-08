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
from app.db.database import async_session_factory
from app.db import crud, schemas
from app.core.security import SecurityManager
from app.db.models import User
from app.db.crud import user

async def create_demo_users():
    """Create demo users using the backend's user creation system"""
    
    # Demo users data (excluding admin - we'll create admin manually)
    demo_users = [
        # 2 Teachers
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
        
        # 4 Students
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
        
        # 6 Guardians
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
        print("Creating demo users...")
        
        # First, create admin user manually with proper password hashing
        print("Creating admin user...")
        admin_password_hash = SecurityManager.get_password_hash("admin123")
        admin_user = User(
            email="admin@school.edu",
            password_hash=admin_password_hash,
            first_name="System",
            last_name="Administrator",
            role="admin",
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        await db.commit()
        print(f"✓ Created admin: admin@school.edu")
        
        # Create other users using the user creation schema
        for user_data in demo_users:
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
                
            except Exception as e:
                print(f"✗ Failed to create {user_data['email']}: {str(e)}")
    
    print("\nDemo Users Created Successfully!")
    print("\nDemo Credentials:")
    print("Admin: admin@school.edu / admin123")
    print("Teacher: sarah.johnson@teacher.schoolsms.com / teacher123")
    print("Teacher: mike.davis@teacher.schoolsms.com / teacher123")
    print("Student: emma.smith@student.schoolsms.com / student123")
    print("Student: noah.jones@student.schoolsms.com / student123")
    print("Student: olivia.brown@student.schoolsms.com / student123")
    print("Student: liam.wilson@student.schoolsms.com / student123")
    print("Guardian: john.smith@email.com / guardian123")
    print("Guardian: mary.jones@email.com / guardian123")
    print("Guardian: david.brown@email.com / guardian123")
    print("Guardian: lisa.wilson@email.com / guardian123")
    print("Guardian: robert.taylor@email.com / guardian123")
    print("Guardian: jennifer.martin@email.com / guardian123")

if __name__ == "__main__":
    asyncio.run(create_demo_users())
