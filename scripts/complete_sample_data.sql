-- Fix the missing guardian relationships and add basic quizzes

-- Add guardian-student relationships
INSERT INTO guardian_students (
    id, guardian_id, student_id, relationship_type, is_primary, created_at
) VALUES 
(
    md5('guardian-student-1')::uuid,
    md5('guardian-smith')::uuid,
    md5('student-emma')::uuid,
    'parent',
    true,
    NOW()
),
(
    md5('guardian-student-2')::uuid,
    md5('guardian-smith')::uuid,
    md5('student-sophia')::uuid,
    'parent',
    true,
    NOW()
),
(
    md5('guardian-student-3')::uuid,
    md5('guardian-jones')::uuid,
    md5('student-noah')::uuid,
    'parent',
    true,
    NOW()
),
(
    md5('guardian-student-4')::uuid,
    md5('guardian-jones')::uuid,
    md5('student-jackson')::uuid,
    'parent',
    true,
    NOW()
),
(
    md5('guardian-student-5')::uuid,
    md5('guardian-brown')::uuid,
    md5('student-olivia')::uuid,
    'parent',
    true,
    NOW()
),
(
    md5('guardian-student-6')::uuid,
    md5('guardian-wilson')::uuid,
    md5('student-liam')::uuid,
    'parent',
    true,
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Add basic quizzes (simplified)
INSERT INTO quizzes (
    id, title, description, class_id, created_by, 
    time_limit_minutes, max_attempts, passing_score, is_published, 
    status, created_at, updated_at
) VALUES 
(
    md5('quiz-english-reading')::uuid,
    'Reading Comprehension Quiz',
    'Test your understanding of reading passages and vocabulary',
    md5('class-grade5-english')::uuid,
    md5('teacher-main')::uuid,
    30,
    3,
    70.00,
    true,
    'published',
    NOW(),
    NOW()
),
(
    md5('quiz-science-human-body')::uuid,
    'Human Body Systems Quiz',
    'Test your knowledge about the different systems of the human body',
    md5('class-grade5-science')::uuid,
    md5('teacher-main')::uuid,
    25,
    3,
    70.00,
    true,
    'published',
    NOW(),
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Add simplified quiz questions
INSERT INTO quiz_questions (
    id, quiz_id, question_text, question_type, options, correct_answer, 
    explanation, order_number, points, ai_generated, 
    created_at, updated_at
) VALUES 
-- English Quiz Questions (simplified)
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
    5,
    1,
    false,
    NOW(),
    NOW()
),

-- Science Quiz Questions (simplified)
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
    5,
    1,
    false,
    NOW(),
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Check what we have
SELECT 'Sample data setup complete!' as message;
SELECT COUNT(*) as total_users, role FROM users GROUP BY role;
SELECT COUNT(*) as total_classes FROM classes;
SELECT COUNT(*) as total_quizzes FROM quizzes;
SELECT COUNT(*) as total_questions FROM quiz_questions;
