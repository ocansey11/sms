'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import DashboardLayout from '@/components/DashboardLayout';
import { PermissionGuard } from '@/components/PermissionGuard';
import { 
  BookOpen, 
  Users, 
  FileText, 
  TrendingUp,
  PlusCircle,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

interface TeacherStats {
  total_classes: number;
  total_students: number;
  total_quizzes: number;
  pending_quizzes: number;
}

interface Class {
  id: string;
  name: string;
  subject: string;
  student_count: number;
  active_quizzes: number;
}

interface RecentQuiz {
  id: string;
  title: string;
  class_name: string;
  status: string;
  created_at: string;
  attempts_count: number;
}

export default function TeacherDashboard() {
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && (!user || user.role !== 'teacher')) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  const { data: stats, isLoading: statsLoading } = useQuery<TeacherStats>({
    queryKey: ['teacher-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/teacher/stats');
      return response.data;
    },
    enabled: !!user && user.role === 'teacher',
  });

  const { data: classes, isLoading: classesLoading } = useQuery<Class[]>({
    queryKey: ['teacher-classes'],
    queryFn: async () => {
      const response = await apiClient.get('/teacher/classes');
      return response.data;
    },
    enabled: !!user && user.role === 'teacher',
  });

  const { data: recentQuizzes, isLoading: quizzesLoading } = useQuery<RecentQuiz[]>({
    queryKey: ['teacher-recent-quizzes'],
    queryFn: async () => {
      const response = await apiClient.get('/teacher/quizzes/recent');
      return response.data;
    },
    enabled: !!user && user.role === 'teacher',
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
      title: 'Total Classes',
      value: stats?.total_classes || 0,
      icon: BookOpen,
      color: 'bg-blue-500',
      loading: statsLoading,
    },
    {
      title: 'Total Students',
      value: stats?.total_students || 0,
      icon: Users,
      color: 'bg-green-500',
      loading: statsLoading,
    },
    {
      title: 'Total Quizzes',
      value: stats?.total_quizzes || 0,
      icon: FileText,
      color: 'bg-purple-500',
      loading: statsLoading,
    },
    {
      title: 'Pending Quizzes',
      value: stats?.pending_quizzes || 0,
      icon: Clock,
      color: 'bg-orange-500',
      loading: statsLoading,
    },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'published':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'draft':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <DashboardLayout title="Teacher Dashboard">
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
            <PermissionGuard permission="create_class">
              <button
                onClick={() => router.push('/teacher/classes/new')}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <PlusCircle className="h-4 w-4 mr-2" />
                Create Class
              </button>
            </PermissionGuard>
            <PermissionGuard permission="create_quiz">
              <button
                onClick={() => router.push('/teacher/quizzes/new')}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
              >
                <PlusCircle className="h-4 w-4 mr-2" />
                Create Quiz
              </button>
            </PermissionGuard>
            <PermissionGuard permission="view_student_progress">
              <button
                onClick={() => router.push('/teacher/reports')}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                <TrendingUp className="h-4 w-4 mr-2" />
                View Reports
              </button>
            </PermissionGuard>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Classes */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Your Classes</h3>
              {classesLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/3"></div>
                    </div>
                  ))}
                </div>
              ) : classes && classes.length > 0 ? (
                <div className="space-y-4">
                  {classes.map((cls) => (
                    <div
                      key={cls.id}
                      className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                      onClick={() => router.push(`/teacher/classes/${cls.id}`)}
                    >
                      <div>
                        <h4 className="font-medium text-gray-900">{cls.name}</h4>
                        <p className="text-sm text-gray-500">{cls.subject}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">
                          {cls.student_count} students
                        </p>
                        <p className="text-sm text-gray-500">
                          {cls.active_quizzes} active quizzes
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No classes yet. Create your first class to get started!</p>
              )}
            </div>
          </div>

          {/* Recent Quizzes */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Recent Quizzes</h3>
                <button
                  onClick={() => router.push('/teacher/quizzes')}
                  className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                >
                  View All
                </button>
              </div>
              {quizzesLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/3"></div>
                    </div>
                  ))}
                </div>
              ) : recentQuizzes && recentQuizzes.length > 0 ? (
                <div className="space-y-4">
                  {recentQuizzes.map((quiz) => (
                    <div
                      key={quiz.id}
                      className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                      onClick={() => router.push(`/teacher/quizzes/${quiz.id}`)}
                    >
                      <div>
                        <div className="flex items-center">
                          <h4 className="font-medium text-gray-900">{quiz.title}</h4>
                          <span className="ml-2">{getStatusIcon(quiz.status)}</span>
                        </div>
                        <p className="text-sm text-gray-500">{quiz.class_name}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">
                          {quiz.attempts_count} attempts
                        </p>
                        <p className="text-sm text-gray-500 capitalize">
                          {quiz.status}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No quizzes yet. Create your first quiz to get started!</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
