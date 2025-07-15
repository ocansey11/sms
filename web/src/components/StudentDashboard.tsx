import React from 'react';
import Navbar from './Navbar';



const StudentDashboard: React.FC = () => (
  <>
    <Navbar role="student" />
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Student Dashboard</h1>
      <p>Coming Soon: Student features and progress tracking.</p>
    </div>
  </>
);

export default StudentDashboard;