import React, { useState, useEffect } from 'react';
import { Users, BookOpen, BarChart3, Plus, Eye } from 'lucide-react';
import { createApiClient } from '../api/config';
import { useAuth } from '../contexts/AuthContext';
import Navbar from './Navbar';

// Import the new modular components
import DashboardStats from './admin/dashboard/DashboardStats';
import UsersListPage from './admin/users/UsersListPage';
import ClassesListPage from './admin/classes/ClassesListPage';
import ReportsPage from './admin/reports/ReportsPage';

interface DashboardStats {
  total_users: number;
  total_teachers: number;
  total_students: number;
  total_guardians: number;
  total_classes: number;
  active_teachers: number;
}

const AdminDashboard: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  
  const [activeView, setActiveView] = useState<'dashboard' | 'users' | 'classes' | 'reports'>('dashboard');
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const apiClient = createApiClient();

  useEffect(() => {
    console.log('🔍 AdminDashboard - isAuthenticated:', isAuthenticated);
    console.log('🔍 AdminDashboard - user:', user);
    console.log('🔍 AdminDashboard - user role:', user?.role);
    
    // ONLY fetch stats when authenticated AND admin
    if (isAuthenticated === true && user?.role === 'admin' && activeView === 'dashboard') {
      fetchDashboardStats();
    }
  }, [isAuthenticated, user, activeView]);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      console.log('🔍 Fetching dashboard stats...');
      const response = await apiClient.get('/admin/dashboard/stats');
      setStats(response.data.data || response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch dashboard stats');
      console.error('Error fetching stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderDashboard = () => (
    <>
      {/* Welcome message */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.first_name || user?.email || 'Admin'}! 👋
        </h1>
        <p className="text-gray-600">Here's your admin dashboard overview</p>
      </div>

      {/* Dashboard Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* User Management Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">User Management</h2>
            <Users className="h-5 w-5 text-gray-400" />
          </div>
          <p className="text-gray-600 mb-4">
            Manage teachers, students, and guardians. Control access and permissions.
          </p>
          <div className="space-y-2">
            <button 
              onClick={() => setActiveView('users')}
              className="w-full text-left px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center justify-center"
            >
              <Eye className="h-4 w-4 mr-2" />
              View All Users
            </button>
            <button className="w-full text-left px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors flex items-center justify-center">
              <Plus className="h-4 w-4 mr-2" />
              Add New User
            </button>
          </div>
          {stats && (
            <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
              <div className="text-center p-2 bg-blue-50 rounded">
                <div className="font-semibold text-blue-600">{stats.total_teachers}</div>
                <div className="text-gray-600">Teachers</div>
              </div>
              <div className="text-center p-2 bg-green-50 rounded">
                <div className="font-semibold text-green-600">{stats.total_students}</div>
                <div className="text-gray-600">Students</div>
              </div>
            </div>
          )}
        </div>

        {/* Class Management Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Class Management</h2>
            <BookOpen className="h-5 w-5 text-gray-400" />
          </div>
          <p className="text-gray-600 mb-4">
            Create and manage classes, assign teachers, and monitor enrollment.
          </p>
          <div className="space-y-2">
            <button 
              onClick={() => setActiveView('classes')}
              className="w-full text-left px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center justify-center"
            >
              <Eye className="h-4 w-4 mr-2" />
              View All Classes
            </button>
            <button className="w-full text-left px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors flex items-center justify-center">
              <Plus className="h-4 w-4 mr-2" />
              Create New Class
            </button>
          </div>
          {stats && (
            <div className="mt-4 text-center">
              <div className="text-2xl font-bold text-indigo-600">{stats.total_classes}</div>
              <div className="text-gray-600">Total Classes</div>
              <div className="text-sm text-green-600 mt-1">{stats.active_teachers} Active Teachers</div>
            </div>
          )}
        </div>

        {/* System Reports Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">System Reports</h2>
            <BarChart3 className="h-5 w-5 text-gray-400" />
          </div>
          <p className="text-gray-600 mb-4">
            View system analytics, user activity, and performance metrics.
          </p>
          <div className="space-y-2">
            <button 
              onClick={() => setActiveView('reports')}
              className="w-full text-left px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors flex items-center justify-center"
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              View Reports
            </button>
          </div>
          {stats && (
            <div className="mt-4 text-center">
              <div className="text-2xl font-bold text-purple-600">{stats.total_users}</div>
              <div className="text-gray-600">Total Users</div>
            </div>
          )}
        </div>
      </div>

      {/* Use the DashboardStats component for the detailed stats */}
      <DashboardStats 
        stats={stats || {}} 
        loading={loading} 
        error={error} 
      />
    </>
  );

  return (
    <>
      <Navbar role="admin" />
      <div className="min-h-screen bg-gray-50">
        <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
          
          {/* Dashboard View */}
          {activeView === 'dashboard' && (
            <div className="max-w-7xl mx-auto">
              {renderDashboard()}
            </div>
          )}
          
          {/* Users View */}
          {activeView === 'users' && (
            <div>
              <div className="mb-6">
                <button 
                  onClick={() => setActiveView('dashboard')}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Back to Dashboard
                </button>
              </div>
              <UsersListPage />
            </div>
          )}
          
          {/* Classes View */}
          {activeView === 'classes' && (
            <div>
              <div className="mb-6">
                <button 
                  onClick={() => setActiveView('dashboard')}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Back to Dashboard
                </button>
              </div>
              <ClassesListPage />
            </div>
          )}
          
          {/* Reports View */}
          {activeView === 'reports' && (
            <div>
              <div className="mb-6">
                <button 
                  onClick={() => setActiveView('dashboard')}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Back to Dashboard
                </button>
              </div>
              <ReportsPage />
            </div>
          )}
          
        </div>
      </div>
    </>
  );
};

export default AdminDashboard;
