'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import DashboardLayout from '@/components/DashboardLayout';
import { 
  Clock, 
  CheckCircle, 
  Circle, 
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Send,
  Timer,
  BookOpen
} from 'lucide-react';

interface QuizQuestion {
  id: string;
  question_text: string;
  question_type: 'multiple_choice' | 'true_false' | 'short_answer';
  options: string[];
  order_number: number;
  points: number;
}

interface QuizData {
  id: string;
  title: string;
  description: string;
  time_limit_minutes: number;
  questions: QuizQuestion[];
  class_name: string;
  total_points: number;
}

interface QuizAttempt {
  id: string;
  started_at: string;
  time_limit_minutes: number;
}

export default function TakeQuizPage({ params }: { params: { id: string } }) {
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<{ [key: string]: string }>({});
  const [timeLeft, setTimeLeft] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showConfirmSubmit, setShowConfirmSubmit] = useState(false);

  useEffect(() => {
    if (!authLoading && (!user || user.role !== 'student')) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  const { data: quiz, isLoading: quizLoading } = useQuery<QuizData>({
    queryKey: ['quiz', params.id],
    queryFn: async () => {
      const response = await apiClient.get(`/student/quizzes/${params.id}`);
      return response.data;
    },
    enabled: !!user && user.role === 'student',
  });

  const { data: attempt, isLoading: attemptLoading } = useQuery<QuizAttempt>({
    queryKey: ['quiz-attempt', params.id],
    queryFn: async () => {
      const response = await apiClient.post(`/student/quizzes/${params.id}/start`);
      return response.data;
    },
    enabled: !!quiz && !!user && user.role === 'student',
  });

  const submitQuizMutation = useMutation({
    mutationFn: async (submissionData: { answers: { [key: string]: string } }) => {
      const response = await apiClient.post(`/student/quiz-attempts/${attempt?.id}/submit`, submissionData);
      return response.data;
    },
    onSuccess: (data) => {
      router.push(`/student/results/${data.id}`);
    },
    onError: (error) => {
      console.error('Quiz submission error:', error);
    },
  });

  // Timer effect
  useEffect(() => {
    if (attempt && quiz) {
      const startTime = new Date(attempt.started_at).getTime();
      const timeLimit = attempt.time_limit_minutes * 60 * 1000;
      const endTime = startTime + timeLimit;

      const timer = setInterval(() => {
        const now = new Date().getTime();
        const remaining = Math.max(0, Math.floor((endTime - now) / 1000));
        setTimeLeft(remaining);

        if (remaining <= 0) {
          clearInterval(timer);
          handleSubmitQuiz();
        }
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [attempt, quiz]);

  const handleAnswerChange = (questionId: string, answer: string) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleSubmitQuiz = async () => {
    if (!attempt) return;
    
    setIsSubmitting(true);
    try {
      await submitQuizMutation.mutateAsync({ answers });
    } catch (error) {
      setIsSubmitting(false);
      setShowConfirmSubmit(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getAnsweredCount = () => {
    return quiz ? Object.keys(answers).length : 0;
  };

  const isQuestionAnswered = (questionId: string) => {
    return answers.hasOwnProperty(questionId) && answers[questionId] !== '';
  };

  if (authLoading || quizLoading || attemptLoading || !quiz || !attempt) {
    return (
      <DashboardLayout title="Loading Quiz...">
        <div className="flex items-center justify-center min-h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  const currentQuestionData = quiz.questions[currentQuestion];
  const isLastQuestion = currentQuestion === quiz.questions.length - 1;
  const isFirstQuestion = currentQuestion === 0;

  return (
    <DashboardLayout title={quiz.title}>
      <div className="max-w-4xl mx-auto">
        {/* Quiz Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{quiz.title}</h1>
              <p className="text-gray-600">{quiz.class_name}</p>
            </div>
            <div className="flex items-center space-x-4">
              {timeLeft !== null && (
                <div className={`flex items-center px-3 py-1 rounded-full ${
                  timeLeft < 300 ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'
                }`}>
                  <Timer className="h-4 w-4 mr-1" />
                  <span className="font-medium">{formatTime(timeLeft)}</span>
                </div>
              )}
              <div className="text-sm text-gray-500">
                {getAnsweredCount()}/{quiz.questions.length} answered
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentQuestion + 1) / quiz.questions.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Question Navigation */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Questions</h3>
            <div className="text-sm text-gray-500">
              Question {currentQuestion + 1} of {quiz.questions.length}
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {quiz.questions.map((question, index) => (
              <button
                key={question.id}
                onClick={() => setCurrentQuestion(index)}
                className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
                  index === currentQuestion
                    ? 'bg-blue-600 text-white'
                    : isQuestionAnswered(question.id)
                    ? 'bg-green-100 text-green-600'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>
        </div>

        {/* Current Question */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-500">
                Question {currentQuestion + 1}
              </span>
              <span className="text-sm text-gray-500">
                {currentQuestionData.points} points
              </span>
            </div>
            <h2 className="text-xl font-medium text-gray-900 mb-4">
              {currentQuestionData.question_text}
            </h2>
          </div>

          {/* Answer Options */}
          <div className="space-y-3">
            {currentQuestionData.question_type === 'multiple_choice' && (
              <div className="space-y-2">
                {currentQuestionData.options.map((option, index) => (
                  <label
                    key={index}
                    className="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50"
                  >
                    <input
                      type="radio"
                      name={`question-${currentQuestionData.id}`}
                      value={option}
                      checked={answers[currentQuestionData.id] === option}
                      onChange={(e) => handleAnswerChange(currentQuestionData.id, e.target.value)}
                      className="mr-3"
                    />
                    <span className="text-gray-900">{option}</span>
                  </label>
                ))}
              </div>
            )}

            {currentQuestionData.question_type === 'true_false' && (
              <div className="space-y-2">
                {['True', 'False'].map((option) => (
                  <label
                    key={option}
                    className="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50"
                  >
                    <input
                      type="radio"
                      name={`question-${currentQuestionData.id}`}
                      value={option}
                      checked={answers[currentQuestionData.id] === option}
                      onChange={(e) => handleAnswerChange(currentQuestionData.id, e.target.value)}
                      className="mr-3"
                    />
                    <span className="text-gray-900">{option}</span>
                  </label>
                ))}
              </div>
            )}

            {currentQuestionData.question_type === 'short_answer' && (
              <textarea
                value={answers[currentQuestionData.id] || ''}
                onChange={(e) => handleAnswerChange(currentQuestionData.id, e.target.value)}
                placeholder="Enter your answer here..."
                className="w-full p-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={4}
              />
            )}
          </div>
        </div>

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
            disabled={isFirstQuestion}
            className="flex items-center px-4 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="h-4 w-4 mr-2" />
            Previous
          </button>

          <div className="flex space-x-3">
            {!isLastQuestion ? (
              <button
                onClick={() => setCurrentQuestion(Math.min(quiz.questions.length - 1, currentQuestion + 1))}
                className="flex items-center px-4 py-2 border border-transparent text-white bg-blue-600 hover:bg-blue-700 rounded-md"
              >
                Next
                <ChevronRight className="h-4 w-4 ml-2" />
              </button>
            ) : (
              <button
                onClick={() => setShowConfirmSubmit(true)}
                className="flex items-center px-4 py-2 border border-transparent text-white bg-green-600 hover:bg-green-700 rounded-md"
              >
                <Send className="h-4 w-4 mr-2" />
                Submit Quiz
              </button>
            )}
          </div>
        </div>

        {/* Confirmation Modal */}
        {showConfirmSubmit && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Submit Quiz?
              </h3>
              <p className="text-gray-600 mb-6">
                Are you sure you want to submit your quiz? You have answered {getAnsweredCount()} out of {quiz.questions.length} questions.
                {getAnsweredCount() < quiz.questions.length && (
                  <span className="text-orange-600 font-medium">
                    {' '}You haven't answered all questions yet.
                  </span>
                )}
              </p>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowConfirmSubmit(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmitQuiz}
                  disabled={isSubmitting}
                  className="px-4 py-2 border border-transparent text-white bg-green-600 hover:bg-green-700 rounded-md disabled:opacity-50"
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Quiz'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
