-- Sample Teacher Scenario: Grade 5 English and Science Classes
-- This script creates a realistic scenario for testing the SMS system

-- Clear existing data (optional - uncomment if needed)
-- DELETE FROM quiz_questions;
-- DELETE FROM quiz_attempts;
-- DELETE FROM quizzes;
-- DELETE FROM student_classes;
-- DELETE FROM guardian_students;
-- DELETE FROM attendance_records;
-- DELETE FROM classes;
-- DELETE FROM users;

-- 1. Create Teacher Account
INSERT INTO users (
    id, email, password_hash, first_name, last_name, role, 
    is_active, is_verified, created_at, updated_at
) VALUES (
    md5('teacher-main')::uuid,
    'teacher@schoolsms.com',
    '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', -- password: teacher123
    'Sarah',
    'Johnson',
    'teacher',
    true,
    true,
    NOW(),
    NOW()
);

-- 2. Create Two Classes
INSERT INTO classes (
    id, name, subject, teacher_id, academic_year, description,
    is_active, created_at, updated_at
) VALUES 
(
    md5('class-grade5-english')::uuid,
    'Grade 5 English',
    'English',
    md5('teacher-main')::uuid,
    '2024-2025',
    'Grade 5 English Language Arts - Reading Comprehension and Writing',
    true,
    NOW(),
    NOW()
),
(
    md5('class-grade5-science')::uuid,
    'Grade 5 Science',
    'Science',
    md5('teacher-main')::uuid,
    '2024-2025',
    'Grade 5 Science - Human Body Systems and Life Science',
    true,
    NOW(),
    NOW()
);

-- 3. Create Guardian Accounts
INSERT INTO users (
    id, email, password_hash, first_name, last_name, role, 
    phone_number, is_active, is_verified, created_at, updated_at
) VALUES 
(
    md5('guardian-smith')::uuid,
    'john.smith@email.com',
    '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', -- password: guardian123
    'John',
    'Smith',
    'guardian',
    '+1234567890',
    true,
    true,
    NOW(),
    NOW()
),
(
    md5('guardian-jones')::uuid,
    'mary.jones@email.com',
    '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', -- password: guardian123
    'Mary',
    'Jones',
    'guardian',
    '+1234567891',
    true,
    true,
    NOW(),
    NOW()
),
(
    md5('guardian-brown')::uuid,
    'david.brown@email.com',
    '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', -- password: guardian123
    'David',
    'Brown',
    'guardian',
    '+1234567892',
    true,
    true,
    NOW(),
    NOW()
),
(
    md5('guardian-wilson')::uuid,
    'lisa.wilson@email.com',
    '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', -- password: guardian123
    'Lisa',
    'Wilson',
    'guardian',
    '+1234567893',
    true,
    true,
    NOW(),
    NOW()
);

-- 4. Create Student Accounts
INSERT INTO users (
    id, email, password_hash, first_name, last_name, role, 
    is_active, is_verified, created_at, updated_at
) VALUES 
(
    md5('student-emma')::uuid,
    'emma.smith@student.schoolsms.com',
    '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', -- password: student123
    'Emma',
    'Smith',
    'student',
    true,
    true,
    NOW(),
    NOW()
),
(
    md5('student-noah')::uuid,
    'noah.jones@student.schoolsms.com',
    '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', -- password: student123
    'Noah',
    'Jones',
    'student',
    true,
    true,
    NOW(),
    NOW()
),
(
    md5('student-olivia')::uuid,
    'olivia.brown@student.schoolsms.com',
    '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', -- password: student123
    'Olivia',
    'Brown',
    'student',
    true,
    true,
    NOW(),
    NOW()
),
(
    md5('student-liam')::uuid,
    'liam.wilson@student.schoolsms.com',
    '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', -- password: student123
    'Liam',
    'Wilson',
    'student',
    true,
    true,
    NOW(),
    NOW()
),
(
    md5('student-sophia')::uuid,
    'sophia.smith@student.schoolsms.com',
    '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', -- password: student123
    'Sophia',
    'Smith',
    'student',
    true,
    true,
    NOW(),
    NOW()
),
(
    md5('student-jackson')::uuid,
    'jackson.jones@student.schoolsms.com',
    '$2b$12$LQv3c1yqBwEHxE5qTRrNTOsGqHjTJZJPKnNlFxlOiIgUgzJKT7QoO', -- password: student123
    'Jackson',
    'Jones',
    'student',
    true,
    true,
    NOW(),
    NOW()
);

-- 5. Link Guardians to Students
INSERT INTO guardian_students (
    id, guardian_id, student_id, relationship, is_primary_contact, 
    created_at, updated_at
) VALUES 
(
    md5('guardian-student-1')::uuid,
    md5('guardian-smith')::uuid,
    md5('student-emma')::uuid,
    'parent',
    true,
    NOW(),
    NOW()
),
(
    md5('guardian-student-2')::uuid,
    md5('guardian-smith')::uuid,
    md5('student-sophia')::uuid,
    'parent',
    true,
    NOW(),
    NOW()
),
(
    md5('guardian-student-3')::uuid,
    md5('guardian-jones')::uuid,
    md5('student-noah')::uuid,
    'parent',
    true,
    NOW(),
    NOW()
),
(
    md5('guardian-student-4')::uuid,
    md5('guardian-jones')::uuid,
    md5('student-jackson')::uuid,
    'parent',
    true,
    NOW(),
    NOW()
),
(
    md5('guardian-student-5')::uuid,
    md5('guardian-brown')::uuid,
    md5('student-olivia')::uuid,
    'parent',
    true,
    NOW(),
    NOW()
),
(
    md5('guardian-student-6')::uuid,
    md5('guardian-wilson')::uuid,
    md5('student-liam')::uuid,
    'parent',
    true,
    NOW(),
    NOW()
);

-- 6. Enroll Students in Classes
INSERT INTO student_classes (
    id, student_id, class_id, enrolled_at, is_active
) VALUES 
-- English Class Students
(
    md5('enrollment-emma-english')::uuid,
    md5('student-emma')::uuid,
    md5('class-grade5-english')::uuid,
    NOW(),
    true
),
(
    md5('enrollment-noah-english')::uuid,
    md5('student-noah')::uuid,
    md5('class-grade5-english')::uuid,
    NOW(),
    true
),
(
    md5('enrollment-olivia-english')::uuid,
    md5('student-olivia')::uuid,
    md5('class-grade5-english')::uuid,
    NOW(),
    true
),
(
    md5('enrollment-liam-english')::uuid,
    md5('student-liam')::uuid,
    md5('class-grade5-english')::uuid,
    NOW(),
    true
),
-- Science Class Students
(
    md5('enrollment-emma-science')::uuid,
    md5('student-emma')::uuid,
    md5('class-grade5-science')::uuid,
    NOW(),
    true
),
(
    md5('enrollment-noah-science')::uuid,
    md5('student-noah')::uuid,
    md5('class-grade5-science')::uuid,
    NOW(),
    true
),
(
    md5('enrollment-sophia-science')::uuid,
    md5('student-sophia')::uuid,
    md5('class-grade5-science')::uuid,
    NOW(),
    true
),
(
    md5('enrollment-jackson-science')::uuid,
    md5('student-jackson')::uuid,
    md5('class-grade5-science')::uuid,
    NOW(),
    true
);

-- 7. Create Quizzes
INSERT INTO quizzes (
    id, title, description, class_id, created_by, 
    total_questions, time_limit, is_active, created_at, updated_at
) VALUES 
(
    md5('quiz-english-reading')::uuid,
    'Reading Comprehension Quiz',
    'Test your understanding of reading passages and vocabulary',
    md5('class-grade5-english')::uuid,
    md5('teacher-main')::uuid,
    10,
    30,
    true,
    NOW(),
    NOW()
),
(
    md5('quiz-science-human-body')::uuid,
    'Human Body Systems Quiz',
    'Test your knowledge about the different systems of the human body',
    md5('class-grade5-science')::uuid,
    md5('teacher-main')::uuid,
    10,
    25,
    true,
    NOW(),
    NOW()
);

-- 8. Create Quiz Questions - English (Reading Comprehension)
INSERT INTO quiz_questions (
    id, quiz_id, question_text, question_type, options, correct_answer, 
    explanation, difficulty_level, order_number, points, ai_generated, 
    created_at, updated_at
) VALUES 
-- English Quiz Questions
(
    md5('question-english-1')::uuid,
    md5('quiz-english-reading')::uuid,
    'What is the main idea of a story?',
    'multiple_choice',
    '["The first sentence", "The most important message", "The last paragraph", "The title"]',
    'The most important message',
    'The main idea is the central message or theme that the author wants to convey.',
    1,
    1,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-english-2')::uuid,
    md5('quiz-english-reading')::uuid,
    'Which word means the same as "happy"?',
    'multiple_choice',
    '["Sad", "Joyful", "Angry", "Tired"]',
    'Joyful',
    'Joyful is a synonym for happy, meaning feeling great pleasure or delight.',
    1,
    2,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-english-3')::uuid,
    md5('quiz-english-reading')::uuid,
    'What are characters in a story?',
    'multiple_choice',
    '["The setting", "The people or animals", "The problem", "The ending"]',
    'The people or animals',
    'Characters are the people, animals, or beings that take part in the story.',
    1,
    3,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-english-4')::uuid,
    md5('quiz-english-reading')::uuid,
    'What is a setting in a story?',
    'multiple_choice',
    '["The characters", "When and where the story happens", "The problem", "The solution"]',
    'When and where the story happens',
    'Setting refers to the time and place where the story takes place.',
    2,
    4,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-english-5')::uuid,
    md5('quiz-english-reading')::uuid,
    'Which is an example of a verb?',
    'multiple_choice',
    '["Dog", "Red", "Run", "Beautiful"]',
    'Run',
    'A verb is an action word. "Run" shows an action someone can do.',
    1,
    5,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-english-6')::uuid,
    md5('quiz-english-reading')::uuid,
    'What does "compare" mean?',
    'multiple_choice',
    '["To make different", "To find similarities", "To ignore", "To forget"]',
    'To find similarities',
    'To compare means to look at how things are alike or similar.',
    2,
    6,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-english-7')::uuid,
    md5('quiz-english-reading')::uuid,
    'What is a noun?',
    'multiple_choice',
    '["An action word", "A describing word", "A person, place, or thing", "A connecting word"]',
    'A person, place, or thing',
    'A noun is a word that names a person, place, thing, or idea.',
    1,
    7,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-english-8')::uuid,
    md5('quiz-english-reading')::uuid,
    'What does "contrast" mean?',
    'multiple_choice',
    '["To show differences", "To show similarities", "To ignore", "To repeat"]',
    'To show differences',
    'To contrast means to show how things are different from each other.',
    2,
    8,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-english-9')::uuid,
    md5('quiz-english-reading')::uuid,
    'What is the beginning of a story called?',
    'multiple_choice',
    '["Middle", "Introduction", "Conclusion", "Summary"]',
    'Introduction',
    'The introduction is the beginning part of a story that introduces characters and setting.',
    1,
    9,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-english-10')::uuid,
    md5('quiz-english-reading')::uuid,
    'Which sentence is complete?',
    'multiple_choice',
    '["The dog", "Running fast", "The cat sleeps", "In the park"]',
    'The cat sleeps',
    'A complete sentence has a subject and a predicate. "The cat sleeps" has both.',
    2,
    10,
    1,
    false,
    NOW(),
    NOW()
),

-- Science Quiz Questions (Human Body)
(
    md5('question-science-1')::uuid,
    md5('quiz-science-human-body')::uuid,
    'Which organ pumps blood throughout the body?',
    'multiple_choice',
    '["Lungs", "Brain", "Heart", "Liver"]',
    'Heart',
    'The heart is the muscular organ responsible for circulating blood throughout the body.',
    1,
    1,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-science-2')::uuid,
    md5('quiz-science-human-body')::uuid,
    'Which body system helps you breathe?',
    'multiple_choice',
    '["Circulatory system", "Respiratory system", "Digestive system", "Nervous system"]',
    'Respiratory system',
    'The respiratory system includes the lungs and helps us take in oxygen and release carbon dioxide.',
    1,
    2,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-science-3')::uuid,
    md5('quiz-science-human-body')::uuid,
    'What does the brain control?',
    'multiple_choice',
    '["Digestion only", "Blood flow only", "Thoughts and actions", "Breathing only"]',
    'Thoughts and actions',
    'The brain is the control center that manages thoughts, actions, and many body functions.',
    2,
    3,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-science-4')::uuid,
    md5('quiz-science-human-body')::uuid,
    'What are bones part of?',
    'multiple_choice',
    '["Muscular system", "Nervous system", "Skeletal system", "Respiratory system"]',
    'Skeletal system',
    'Bones make up the skeletal system, which supports and gives structure to the body.',
    1,
    4,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-science-5')::uuid,
    md5('quiz-science-human-body')::uuid,
    'Which organ helps digest food?',
    'multiple_choice',
    '["Heart", "Brain", "Lungs", "Stomach"]',
    'Stomach',
    'The stomach breaks down food with acids and enzymes as part of the digestive system.',
    2,
    5,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-science-6')::uuid,
    md5('quiz-science-human-body')::uuid,
    'Which part of the body helps you smell?',
    'multiple_choice',
    '["Eyes", "Nose", "Ears", "Skin"]',
    'Nose',
    'The nose contains olfactory receptors that detect different smells.',
    1,
    6,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-science-7')::uuid,
    md5('quiz-science-human-body')::uuid,
    'What is the main function of muscles?',
    'multiple_choice',
    '["To think", "To move the body", "To breathe", "To digest food"]',
    'To move the body',
    'Muscles contract and relax to enable movement of the body and internal organs.',
    2,
    7,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-science-8')::uuid,
    md5('quiz-science-human-body')::uuid,
    'Which organs remove waste from the body?',
    'multiple_choice',
    '["Liver", "Kidneys", "Stomach", "Heart"]',
    'Kidneys',
    'The kidneys filter waste and excess fluids from the blood to produce urine.',
    2,
    8,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-science-9')::uuid,
    md5('quiz-science-human-body')::uuid,
    'How many lungs do humans have?',
    'multiple_choice',
    '["One", "Two", "Three", "Four"]',
    'Two',
    'Humans have two lungs: the left lung and the right lung.',
    1,
    9,
    1,
    false,
    NOW(),
    NOW()
),
(
    md5('question-science-10')::uuid,
    md5('quiz-science-human-body')::uuid,
    'What protects the brain inside your head?',
    'multiple_choice',
    '["Muscles", "Skin", "Skull", "Hair"]',
    'Skull',
    'The skull is a hard bone structure that protects the brain from injury.',
    2,
    10,
    1,
    false,
    NOW(),
    NOW()
);

-- Summary Information
SELECT 'Sample data created successfully!' as message;
SELECT 'Teacher: teacher@schoolsms.com (password: teacher123)' as login_info;
SELECT 'Students: emma.smith@student.schoolsms.com, noah.jones@student.schoolsms.com, etc. (password: student123)' as student_info;
SELECT 'Guardians: john.smith@email.com, mary.jones@email.com, etc. (password: guardian123)' as guardian_info;
