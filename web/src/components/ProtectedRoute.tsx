import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  allowedRoles 
}) => {
  const { isAuthenticated, user } = useAuth();
  
  console.log('🔍 ProtectedRoute - isAuthenticated:', isAuthenticated);
  console.log('🔍 ProtectedRoute - user:', user);
  console.log('🔍 ProtectedRoute - allowedRoles:', allowedRoles);
  
  // Show loading while auth is being restored
  if (isAuthenticated === null) {
    console.log('⏳ ProtectedRoute - Showing loading...');
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Restoring authentication...</p>
        </div>
      </div>
    );
  }
  
  // Not authenticated - redirect to login
  if (isAuthenticated === false) {
    console.log('❌ ProtectedRoute - Redirecting to login');
    return <Navigate to="/login" replace />;
  }
  
  // NEW - Check if user has required role
  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    console.log(`❌ ProtectedRoute - Access denied. User role: ${user.role}, Required: ${allowedRoles.join(', ')}`);
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          <div className="text-red-600 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-6">
            You don't have permission to access this area. 
            Required role: <strong>{allowedRoles.join(' or ')}</strong>
            <br />
            Your role: <strong>{user.role}</strong>
          </p>
          <button 
            onClick={() => window.location.href = `/${user.role}`}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            Go to My Dashboard
          </button>
        </div>
      </div>
    );
  }
  
  console.log('✅ ProtectedRoute - Access granted');
  return <>{children}</>;
};

export default ProtectedRoute;