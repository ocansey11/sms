'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import DashboardLayout from '@/components/DashboardLayout';
import { 
  Clock, 
  Play,
  BookOpen,
  Calendar,
  Target,
  CheckCircle,
  AlertCircle,
  Filter,
  Search
} from 'lucide-react';

interface Quiz {
  id: string;
  title: string;
  description: string;
  class_name: string;
  time_limit_minutes: number;
  max_attempts: number;
  attempts_used: number;
  passing_score: number;
  scheduled_start: string;
  scheduled_end: string;
  status: 'available' | 'upcoming' | 'expired' | 'completed';
  best_score?: number;
  last_attempt_date?: string;
}

export default function StudentQuizzesPage() {
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    if (!authLoading && (!user || user.role !== 'student')) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  const { data: quizzes, isLoading: quizzesLoading } = useQuery<Quiz[]>({
    queryKey: ['student-quizzes'],
    queryFn: async () => {
      const response = await apiClient.get('/student/quizzes');
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

  const getQuizStatus = (quiz: Quiz) => {
    const now = new Date();
    const start = new Date(quiz.scheduled_start);
    const end = quiz.scheduled_end ? new Date(quiz.scheduled_end) : null;

    if (quiz.attempts_used >= quiz.max_attempts) {
      return { status: 'completed', color: 'bg-green-100 text-green-800', text: 'Completed' };
    }
    
    if (now < start) {
      return { status: 'upcoming', color: 'bg-blue-100 text-blue-800', text: 'Upcoming' };
    }
    
    if (end && now > end) {
      return { status: 'expired', color: 'bg-red-100 text-red-800', text: 'Expired' };
    }
    
    return { status: 'available', color: 'bg-green-100 text-green-800', text: 'Available' };
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available':
        return <Play className="h-4 w-4 text-green-600" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'upcoming':
        return <Clock className="h-4 w-4 text-blue-600" />;
      case 'expired':
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const filteredQuizzes = quizzes?.filter(quiz => {
    const matchesSearch = quiz.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         quiz.class_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || getQuizStatus(quiz).status === statusFilter;
    return matchesSearch && matchesStatus;
  }) || [];

  const statusOptions = [
    { value: 'all', label: 'All Quizzes' },
    { value: 'available', label: 'Available' },
    { value: 'upcoming', label: 'Upcoming' },
    { value: 'completed', label: 'Completed' },
    { value: 'expired', label: 'Expired' },
  ];

  return (
    <DashboardLayout title="My Quizzes">
      <div className="space-y-6">
        {/* Search and Filter */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search quizzes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="pl-10 pr-8 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
              >
                {statusOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Quiz List */}
        <div className="space-y-4">
          {quizzesLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
                  <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                </div>
              ))}
            </div>
          ) : filteredQuizzes.length > 0 ? (
            filteredQuizzes.map((quiz) => {
              const status = getQuizStatus(quiz);
              return (
                <div key={quiz.id} className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-xl font-semibold text-gray-900">{quiz.title}</h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.color}`}>
                          {status.text}
                        </span>
                      </div>
                      <div className="flex items-center text-sm text-gray-600 mb-2">
                        <BookOpen className="h-4 w-4 mr-1" />
                        <span>{quiz.class_name}</span>
                      </div>
                      {quiz.description && (
                        <p className="text-gray-600 mb-4">{quiz.description}</p>
                      )}
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(status.status)}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 mr-2 text-gray-400" />
                      <span>{quiz.time_limit_minutes} minutes</span>
                    </div>
                    <div className="flex items-center">
                      <Target className="h-4 w-4 mr-2 text-gray-400" />
                      <span>{quiz.attempts_used}/{quiz.max_attempts} attempts</span>
                    </div>
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                      <span>Due: {new Date(quiz.scheduled_end || quiz.scheduled_start).toLocaleDateString()}</span>
                    </div>
                    {quiz.best_score && (
                      <div className="flex items-center">
                        <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                        <span>Best: {quiz.best_score}%</span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-500">
                      {quiz.last_attempt_date && (
                        <span>Last attempt: {new Date(quiz.last_attempt_date).toLocaleDateString()}</span>
                      )}
                      {quiz.passing_score && (
                        <span className="ml-4">Passing score: {quiz.passing_score}%</span>
                      )}
                    </div>
                    <div className="flex space-x-2">
                      {status.status === 'available' && (
                        <button
                          onClick={() => router.push(`/student/quizzes/${quiz.id}`)}
                          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                        >
                          <Play className="h-4 w-4 mr-2" />
                          Start Quiz
                        </button>
                      )}
                      {status.status === 'completed' && (
                        <button
                          onClick={() => router.push(`/student/results?quiz=${quiz.id}`)}
                          className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                        >
                          View Results
                        </button>
                      )}
                      {status.status === 'upcoming' && (
                        <div className="text-sm text-gray-500">
                          Starts: {new Date(quiz.scheduled_start).toLocaleString()}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No quizzes found</h3>
              <p className="text-gray-600">
                {searchTerm || statusFilter !== 'all' 
                  ? 'Try adjusting your search or filter criteria.'
                  : 'No quizzes are available at the moment. Check back later!'}
              </p>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
