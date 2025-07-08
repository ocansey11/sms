'use client';

import { useState, ChangeEvent, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { QuestionForm, QuizQuestion } from './QuestionForm';
import { Plus, Save, Eye, ArrowLeft } from 'lucide-react';
import apiClient from '@/lib/api';

interface QuizFormData {
  title: string;
  description: string;
  time_limit_minutes: number;
  max_attempts: number;
  passing_score: number;
  class_id: string;
}

interface QuizCreateFormProps {
  classes?: Array<{ id: string; name: string }>;
}

export function QuizCreateForm({ classes = [] }: QuizCreateFormProps) {
  const router = useRouter();
  const [quizData, setQuizData] = useState<QuizFormData>({
    title: '',
    description: '',
    time_limit_minutes: 30,
    max_attempts: 3,
    passing_score: 70,
    class_id: ''
  });

  const [questions, setQuestions] = useState<QuizQuestion[]>([
    {
      question_text: '',
      question_type: 'multiple_choice',
      options: ['', '', '', ''],
      correct_answer: '',
      explanation: '',
      points: 1,
      order_number: 1
    }
  ]);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const updateQuizData = (field: keyof QuizFormData, value: string | number) => {
    setQuizData(prev => ({ ...prev, [field]: value }));
    // Clear field error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const addQuestion = () => {
    const newQuestion: QuizQuestion = {
      question_text: '',
      question_type: 'multiple_choice',
      options: ['', '', '', ''],
      correct_answer: '',
      explanation: '',
      points: 1,
      order_number: questions.length + 1
    };
    setQuestions([...questions, newQuestion]);
  };

  const updateQuestion = (index: number, updatedQuestion: QuizQuestion) => {
    const newQuestions = [...questions];
    newQuestions[index] = { ...updatedQuestion, order_number: index + 1 };
    setQuestions(newQuestions);
  };

  const deleteQuestion = (index: number) => {
    if (questions.length > 1) {
      const newQuestions = questions.filter((_, i) => i !== index);
      // Reorder questions
      const reorderedQuestions = newQuestions.map((q, i) => ({ ...q, order_number: i + 1 }));
      setQuestions(reorderedQuestions);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Validate quiz data
    if (!quizData.title.trim()) {
      newErrors.title = 'Quiz title is required';
    }
    if (!quizData.class_id) {
      newErrors.class_id = 'Please select a class';
    }
    if (quizData.time_limit_minutes < 1 || quizData.time_limit_minutes > 300) {
      newErrors.time_limit_minutes = 'Time limit must be between 1 and 300 minutes';
    }
    if (quizData.max_attempts < 1 || quizData.max_attempts > 10) {
      newErrors.max_attempts = 'Max attempts must be between 1 and 10';
    }
    if (quizData.passing_score < 0 || quizData.passing_score > 100) {
      newErrors.passing_score = 'Passing score must be between 0 and 100';
    }

    // Validate questions
    questions.forEach((question, index) => {
      if (!question.question_text.trim()) {
        newErrors[`question_${index}_text`] = `Question ${index + 1} text is required`;
      }
      if (!question.correct_answer.trim()) {
        newErrors[`question_${index}_answer`] = `Question ${index + 1} must have a correct answer`;
      }
      if (question.question_type === 'multiple_choice') {
        const validOptions = (question.options || []).filter(opt => opt.trim());
        if (validOptions.length < 2) {
          newErrors[`question_${index}_options`] = `Question ${index + 1} needs at least 2 options`;
        }
        if (!validOptions.includes(question.correct_answer)) {
          newErrors[`question_${index}_correct`] = `Question ${index + 1} correct answer must be one of the options`;
        }
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent, asDraft = false) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      // First create the quiz
      const quizResponse = await apiClient.post('/teacher/quizzes', {
        ...quizData,
        is_published: !asDraft
      });

      const quiz = quizResponse.data;

      // Then add questions
      for (const question of questions) {
        await apiClient.post(`/teacher/quizzes/${quiz.id}/questions`, {
          ...question,
          quiz_id: quiz.id
        });
      }

      // Redirect to quiz list
      router.push('/teacher/quizzes');
    } catch (error) {
      console.error('Error creating quiz:', error);
      setErrors({ submit: 'Failed to create quiz. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => router.back()}
          className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Quizzes
        </button>
        <h1 className="text-2xl font-bold text-gray-900">Create New Quiz</h1>
        <p className="text-gray-600 mt-1">Build your quiz by filling out the details and adding questions.</p>
      </div>

      <form onSubmit={(e) => handleSubmit(e, false)} className="space-y-6">
        {/* Quiz Details */}
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quiz Details</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Title */}
            <div className="md:col-span-2">
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                Quiz Title *
              </label>
              <input
                id="title"
                type="text"
                value={quizData.title}
                onChange={(e: ChangeEvent<HTMLInputElement>) => updateQuizData('title', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter quiz title"
                required
              />
              {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title}</p>}
            </div>

            {/* Class */}
            <div>
              <label htmlFor="class_id" className="block text-sm font-medium text-gray-700 mb-1">
                Class *
              </label>
              <select
                id="class_id"
                value={quizData.class_id}
                onChange={(e: ChangeEvent<HTMLSelectElement>) => updateQuizData('class_id', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              >
                <option value="">Select a class</option>
                {classes.map((cls) => (
                  <option key={cls.id} value={cls.id}>
                    {cls.name}
                  </option>
                ))}
              </select>
              {errors.class_id && <p className="text-red-500 text-sm mt-1">{errors.class_id}</p>}
            </div>

            {/* Time Limit */}
            <div>
              <label htmlFor="time_limit" className="block text-sm font-medium text-gray-700 mb-1">
                Time Limit (minutes) *
              </label>
              <input
                id="time_limit"
                type="number"
                min="1"
                max="300"
                value={quizData.time_limit_minutes}
                onChange={(e: ChangeEvent<HTMLInputElement>) => updateQuizData('time_limit_minutes', parseInt(e.target.value) || 30)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
              {errors.time_limit_minutes && <p className="text-red-500 text-sm mt-1">{errors.time_limit_minutes}</p>}
            </div>

            {/* Max Attempts */}
            <div>
              <label htmlFor="max_attempts" className="block text-sm font-medium text-gray-700 mb-1">
                Max Attempts *
              </label>
              <input
                id="max_attempts"
                type="number"
                min="1"
                max="10"
                value={quizData.max_attempts}
                onChange={(e: ChangeEvent<HTMLInputElement>) => updateQuizData('max_attempts', parseInt(e.target.value) || 3)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
              {errors.max_attempts && <p className="text-red-500 text-sm mt-1">{errors.max_attempts}</p>}
            </div>

            {/* Passing Score */}
            <div>
              <label htmlFor="passing_score" className="block text-sm font-medium text-gray-700 mb-1">
                Passing Score (%) *
              </label>
              <input
                id="passing_score"
                type="number"
                min="0"
                max="100"
                value={quizData.passing_score}
                onChange={(e: ChangeEvent<HTMLInputElement>) => updateQuizData('passing_score', parseFloat(e.target.value) || 70)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
              {errors.passing_score && <p className="text-red-500 text-sm mt-1">{errors.passing_score}</p>}
            </div>

            {/* Description */}
            <div className="md:col-span-2">
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                Description (Optional)
              </label>
              <textarea
                id="description"
                value={quizData.description}
                onChange={(e: ChangeEvent<HTMLTextAreaElement>) => updateQuizData('description', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                rows={3}
                placeholder="Describe what this quiz covers..."
              />
            </div>
          </div>
        </div>

        {/* Questions Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Questions ({questions.length})</h2>
            <button
              type="button"
              onClick={addQuestion}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Question
            </button>
          </div>

          {questions.map((question, index) => (
            <QuestionForm
              key={index}
              question={question}
              questionNumber={index + 1}
              onUpdate={(updatedQuestion) => updateQuestion(index, updatedQuestion)}
              onDelete={() => deleteQuestion(index)}
            />
          ))}
        </div>

        {/* Errors */}
        {Object.keys(errors).length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <h3 className="text-sm font-medium text-red-800 mb-2">Please fix the following errors:</h3>
            <ul className="text-sm text-red-700 space-y-1">
              {Object.entries(errors).map(([key, error]) => (
                <li key={key}>• {error}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Submit Buttons */}
        <div className="flex justify-end space-x-3 pt-6 border-t">
          <button
            type="button"
            onClick={(e) => handleSubmit(e as any, true)}
            disabled={isSubmitting}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            <Save className="h-4 w-4 mr-2 inline" />
            Save as Draft
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            <Eye className="h-4 w-4 mr-2 inline" />
            {isSubmitting ? 'Creating...' : 'Create & Publish Quiz'}
          </button>
        </div>
      </form>
    </div>
  );
}
