import React from 'react';
import Navbar from './Navbar';

const TeacherDashboard: React.FC = () => (
  <>
    <Navbar role="teacher" />
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Teacher Dashboard</h1>
      <p>Coming Soon: Teacher features and class management.</p>
    </div>
  </>
);

export default TeacherDashboard;