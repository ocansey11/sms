'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import DashboardLayout from '@/components/DashboardLayout';
import { 
  Users, 
  TrendingUp, 
  BookOpen, 
  Clock,
  CheckCircle,
  AlertCircle,
  Calendar,
  Award,
  Target,
  MessageCircle
} from 'lucide-react';

interface GuardianStats {
  total_students: number;
  total_classes: number;
  completed_quizzes: number;
  pending_quizzes: number;
}

interface StudentProgress {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  total_classes: number;
  completed_quizzes: number;
  pending_quizzes: number;
  average_score: number;
  recent_activity: string;
}

interface RecentActivity {
  id: string;
  student_name: string;
  activity_type: string;
  description: string;
  timestamp: string;
  score?: number;
  quiz_title?: string;
}

export default function GuardianDashboard() {
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && (!user || user.role !== 'guardian')) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  const { data: stats, isLoading: statsLoading } = useQuery<GuardianStats>({
    queryKey: ['guardian-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/guardian/stats');
      return response.data;
    },
    enabled: !!user && user.role === 'guardian',
  });

  const { data: students, isLoading: studentsLoading } = useQuery<StudentProgress[]>({
    queryKey: ['guardian-students'],
    queryFn: async () => {
      const response = await apiClient.get('/guardian/students');
      return response.data;
    },
    enabled: !!user && user.role === 'guardian',
  });

  const { data: recentActivity, isLoading: activityLoading } = useQuery<RecentActivity[]>({
    queryKey: ['guardian-recent-activity'],
    queryFn: async () => {
      const response = await apiClient.get('/guardian/recent-activity');
      return response.data;
    },
    enabled: !!user && user.role === 'guardian',
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
      title: 'Students',
      value: stats?.total_students || 0,
      icon: Users,
      color: 'bg-blue-500',
      loading: statsLoading,
    },
    {
      title: 'Total Classes',
      value: stats?.total_classes || 0,
      icon: BookOpen,
      color: 'bg-green-500',
      loading: statsLoading,
    },
    {
      title: 'Completed Quizzes',
      value: stats?.completed_quizzes || 0,
      icon: CheckCircle,
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

  const getScoreColor = (percentage: number) => {
    if (percentage >= 90) return 'text-green-600';
    if (percentage >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getActivityIcon = (activityType: string) => {
    switch (activityType) {
      case 'quiz_completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'quiz_started':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'class_enrolled':
        return <BookOpen className="h-4 w-4 text-purple-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <DashboardLayout title="Guardian Dashboard">
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
              onClick={() => router.push('/guardian/students')}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <Users className="h-4 w-4 mr-2" />
              View Students
            </button>
            <button
              onClick={() => router.push('/guardian/reports')}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <TrendingUp className="h-4 w-4 mr-2" />
              View Reports
            </button>
            <button
              onClick={() => router.push('/guardian/communications')}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <MessageCircle className="h-4 w-4 mr-2" />
              Communications
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Student Progress */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Student Progress</h3>
              {studentsLoading ? (
                <div className="space-y-4">
                  {[1, 2].map((i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/3"></div>
                    </div>
                  ))}
                </div>
              ) : students && students.length > 0 ? (
                <div className="space-y-4">
                  {students.map((student) => (
                    <div
                      key={student.id}
                      className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                      onClick={() => router.push(`/guardian/students/${student.id}`)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900">
                          {student.first_name} {student.last_name}
                        </h4>
                        <span className={`text-lg font-bold ${getScoreColor(student.average_score)}`}>
                          {student.average_score.toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-sm text-gray-500 mb-2">{student.email}</p>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div className="flex items-center">
                          <BookOpen className="h-4 w-4 mr-1 text-blue-500" />
                          <span>{student.total_classes} classes</span>
                        </div>
                        <div className="flex items-center">
                          <CheckCircle className="h-4 w-4 mr-1 text-green-500" />
                          <span>{student.completed_quizzes} completed</span>
                        </div>
                        <div className="flex items-center">
                          <Clock className="h-4 w-4 mr-1 text-orange-500" />
                          <span>{student.pending_quizzes} pending</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No students found. Contact the school to link your account.</p>
              )}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
              {activityLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/3"></div>
                    </div>
                  ))}
                </div>
              ) : recentActivity && recentActivity.length > 0 ? (
                <div className="space-y-4">
                  {recentActivity.map((activity) => (
                    <div
                      key={activity.id}
                      className="flex items-start space-x-3 p-3 border border-gray-200 rounded-lg"
                    >
                      <div className="flex-shrink-0 mt-1">
                        {getActivityIcon(activity.activity_type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-900">
                            {activity.student_name}
                          </p>
                          <div className="flex items-center text-sm text-gray-500">
                            <Calendar className="h-3 w-3 mr-1" />
                            {new Date(activity.timestamp).toLocaleDateString()}
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          {activity.description}
                        </p>
                        {activity.score && activity.quiz_title && (
                          <div className="flex items-center mt-2 text-sm">
                            <Award className="h-3 w-3 mr-1 text-yellow-500" />
                            <span className="text-gray-600">
                              Quiz: {activity.quiz_title} - Score: {activity.score}%
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No recent activity found.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
