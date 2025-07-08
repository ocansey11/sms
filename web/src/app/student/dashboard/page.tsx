'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import DashboardLayout from '@/components/DashboardLayout';
import { 
  BookOpen, 
  Clock, 
  CheckCircle, 
  TrendingUp,
  Play,
  Award,
  Calendar,
  Target
} from 'lucide-react';

interface StudentStats {
  total_classes: number;
  completed_quizzes: number;
  pending_quizzes: number;
  average_score: number;
}

interface AvailableQuiz {
  id: string;
  title: string;
  class_name: string;
  time_limit_minutes: number;
  max_attempts: number;
  attempts_used: number;
  description: string;
  scheduled_start: string;
  scheduled_end: string;
}

interface RecentResult {
  id: string;
  quiz_title: string;
  class_name: string;
  score: number;
  max_score: number;
  percentage: number;
  completed_at: string;
  status: string;
}

export default function StudentDashboard() {
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && (!user || user.role !== 'student')) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  const { data: stats, isLoading: statsLoading } = useQuery<StudentStats>({
    queryKey: ['student-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/student/stats');
      return response.data;
    },
    enabled: !!user && user.role === 'student',
  });

  const { data: availableQuizzes, isLoading: quizzesLoading } = useQuery<AvailableQuiz[]>({
    queryKey: ['student-available-quizzes'],
    queryFn: async () => {
      const response = await apiClient.get('/student/quizzes/available');
      return response.data;
    },
    enabled: !!user && user.role === 'student',
  });

  const { data: recentResults, isLoading: resultsLoading } = useQuery<RecentResult[]>({
    queryKey: ['student-recent-results'],
    queryFn: async () => {
      const response = await apiClient.get('/student/quiz-results/recent');
      return response.data;
    },
    enabled: !!user && user.role === 'student',
  });

  if (authLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Enrolled Classes',
      value: stats?.total_classes || 0,
      icon: BookOpen,
      color: 'bg-blue-500',
      loading: statsLoading,
    },
    {
      title: 'Completed Quizzes',
      value: stats?.completed_quizzes || 0,
      icon: CheckCircle,
      color: 'bg-green-500',
      loading: statsLoading,
    },
    {
      title: 'Pending Quizzes',
      value: stats?.pending_quizzes || 0,
      icon: Clock,
      color: 'bg-orange-500',
      loading: statsLoading,
    },
    {
      title: 'Average Score',
      value: stats?.average_score ? `${stats.average_score.toFixed(1)}%` : '0%',
      icon: Award,
      color: 'bg-purple-500',
      loading: statsLoading,
    },
  ];

  const getQuizStatus = (quiz: AvailableQuiz) => {
    const now = new Date();
    const start = new Date(quiz.scheduled_start);
    const end = quiz.scheduled_end ? new Date(quiz.scheduled_end) : null;

    if (quiz.attempts_used >= quiz.max_attempts) {
      return { status: 'completed', color: 'text-green-600', text: 'Completed' };
    }
    
    if (now < start) {
      return { status: 'upcoming', color: 'text-blue-600', text: 'Upcoming' };
    }
    
    if (end && now > end) {
      return { status: 'expired', color: 'text-red-600', text: 'Expired' };
    }
    
    return { status: 'available', color: 'text-green-600', text: 'Available' };
  };

  const getScoreColor = (percentage: number) => {
    if (percentage >= 90) return 'text-green-600';
    if (percentage >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <DashboardLayout title="Student Dashboard">
      <div className="space-y-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((card) => (
            <div key={card.title} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className={`p-3 rounded-full ${card.color} text-white`}>
                  <card.icon className="h-6 w-6" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">{card.title}</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {card.loading ? (
                      <div className="animate-pulse h-6 w-8 bg-gray-200 rounded"></div>
                    ) : (
                      card.value
                    )}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => router.push('/student/quizzes')}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <Play className="h-4 w-4 mr-2" />
              Take Quiz
            </button>
            <button
              onClick={() => router.push('/student/progress')}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <TrendingUp className="h-4 w-4 mr-2" />
              View Progress
            </button>
            <button
              onClick={() => router.push('/student/results')}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <Target className="h-4 w-4 mr-2" />
              View Results
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Available Quizzes */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Available Quizzes</h3>
              {quizzesLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/3"></div>
                    </div>
                  ))}
                </div>
              ) : availableQuizzes && availableQuizzes.length > 0 ? (
                <div className="space-y-4">
                  {availableQuizzes.map((quiz) => {
                    const status = getQuizStatus(quiz);
                    return (
                      <div
                        key={quiz.id}
                        className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900">{quiz.title}</h4>
                          <span className={`text-sm font-medium ${status.color}`}>
                            {status.text}
                          </span>
                        </div>
                        <p className="text-sm text-gray-500 mb-2">{quiz.class_name}</p>
                        <div className="flex items-center justify-between text-sm text-gray-500">
                          <div className="flex items-center space-x-4">
                            <div className="flex items-center">
                              <Clock className="h-4 w-4 mr-1" />
                              {quiz.time_limit_minutes} min
                            </div>
                            <div className="flex items-center">
                              <Target className="h-4 w-4 mr-1" />
                              {quiz.attempts_used}/{quiz.max_attempts} attempts
                            </div>
                          </div>
                          {status.status === 'available' && (
                            <button
                              onClick={() => router.push(`/student/quizzes/${quiz.id}`)}
                              className="inline-flex items-center text-blue-600 hover:text-blue-800"
                            >
                              <Play className="h-4 w-4 mr-1" />
                              Start
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-gray-500">No quizzes available at the moment.</p>
              )}
            </div>
          </div>

          {/* Recent Results */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Results</h3>
              {resultsLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/3"></div>
                    </div>
                  ))}
                </div>
              ) : recentResults && recentResults.length > 0 ? (
                <div className="space-y-4">
                  {recentResults.map((result) => (
                    <div
                      key={result.id}
                      className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                      onClick={() => router.push(`/student/results/${result.id}`)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900">{result.quiz_title}</h4>
                        <span className={`text-lg font-bold ${getScoreColor(result.percentage)}`}>
                          {result.percentage.toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-sm text-gray-500 mb-2">{result.class_name}</p>
                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          {new Date(result.completed_at).toLocaleDateString()}
                        </div>
                        <div>
                          {result.score}/{result.max_score} points
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No quiz results yet. Take your first quiz to see results!</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
