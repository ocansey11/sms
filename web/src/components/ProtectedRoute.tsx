'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'admin' | 'teacher' | 'student' | 'guardian';
  redirectTo?: string;
}

export default function ProtectedRoute({ 
  children, 
  requiredRole, 
  redirectTo = '/login' 
}: ProtectedRouteProps) {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Don't redirect while still loading
    if (isLoading) return;

    // If not authenticated, redirect to login
    if (!isAuthenticated || !user) {
      router.push(redirectTo);
      return;
    }

    // If specific role required, check user role
    if (requiredRole && user.role !== requiredRole) {
      // Redirect based on user's actual role
      switch (user.role) {
        case 'admin':
          router.push('/admin');
          break;
        case 'teacher':
          router.push('/teacher/dashboard');
          break;
        case 'student':
          router.push('/student/dashboard');
          break;
        case 'guardian':
          router.push('/guardian/dashboard');
          break;
        default:
          router.push('/login');
      }
      return;
    }
  }, [user, isAuthenticated, isLoading, requiredRole, router, redirectTo]);

  // Show loading spinner while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render content if not authenticated or wrong role
  if (!isAuthenticated || !user || (requiredRole && user.role !== requiredRole)) {
    return null;
  }

  // Render protected content
  return <>{children}</>;
}
