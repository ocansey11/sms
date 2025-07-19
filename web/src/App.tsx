import React from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './components/LoginPage';
import AdminDashboard from './components/AdminDashboard';
import ProtectedRoute from './components/ProtectedRoute';

const AppContent: React.FC = () => {
  const { user } = useAuth();

  return (
    <>
      <Routes>
        {/* Admin Dashboard - Only admins */}
        <Route path="/admin" element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminDashboard />
          </ProtectedRoute>
        } />
        
        {/* Teacher Dashboard - Only teachers */}
        <Route path="/teacher" element={
          <ProtectedRoute allowedRoles={['teacher']}>
            <div className="p-8">
              <h1 className="text-2xl font-bold">Teacher Dashboard</h1>
              <p>Welcome, Teacher!</p>
            </div>
          </ProtectedRoute>
        } />
        
        {/* Student Dashboard - Only students */}
        <Route path="/student" element={
          <ProtectedRoute allowedRoles={['student']}>
            <div className="p-8">
              <h1 className="text-2xl font-bold">Student Dashboard</h1>
              <p>Welcome, Student!</p>
            </div>
          </ProtectedRoute>
        } />
        
        {/* Guardian Dashboard - Only guardians */}
        <Route path="/guardian" element={
          <ProtectedRoute allowedRoles={['guardian']}>
            <div className="p-8">
              <h1 className="text-2xl font-bold">Guardian Dashboard</h1>
              <p>Welcome, Guardian!</p>
            </div>
          </ProtectedRoute>
        } />
        
        {/* Login page - No protection needed */}
        <Route path="/login" element={<LoginPage />} />
        
        {/* Default redirect based on user role */}
        <Route path="/" element={
          <ProtectedRoute>
            <Navigate to={`/${user?.role ?? 'login'}`} replace />
          </ProtectedRoute>
        } />
        
        {/* Catch all - redirect to user's dashboard */}
        <Route path="*" element={
          <ProtectedRoute>
            <Navigate to={`/${user?.role ?? 'login'}`} replace />
          </ProtectedRoute>
        } />
      </Routes>
    </>
  );
};

const App: React.FC = () => (
  <Router>
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  </Router>
);

export default App;
