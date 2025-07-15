import React, { useState, useEffect } from 'react';
import { Users, BookOpen, BarChart3, Plus, Eye } from 'lucide-react';
import { createApiClient } from '../api/config';
import Navbar from './Navbar';


// Define types for our data
interface User {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

interface Class {
  id: string;
  name: string;
  subject: string;
  academic_year: string;
  description: string;
  is_active: boolean;
  teacher: {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
  };
}

interface DashboardStats {
  total_users: number;
  total_teachers: number;
  total_students: number;
  total_guardians: number;
  total_classes: number;
  active_teachers: number;
}

const AdminDashboard: React.FC = () => {
  const [activeView, setActiveView] = useState<'dashboard' | 'users' | 'classes' | 'reports'>('dashboard');
  const [users, setUsers] = useState<User[]>([]);
  const [classes, setClasses] = useState<Class[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Use your new API client
  const apiClient = createApiClient();

  useEffect(() => {
    if (activeView === 'users') {
      fetchUsers();
    } else if (activeView === 'classes') {
      fetchClasses();
    } else if (activeView === 'dashboard') {
      fetchDashboardStats();
    }
  }, [activeView]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/admin/users');
      setUsers(response.data.data || response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch users');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchClasses = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/admin/classes');
      setClasses(response.data.data || response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch classes');
      console.error('Error fetching classes:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
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
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      
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
  );

  const renderUsersList = () => (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-900">All Users</h2>
        <button 
          onClick={() => setActiveView('dashboard')}
          className="text-blue-600 hover:text-blue-800"
        >
          ← Back to Dashboard
        </button>
      </div>
      <div className="p-6">
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading users...</p>
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <p className="text-red-600">{error}</p>
            <button 
              onClick={fetchUsers}
              className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created At
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {user.first_name} {user.last_name}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{user.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        user.role === 'admin' ? 'bg-purple-100 text-purple-800' :
                        user.role === 'teacher' ? 'bg-blue-100 text-blue-800' :
                        user.role === 'student' ? 'bg-green-100 text-green-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );

  const renderClassesList = () => (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-900">All Classes</h2>
        <button 
          onClick={() => setActiveView('dashboard')}
          className="text-blue-600 hover:text-blue-800"
        >
          ← Back to Dashboard
        </button>
      </div>
      <div className="p-6">
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading classes...</p>
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <p className="text-red-600">{error}</p>
            <button 
              onClick={fetchClasses}
              className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Class Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Subject
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Teacher
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Academic Year
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {classes.map((cls) => (
                  <tr key={cls.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{cls.name}</div>
                      <div className="text-sm text-gray-500">{cls.description}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{cls.subject}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {cls.teacher.first_name} {cls.teacher.last_name}
                      </div>
                      <div className="text-sm text-gray-500">{cls.teacher.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{cls.academic_year}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        cls.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {cls.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );

  return (

    <>
    <Navbar role="admin" />
    <div className="min-h-screen bg-gray-50">

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeView === 'dashboard' && (
          <>
            {renderDashboard()}
            
            {/* Recent Activity */}
            <div className="mt-8 bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between py-2">
                    <div>
                      <p className="font-medium text-gray-900">Admin dashboard functional</p>
                      <p className="text-sm text-gray-500">API endpoints connected successfully</p>
                    </div>
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                      System
                    </span>
                  </div>
                  <div className="flex items-center justify-between py-2">
                    <div>
                      <p className="font-medium text-gray-900">Demo credentials verified</p>
                      <p className="text-sm text-gray-500">All role-based logins working</p>
                    </div>
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                      Update
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
        
        {activeView === 'users' && renderUsersList()}
        {activeView === 'classes' && renderClassesList()}
        {activeView === 'reports' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">System Reports</h2>
            <p className="text-gray-600">Reports feature coming soon...</p>
            <button 
              onClick={() => setActiveView('dashboard')}
              className="mt-4 text-blue-600 hover:text-blue-800"
            >
              ← Back to Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
    </>
  );

  
};

export default AdminDashboard;
