import React from 'react';
import Navbar from './Navbar';

const GuardianDashboard: React.FC = () => (
  <div className="p-8">
    <Navbar role ="guardian" />
    <h1 className="text-2xl font-bold mb-4">Guardian Dashboard</h1>
    <p>Coming Soon: Guardian features and student monitoring.</p>
  </div>
);

export default GuardianDashboard;