import React from 'react';
import { useAuth } from '../contexts/AuthContext';

interface NavbarProps {
  role: string;
}

const Navbar: React.FC<NavbarProps> = ({ role }) => {
  const { user, logout } = useAuth();

  const handleSettings = () => {
    // TODO: Implement settings functionality
    console.log('Settings clicked');
  };

  const handleAdminPanel = () => {
    // TODO: Navigate to admin panel or show admin menu
    console.log('Admin panel clicked');
  };

  return (
    <nav className="w-full flex items-center justify-between bg-white shadow-md px-6 py-4 border-b">
      {/* Left side - Logo/Title */}
      <div className="font-bold text-xl text-gray-900">SMS Portal</div>
      
      {/* Right side - User info and actions */}
      <div className="flex items-center gap-6">
        {/* Welcome message */}
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-600">
            Welcome back, <span className="font-medium text-gray-900">{user?.first_name || 'User'}</span>
          </span>
          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium uppercase">
            {role}
          </span>
        </div>
        
        {/* Action buttons */}
        <div className="flex items-center gap-3">
          <button 
            onClick={handleSettings}
            className="px-3 py-2 text-sm text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
          >
            Settings
          </button>
          
          {/* Admin Panel button for admins */}
          {role === 'admin' && (
            <button 
              onClick={handleAdminPanel}
              className="px-3 py-2 text-sm text-green-700 hover:text-green-900 hover:bg-green-50 rounded-md transition-colors"
            >
              Admin Panel
            </button>
          )}
          
          <button 
            onClick={logout}
            className="px-4 py-2 text-sm text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;