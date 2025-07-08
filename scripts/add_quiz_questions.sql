-- Add quiz questions with correct schema
INSERT INTO quiz_questions (
    id, quiz_id, question_text, question_type, options, correct_answer, 
    explanation, order_number, points, created_at, updated_at
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
    NOW(),
    NOW()
),

-- Science Quiz Questions
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
    NOW(),
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Final summary
SELECT 'Quiz questions added successfully!' as message;
SELECT COUNT(*) as total_questions FROM quiz_questions;
SELECT q.title, COUNT(qq.id) as question_count
FROM quizzes q 
LEFT JOIN quiz_questions qq ON q.id = qq.quiz_id 
GROUP BY q.id, q.title;
