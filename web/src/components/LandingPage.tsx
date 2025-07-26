import React from 'react';
import { useNavigate } from 'react-router-dom';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow p-8 text-center">
        <h1 className="text-3xl font-bold mb-4 text-blue-700">Welcome to SMS SaaS</h1>
        <p className="mb-8 text-gray-600">
          Manage your classes, users, and organization with ease.<br />
          Choose your path to get started.
        </p>
        <div className="space-y-4">
          <button
            onClick={() => navigate('/signup')}
            className="w-full py-3 px-6 bg-blue-600 text-white rounded-md font-semibold hover:bg-blue-700 transition-colors"
          >
            Sign Up
          </button>
          <button
            onClick={() => navigate('/login')}
            className="w-full py-3 px-6 bg-gray-200 text-blue-700 rounded-md font-semibold hover:bg-gray-300 transition-colors"
          >
            Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;