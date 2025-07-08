'use client';

import { useEffect, useState } from 'react';
import { QuizCreateForm } from '@/components/quiz/QuizCreateForm';
import DashboardLayout from '@/components/DashboardLayout';
import apiClient from '@/lib/api';

interface Class {
  id: string;
  name: string;
}

export default function NewQuizPage() {
  const [classes, setClasses] = useState<Class[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchClasses();
  }, []);

  const fetchClasses = async () => {
    try {
      const response = await apiClient.get('/teacher/classes');
      setClasses(response.data);
    } catch (error) {
      console.error('Failed to fetch classes:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout title="Create New Quiz">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Create New Quiz">
      <QuizCreateForm classes={classes} />
    </DashboardLayout>
  );
}
