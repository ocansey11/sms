'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Plus, Search, Filter, Edit, Eye, Trash2, BookOpen, Users } from 'lucide-react';
import { apiClient } from '@/lib/api';
import ProtectedRoute from '@/components/ProtectedRoute';

interface Teacher {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
}

interface Class {
  id: string;
  name: string;
  subject: string;
  academic_year: string;
  description: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  teacher: Teacher;
}

function AdminClassesContent() {
  const [classes, setClasses] = useState<Class[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [subjectFilter, setSubjectFilter] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchClasses();
  }, []);

  const fetchClasses = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/admin/classes');
      setClasses(response.data);
    } catch (err) {
      setError('Failed to fetch classes');
      console.error('Error fetching classes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClass = async (id: string) => {
    if (!confirm('Are you sure you want to delete this class?')) return;
    
    try {
      await apiClient.delete(`/admin/classes/${id}`);
      setClasses(classes.filter(c => c.id !== id));
    } catch (err) {
      setError('Failed to delete class');
      console.error('Error deleting class:', err);
    }
  };

  const filteredClasses = classes.filter(cls => {
    const matchesSearch = cls.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         cls.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         cls.teacher.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         cls.teacher.last_name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesSubject = !subjectFilter || cls.subject.toLowerCase().includes(subjectFilter.toLowerCase());
    
    return matchesSearch && matchesSubject;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading classes...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">{error}</p>
          <button
            onClick={fetchClasses}
            className="mt-2 text-blue-600 hover:text-blue-800"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Class Management</h1>
              <p className="mt-1 text-sm text-gray-500">Manage all classes in the system</p>
            </div>
            <Link
              href="/admin/classes/new"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create Class
            </Link>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="p-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <input
                    type="text"
                    placeholder="Search classes..."
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
              </div>
              <div className="sm:w-48">
                <input
                  type="text"
                  placeholder="Filter by subject..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={subjectFilter}
                  onChange={(e) => setSubjectFilter(e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Classes Grid */}
        {filteredClasses.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredClasses.map((cls) => (
              <div key={cls.id} className="bg-white rounded-lg shadow hover:shadow-md transition-shadow">
                <div className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900">{cls.name}</h3>
                      <p className="text-sm text-gray-600 mt-1">{cls.subject}</p>
                      <p className="text-sm text-gray-500 mt-2">{cls.academic_year}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button className="text-gray-400 hover:text-gray-600">
                        <Eye className="h-4 w-4" />
                      </button>
                      <button className="text-gray-400 hover:text-gray-600">
                        <Edit className="h-4 w-4" />
                      </button>
                      <button 
                        onClick={() => handleDeleteClass(cls.id)}
                        className="text-gray-400 hover:text-red-600"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  
                  {cls.description && (
                    <p className="text-sm text-gray-600 mt-3">{cls.description}</p>
                  )}
                  
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center text-sm text-gray-500">
                        <Users className="h-4 w-4 mr-1" />
                        Teacher: {cls.teacher.first_name} {cls.teacher.last_name}
                      </div>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        cls.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {cls.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No classes found</h3>
            <p className="mt-2 text-gray-500">
              {searchTerm || subjectFilter ? 'Try adjusting your search or filter criteria.' : 'Get started by creating a new class.'}
            </p>
            {!searchTerm && !subjectFilter && (
              <Link
                href="/admin/classes/new"
                className="mt-4 inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                <Plus className="h-4 w-4 mr-2" />
                Create Class
              </Link>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function AdminClasses() {
  return (
    <ProtectedRoute requiredRole="admin">
      <AdminClassesContent />
    </ProtectedRoute>
  );
}
