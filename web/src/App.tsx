import React from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './components/LoginPage';
import AdminDashboard from './components/AdminDashboard';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const AppContent: React.FC = () => {
  const { user } = useAuth();

  return (
    <>
      <Routes>
        <Route path="/admin" element={
          <ProtectedRoute>
            <AdminDashboard />
          </ProtectedRoute>
        } />
        <Route path="/teacher" element={
          <ProtectedRoute>
            <div className="p-8">Teacher Dashboard (Coming Soon)</div>
          </ProtectedRoute>
        } />
        <Route path="/student" element={
          <ProtectedRoute>
            <div className="p-8">Student Dashboard (Coming Soon)</div>
          </ProtectedRoute>
        } />
        <Route path="/guardian" element={
          <ProtectedRoute>
            <div className="p-8">Guardian Dashboard (Coming Soon)</div>
          </ProtectedRoute>
        } />
        <Route path="/login" element={<LoginPage />} />
        <Route path="*" element={
          <ProtectedRoute>
            <Navigate to={`/${user?.role ?? 'login'}`} />
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
