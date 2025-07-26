import React from 'react';
import { useNavigate } from 'react-router-dom';

const SignUpPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow p-8 text-center">
        <h2 className="text-2xl font-bold mb-4 text-blue-700">Sign Up</h2>
        <p className="mb-8 text-gray-600">
          Choose how you want to use SMS SaaS.
        </p>
        <div className="space-y-4">
          <button
            onClick={() => navigate('/signup/organization')}
            className="w-full py-3 px-6 bg-blue-600 text-white rounded-md font-semibold hover:bg-blue-700 transition-colors"
          >
            Sign Up as Organization
          </button>
          <button
            onClick={() => navigate('/signup/teacher')}
            className="w-full py-3 px-6 bg-green-600 text-white rounded-md font-semibold hover:bg-green-700 transition-colors"
          >
            Sign Up as Teacher
          </button>
        </div>
        <div className="mt-6">
          <span className="text-gray-500">Already have an account?</span>
          <button
            onClick={() => navigate('/login')}
            className="ml-2 text-blue-600 hover:underline font-medium"
          >
            Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default SignUpPage;