-- Fix demo password hashes
UPDATE users SET password_hash = '$2b$12$Nx7502/KxJGzs39lRXZBKemdu3t68Y7yUZycUkdLvJEV93Fyzvi9W' WHERE email = 'admin@school.edu';
UPDATE users SET password_hash = '$2b$12$1yBTa42EFJh1Jz5XQH4wSeJZpYTDR3CWF0xeL8QjSVZBCNxCqb8me' WHERE email = 'teacher@schoolsms.com';
UPDATE users SET password_hash = '$2b$12$.tbpjuiUB8rOH.71LE9UN.3v0xpPMw60vXmhoIZ0QMrSEgP/Nj7rW' WHERE email = 'emma.smith@student.schoolsms.com';
UPDATE users SET password_hash = '$2b$12$dVtRZjW.EK1FHtiRltmhS.4vKk1TvJLz29R1hHHXu/1WX2cEzPsZq' WHERE email = 'john.smith@email.com';

-- Verify the updates
SELECT email, role, 'Password updated' as status FROM users WHERE email IN (
    'admin@school.edu',
    'teacher@schoolsms.com', 
    'emma.smith@student.schoolsms.com',
    'john.smith@email.com'
);
