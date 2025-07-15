#!/usr/bin/env python3
"""
Demo Credentials Tester for SMS System
Tests all demo user credentials to ensure they work properly
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any

# Base URL for the API
BASE_URL = "http://localhost:8000"

# All Demo Credentials to Test
DEMO_CREDENTIALS = [
    # Admin User
    {
        "email": "admin@school.edu",
        "password": "admin123",
        "role": "admin",
        "name": "System Administrator",
        "description": "Main admin account for system management"
    },
    
    # Teacher shown in LoginPage
    {
        "email": "john.doe@school.edu", 
        "password": "teacher123",
        "role": "teacher",
        "name": "John Doe",
        "description": "Demo teacher account shown in login page"
    },
    
    # Teachers from demo users script
    {
        "email": "sarah.johnson@teacher.schoolsms.com",
        "password": "teacher123",
        "role": "teacher", 
        "name": "Sarah Johnson",
        "description": "Demo teacher from create_demo_users.py"
    },
    {
        "email": "mike.davis@teacher.schoolsms.com",
        "password": "teacher123",
        "role": "teacher",
        "name": "Mike Davis", 
        "description": "Demo teacher from create_demo_users.py"
    },
    
    # Students from demo users script
    {
        "email": "emma.smith@student.schoolsms.com",
        "password": "student123",
        "role": "student",
        "name": "Emma Smith",
        "description": "Demo student from create_demo_users.py"
    },
    {
        "email": "noah.jones@student.schoolsms.com",
        "password": "student123", 
        "role": "student",
        "name": "Noah Jones",
        "description": "Demo student from create_demo_users.py"
    },
    {
        "email": "olivia.brown@student.schoolsms.com",
        "password": "student123",
        "role": "student", 
        "name": "Olivia Brown",
        "description": "Demo student from create_demo_users.py"
    },
    {
        "email": "liam.wilson@student.schoolsms.com",
        "password": "student123",
        "role": "student",
        "name": "Liam Wilson", 
        "description": "Demo student from create_demo_users.py"
    },
    
    # Guardians from demo users script
    {
        "email": "john.smith@email.com",
        "password": "guardian123",
        "role": "guardian",
        "name": "John Smith",
        "description": "Demo guardian from create_demo_users.py"
    },
    {
        "email": "mary.jones@email.com", 
        "password": "guardian123",
        "role": "guardian",
        "name": "Mary Jones",
        "description": "Demo guardian from create_demo_users.py"
    },
    {
        "email": "david.brown@email.com",
        "password": "guardian123",
        "role": "guardian",
        "name": "David Brown",
        "description": "Demo guardian from create_demo_users.py"
    },
    {
        "email": "lisa.wilson@email.com",
        "password": "guardian123", 
        "role": "guardian",
        "name": "Lisa Wilson",
        "description": "Demo guardian from create_demo_users.py"
    },
    {
        "email": "robert.taylor@email.com",
        "password": "guardian123",
        "role": "guardian", 
        "name": "Robert Taylor",
        "description": "Demo guardian from create_demo_users.py"
    },
    {
        "email": "jennifer.martin@email.com",
        "password": "guardian123",
        "role": "guardian",
        "name": "Jennifer Martin",
        "description": "Demo guardian from create_demo_users.py"
    }
]

async def test_login(session: aiohttp.ClientSession, credentials: Dict[str, Any]) -> Dict[str, Any]:
    """Test login for a single set of credentials"""
    
    login_url = f"{BASE_URL}/api/auth/login"
    
    # Prepare login data
    login_data = {
        "email": credentials["email"],
        "password": credentials["password"]
    }
    
    try:
        async with session.post(login_url, json=login_data) as response:
            result = {
                "email": credentials["email"],
                "role": credentials["role"],
                "name": credentials["name"],
                "description": credentials["description"],
                "status_code": response.status,
                "success": False,
                "token": None,
                "user_data": None,
                "error": None
            }
            
            if response.status == 200:
                response_data = await response.json()
                result["success"] = True
                result["token"] = response_data.get("access_token", "No token")
                result["user_data"] = response_data.get("user", {})
            else:
                error_text = await response.text()
                result["error"] = error_text
                
            return result
            
    except Exception as e:
        return {
            "email": credentials["email"],
            "role": credentials["role"], 
            "name": credentials["name"],
            "description": credentials["description"],
            "status_code": 0,
            "success": False,
            "token": None,
            "user_data": None,
            "error": str(e)
        }

async def test_all_credentials():
    """Test all demo credentials"""
    
    print("🧪 Testing All Demo Credentials for SMS System")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Test each credential
        results = []
        for i, cred in enumerate(DEMO_CREDENTIALS, 1):
            print(f"\n[{i}/{len(DEMO_CREDENTIALS)}] Testing: {cred['name']} ({cred['email']})")
            print(f"    Role: {cred['role']}")
            print(f"    Description: {cred['description']}")
            
            result = await test_login(session, cred)
            results.append(result)
            
            if result["success"]:
                print(f"    ✅ LOGIN SUCCESS")
                print(f"    📝 User ID: {result['user_data'].get('id', 'N/A')}")
                print(f"    🔑 Token received: {result['token'][:20]}..." if result['token'] else "    🔑 No token")
            else:
                print(f"    ❌ LOGIN FAILED")
                print(f"    📛 Status: {result['status_code']}")
                print(f"    📛 Error: {result['error']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY OF DEMO CREDENTIAL TESTS")
    print("=" * 60)
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"✅ Successful logins: {len(successful)}/{len(results)}")
    print(f"❌ Failed logins: {len(failed)}/{len(results)}")
    
    if successful:
        print(f"\n🎉 WORKING CREDENTIALS:")
        for result in successful:
            print(f"    ✅ {result['name']} ({result['email']}) - {result['role']}")
    
    if failed:
        print(f"\n⚠️  FAILED CREDENTIALS:")
        for result in failed:
            print(f"    ❌ {result['name']} ({result['email']}) - {result['role']}")
            print(f"       Error: {result['error']}")
    
    print("\n" + "=" * 60)
    if len(successful) == len(results):
        print("🎯 ALL DEMO CREDENTIALS ARE WORKING! 🎯")
    else:
        print("⚠️  SOME CREDENTIALS NEED ATTENTION ⚠️")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    asyncio.run(test_all_credentials())
