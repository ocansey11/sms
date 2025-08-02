import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../supabaseClient';

const SignUpPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'org' | 'teacher'>('org');
  const [orgForm, setOrgForm] = useState({
    orgName: '',
    adminFirstName: '',
    adminLastName: '',
    adminEmail: '',
    adminPassword: '',
  });
  const [teacherForm, setTeacherForm] = useState({
    teacherFirstName: '',
    teacherLastName: '',
    teacherEmail: '',
    teacherPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  // Handlers for form field changes
  const handleOrgChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setOrgForm({ ...orgForm, [e.target.name]: e.target.value });
  };
  const handleTeacherChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTeacherForm({ ...teacherForm, [e.target.name]: e.target.value });
  };

  // Submit handlers
  const handleOrgSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const res = await fetch('/api/auth/signup/organization', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          organization_name: orgForm.orgName,
          admin_first_name: orgForm.adminFirstName,
          admin_last_name: orgForm.adminLastName,
          admin_email: orgForm.adminEmail,
          admin_password: orgForm.adminPassword,
        }),
      });
      if (!res.ok) throw new Error('Sign up failed');
      setSuccess('Organization registered! You can now log in.');
      setTimeout(() => navigate('/login'), 1500);
    } catch (err) {
      setError('Sign up failed. Please check your details.');
    } finally {
      setLoading(false);
    }
  };

  const handleTeacherSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const res = await fetch('/api/auth/signup/teacher', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          teacher_first_name: teacherForm.teacherFirstName,
          teacher_last_name: teacherForm.teacherLastName,
          teacher_email: teacherForm.teacherEmail,
          teacher_password: teacherForm.teacherPassword,
        }),
      });
      if (!res.ok) throw new Error('Sign up failed');
      setSuccess('Teacher registered! You can now log in.');
      setTimeout(() => navigate('/login'), 1500);
    } catch (err) {
      setError('Sign up failed. Please check your details.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignUp = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: window.location.origin + '/dashboard', // or wherever you want
      },
    });
    if (error) {
      setError('Google sign up failed.');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold mb-4 text-blue-700 text-center">
          Sign Up
        </h2>
        <div className="flex mb-6">
          <button
            className={`flex-1 py-2 rounded-l-md font-semibold transition-colors ${
              activeTab === 'org'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-blue-700 hover:bg-gray-200'
            }`}
            onClick={() => setActiveTab('org')}
            type="button"
          >
            Sign Up as Organization
          </button>
          <button
            className={`flex-1 py-2 rounded-r-md font-semibold transition-colors ${
              activeTab === 'teacher'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-green-700 hover:bg-gray-200'
            }`}
            onClick={() => setActiveTab('teacher')}
            type="button"
          >
            Sign Up as Teacher
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4 text-red-700 text-sm">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-50 border border-green-200 rounded-md p-3 mb-4 text-green-700 text-sm">
            {success}
          </div>
        )}

        <div className="mb-4 flex flex-col gap-2">
          <button
            onClick={handleGoogleSignUp}
            className="w-full py-2 bg-red-600 text-white rounded font-semibold hover:bg-red-700 transition-colors"
            type="button"
          >
            Sign Up with Google
          </button>
        </div>

        {activeTab === 'org' ? (
          <form className="space-y-4" onSubmit={handleOrgSubmit}>
            <input
              type="text"
              name="orgName"
              placeholder="Organization Name"
              value={orgForm.orgName}
              onChange={handleOrgChange}
              required
              className="w-full px-3 py-2 border rounded"
            />
            <input
              type="text"
              name="adminFirstName"
              placeholder="Admin First Name"
              value={orgForm.adminFirstName}
              onChange={handleOrgChange}
              required
              className="w-full px-3 py-2 border rounded"
            />
            <input
              type="text"
              name="adminLastName"
              placeholder="Admin Last Name"
              value={orgForm.adminLastName}
              onChange={handleOrgChange}
              required
              className="w-full px-3 py-2 border rounded"
            />
            <input
              type="email"
              name="adminEmail"
              placeholder="Admin Email"
              value={orgForm.adminEmail}
              onChange={handleOrgChange}
              required
              className="w-full px-3 py-2 border rounded"
            />
            <input
              type="password"
              name="adminPassword"
              placeholder="Admin Password"
              value={orgForm.adminPassword}
              onChange={handleOrgChange}
              required
              className="w-full px-3 py-2 border rounded"
            />
            <button
              type="submit"
              className="w-full py-2 bg-blue-600 text-white rounded font-semibold hover:bg-blue-700 transition-colors"
              disabled={loading}
            >
              {loading ? 'Signing up...' : 'Sign Up as Organization'}
            </button>
          </form>
        ) : (
          <form className="space-y-4" onSubmit={handleTeacherSubmit}>
            <input
              type="text"
              name="teacherFirstName"
              placeholder="First Name"
              value={teacherForm.teacherFirstName}
              onChange={handleTeacherChange}
              required
              className="w-full px-3 py-2 border rounded"
            />
            <input
              type="text"
              name="teacherLastName"
              placeholder="Last Name"
              value={teacherForm.teacherLastName}
              onChange={handleTeacherChange}
              required
              className="w-full px-3 py-2 border rounded"
            />
            <input
              type="email"
              name="teacherEmail"
              placeholder="Email"
              value={teacherForm.teacherEmail}
              onChange={handleTeacherChange}
              required
              className="w-full px-3 py-2 border rounded"
            />
            <input
              type="password"
              name="teacherPassword"
              placeholder="Password"
              value={teacherForm.teacherPassword}
              onChange={handleTeacherChange}
              required
              className="w-full px-3 py-2 border rounded"
            />
            <button
              type="submit"
              className="w-full py-2 bg-green-600 text-white rounded font-semibold hover:bg-green-700 transition-colors"
              disabled={loading}
            >
              {loading ? 'Signing up...' : 'Sign Up as Teacher'}
            </button>
          </form>
        )}

        <div className="mt-6 text-center">
          <span className="text-gray-500">Already have an account?</span>
          <button
            onClick={() => navigate('/login')}
            className="ml-2 text-blue-600 hover:underline font-medium"
            type="button"
          >
            Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default SignUpPage;