import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { GraduationCap, Eye, EyeOff } from 'lucide-react';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
    } catch (error) {
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const fillDemoCredentials = (demoEmail: string, demoPassword: string) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="flex items-center justify-center mb-4">
            <GraduationCap className="h-12 w-12 text-blue-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900">SMS Portal</h2>
          <p className="mt-2 text-gray-600">Sign in to your account</p>
        </div>

        {/* Demo Credentials */}
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Demo Credentials:</h3>
          <div className="space-y-2">
            <button
              type="button"
              onClick={() => fillDemoCredentials('admin@school.edu', 'admin123')}
              className="w-full text-left p-2 text-xs bg-purple-50 hover:bg-purple-100 rounded border"
            >
              <div className="font-medium">👨‍💼 Admin</div>
              <div className="text-gray-600">admin@school.edu / admin123</div>
            </button>
            <button
              type="button"
              onClick={() => fillDemoCredentials('sarah.johnson@teacher.schoolsms.com', 'teacher123')}
              className="w-full text-left p-2 text-xs bg-blue-50 hover:bg-blue-100 rounded border"
            >
              <div className="font-medium">👩‍🏫 Teacher</div>
              <div className="text-gray-600">sarah.johnson@teacher.schoolsms.com / teacher123</div>
            </button>
            <button
              type="button"
              onClick={() => fillDemoCredentials('emma.smith@student.schoolsms.com', 'student123')}
              className="w-full text-left p-2 text-xs bg-green-50 hover:bg-green-100 rounded border"
            >
              <div className="font-medium">👩‍🎓 Student</div>
              <div className="text-gray-600">emma.smith@student.schoolsms.com / student123</div>
            </button>
            <button
              type="button"
              onClick={() => fillDemoCredentials('john.smith@email.com', 'guardian123')}
              className="w-full text-left p-2 text-xs bg-yellow-50 hover:bg-yellow-100 rounded border"
            >
              <div className="font-medium">👨‍👩‍👧‍👦 Guardian</div>
              <div className="text-gray-600">john.smith@email.com / guardian123</div>
            </button>
          </div>
        </div>

        {/* Login Form */}
        <form className="mt-8 space-y-6 bg-white p-8 rounded-lg shadow" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your email"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="mt-1 relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4 text-gray-400" />
                  ) : (
                    <Eye className="h-4 w-4 text-gray-400" />
                  )}
                </button>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
