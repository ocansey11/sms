from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Test password hash verification
password = "teacher123"
hash = "$2b$12$PyGXVmVkCCU4oHOpesMU/e2tYb698tsXNCn6KBaUyeN/ZVc3D9blm"

if pwd_context.verify(password, hash):
    print("Password verification successful")
else:
    print("Password verification failed")
