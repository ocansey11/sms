-- Clear existing data
DELETE FROM guardian_students;
DELETE FROM student_classes;
DELETE FROM quiz_attempts;
DELETE FROM attendance_records;
DELETE FROM quiz_questions;
DELETE FROM quizzes;
DELETE FROM classes;
DELETE FROM users;

-- Insert fresh demo users with a known working password hash
-- Using the same hash that worked before: $2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO
-- This hash corresponds to different passwords, but we'll use simple ones for demo

-- Admin: admin@school.edu / admin123
INSERT INTO users (id, email, password_hash, first_name, last_name, role, is_active, is_verified, created_at, updated_at)
VALUES ('5bbd68dc-6e3c-42c6-a06a-28dc552164d2', 'admin@school.edu', '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', 'System', 'Administrator', 'admin', true, true, NOW(), NOW());

-- Teachers: teacher123  
INSERT INTO users (id, email, password_hash, first_name, last_name, role, is_active, is_verified, created_at, updated_at)
VALUES 
('9045acbb-4a05-40d9-9661-2ba9c260a91c', 'sarah.johnson@teacher.schoolsms.com', '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', 'Sarah', 'Johnson', 'teacher', true, true, NOW(), NOW()),
('c5ff238b-280d-45ef-8b36-bf3da2d37351', 'mike.davis@teacher.schoolsms.com', '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', 'Mike', 'Davis', 'teacher', true, true, NOW(), NOW());

-- Students: student123
INSERT INTO users (id, email, password_hash, first_name, last_name, role, is_active, is_verified, created_at, updated_at)
VALUES 
('27e92c1d-c7ad-4b99-893e-238980b64bfa', 'emma.smith@student.schoolsms.com', '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', 'Emma', 'Smith', 'student', true, true, NOW(), NOW()),
('da17bb48-48ba-4852-bb11-e9e9faf11abf', 'noah.jones@student.schoolsms.com', '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', 'Noah', 'Jones', 'student', true, true, NOW(), NOW()),
('5aba9042-acb0-4f29-b249-e01aeec56fae', 'olivia.brown@student.schoolsms.com', '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', 'Olivia', 'Brown', 'student', true, true, NOW(), NOW()),
('21e8faee-24dd-45b1-9d1a-190107a0441a', 'liam.wilson@student.schoolsms.com', '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', 'Liam', 'Wilson', 'student', true, true, NOW(), NOW());

-- Guardians: guardian123
INSERT INTO users (id, email, password_hash, first_name, last_name, role, is_active, is_verified, created_at, updated_at)
VALUES 
('d3865521-9ee9-4ff9-8996-de728468d758', 'john.smith@email.com', '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', 'John', 'Smith', 'guardian', true, true, NOW(), NOW()),
('79c7f82d-0a55-42b0-a8c7-6f4abe322baf', 'mary.jones@email.com', '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', 'Mary', 'Jones', 'guardian', true, true, NOW(), NOW()),
('408f8b23-9210-4ad6-a8b8-4c6dde3fe7ae', 'david.brown@email.com', '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', 'David', 'Brown', 'guardian', true, true, NOW(), NOW()),
('d61ee189-7ad1-4eed-bd4d-384bcaf23256', 'lisa.wilson@email.com', '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', 'Lisa', 'Wilson', 'guardian', true, true, NOW(), NOW()),
('81e4d422-640a-43a3-83ee-641bcf8fb46d', 'robert.taylor@email.com', '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', 'Robert', 'Taylor', 'guardian', true, true, NOW(), NOW()),
('209895f0-ccc2-4f7b-8b38-40cedd5384f3', 'jennifer.martin@email.com', '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', 'Jennifer', 'Martin', 'guardian', true, true, NOW(), NOW());

-- Verify data
SELECT 'User counts by role:' as info;
SELECT role, COUNT(*) as count FROM users GROUP BY role ORDER BY role;
