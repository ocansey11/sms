'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Plus, Edit, Trash2, Eye, BarChart3, Users, Calendar } from 'lucide-react';
import DashboardLayout from '@/components/DashboardLayout';
import apiClient from '@/lib/api';

interface Quiz {
  id: string;
  title: string;
  description?: string;
  time_limit_minutes: number;
  max_attempts: number;
  passing_score: number;
  is_published: boolean;
  status: string;
  questions_count: number;
  created_at: string;
  updated_at: string;
  creator: {
    id: string;
    name: string;
  };
}

export default function QuizListPage() {
  const router = useRouter();
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchQuizzes();
  }, []);

  const fetchQuizzes = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/teacher/quizzes');
      setQuizzes(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load quizzes');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteQuiz = async (quizId: string) => {
    if (!confirm('Are you sure you want to delete this quiz? This action cannot be undone.')) {
      return;
    }

    try {
      await apiClient.delete(`/teacher/quizzes/${quizId}`);
      // Remove quiz from local state
      setQuizzes(quizzes.filter(quiz => quiz.id !== quizId));
    } catch (err) {
      alert('Failed to delete quiz. Please try again.');
    }
  };

  const handleTogglePublish = async (quizId: string, currentlyPublished: boolean) => {
    try {
      await apiClient.put(`/teacher/quizzes/${quizId}/publish`, {
        is_published: !currentlyPublished
      });
      
      // Update quiz in local state
      setQuizzes(quizzes.map(quiz => 
        quiz.id === quizId 
          ? { ...quiz, is_published: !currentlyPublished }
          : quiz
      ));
    } catch (err) {
      alert('Failed to update quiz status. Please try again.');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <DashboardLayout title="My Quizzes">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout title="My Quizzes">
        <div className="text-center py-12">
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={fetchQuizzes}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="My Quizzes">
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Quizzes</h1>
          <p className="text-gray-600 mt-1">Manage your quizzes and track student performance</p>
        </div>
        <Link
          href="/teacher/quizzes/new"
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Create Quiz
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <BarChart3 className="h-5 w-5 text-blue-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Total Quizzes</p>
              <p className="text-xl font-bold text-gray-900">{quizzes.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Eye className="h-5 w-5 text-green-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Published</p>
              <p className="text-xl font-bold text-gray-900">
                {quizzes.filter(q => q.is_published).length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Edit className="h-5 w-5 text-yellow-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Drafts</p>
              <p className="text-xl font-bold text-gray-900">
                {quizzes.filter(q => !q.is_published).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Quiz List */}
      {quizzes.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No quizzes yet</h3>
          <p className="text-gray-600 mb-4">Get started by creating your first quiz</p>
          <Link
            href="/teacher/quizzes/new"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Create Your First Quiz
          </Link>
        </div>
      ) : (
        <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quiz
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Questions
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time Limit
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {quizzes.map((quiz) => (
                  <tr key={quiz.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{quiz.title}</div>
                        {quiz.description && (
                          <div className="text-sm text-gray-500 mt-1">{quiz.description}</div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        quiz.is_published
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {quiz.is_published ? 'Published' : 'Draft'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {quiz.questions_count} questions
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {quiz.time_limit_minutes} min
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {formatDate(quiz.created_at)}
                    </td>
                    <td className="px-6 py-4 text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <Link
                          href={`/teacher/quizzes/${quiz.id}/results`}
                          className="text-blue-600 hover:text-blue-900 p-1"
                          title="View Results"
                        >
                          <BarChart3 className="h-4 w-4" />
                        </Link>
                        <Link
                          href={`/teacher/quizzes/${quiz.id}/edit`}
                          className="text-gray-600 hover:text-gray-900 p-1"
                          title="Edit Quiz"
                        >
                          <Edit className="h-4 w-4" />
                        </Link>
                        <button
                          onClick={() => handleTogglePublish(quiz.id, quiz.is_published)}
                          className="text-green-600 hover:text-green-900 p-1"
                          title={quiz.is_published ? 'Unpublish' : 'Publish'}
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteQuiz(quiz.id)}
                          className="text-red-600 hover:text-red-900 p-1"
                          title="Delete Quiz"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
    </DashboardLayout>
  );
}
