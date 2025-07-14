#!/usr/bin/env python3
"""
Script to generate correct password hashes for demo credentials
"""
from passlib.context import CryptContext

# Initialize the same password context as the backend
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Demo credentials
demo_credentials = [
    ("admin@school.edu", "admin123"),
    ("teacher@schoolsms.com", "teacher123"),
    ("emma.smith@student.schoolsms.com", "student123"),
    ("john.smith@email.com", "guardian123"),
]

print("-- SQL script to update demo user password hashes")
print("-- Generated password hashes for demo credentials\n")

for email, password in demo_credentials:
    hashed = pwd_context.hash(password)
    print(f"UPDATE users SET password_hash = '{hashed}' WHERE email = '{email}';")

print("\n-- Verification queries")
for email, password in demo_credentials:
    print(f"SELECT email, 'password: {password}' as password FROM users WHERE email = '{email}';")
