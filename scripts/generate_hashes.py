from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

demos = [
    ('admin@school.edu', 'admin123'),
    ('teacher@schoolsms.com', 'teacher123'),
    ('emma.smith@student.schoolsms.com', 'student123'),
    ('john.smith@email.com', 'guardian123'),
]

print('-- SQL script to fix demo passwords')
for email, password in demos:
    hashed = pwd_context.hash(password)
    print(f"UPDATE users SET password_hash = '{hashed}' WHERE email = '{email}';")
