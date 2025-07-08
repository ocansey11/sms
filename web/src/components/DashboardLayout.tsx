'use client';

import { ReactNode } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { 
  GraduationCap, 
  LogOut, 
  Menu, 
  X,
  BookOpen,
  Users,
  Shield,
  BarChart3,
  Settings
} from 'lucide-react';
import { useState } from 'react';

interface DashboardLayoutProps {
  children: ReactNode;
  title: string;
}

export default function DashboardLayout({ children, title }: DashboardLayoutProps) {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'teacher':
        return <BookOpen className="h-5 w-5" />;
      case 'student':
        return <Users className="h-5 w-5" />;
      case 'guardian':
        return <Shield className="h-5 w-5" />;
      default:
        return <Users className="h-5 w-5" />;
    }
  };

  const getNavigationItems = () => {
    const baseItems = [
      { name: 'Dashboard', href: `/${user?.role}/dashboard`, icon: BarChart3 },
    ];

    switch (user?.role) {
      case 'teacher':
        return [
          ...baseItems,
          { name: 'Classes', href: '/teacher/classes', icon: BookOpen },
          { name: 'Quizzes', href: '/teacher/quizzes', icon: Settings },
        ];
      case 'student':
        return [
          ...baseItems,
          { name: 'Quizzes', href: '/student/quizzes', icon: BookOpen },
          { name: 'Progress', href: '/student/progress', icon: BarChart3 },
        ];
      case 'guardian':
        return [
          ...baseItems,
          { name: 'Students', href: '/guardian/students', icon: Users },
          { name: 'Reports', href: '/guardian/reports', icon: BarChart3 },
        ];
      default:
        return baseItems;
    }
  };

  const navigationItems = getNavigationItems();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Title */}
            <div className="flex items-center">
              <button
                type="button"
                className="md:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              >
                {isMobileMenuOpen ? (
                  <X className="h-6 w-6" />
                ) : (
                  <Menu className="h-6 w-6" />
                )}
              </button>
              <div className="flex items-center ml-2 md:ml-0">
                <GraduationCap className="h-8 w-8 text-blue-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">
                  SMS
                </span>
              </div>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex space-x-8">
              {navigationItems.map((item) => (
                <button
                  key={item.name}
                  onClick={() => router.push(item.href)}
                  className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium flex items-center"
                >
                  <item.icon className="h-4 w-4 mr-2" />
                  {item.name}
                </button>
              ))}
            </nav>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                {getRoleIcon(user?.role || '')}
                <span className="text-sm font-medium text-gray-900">
                  {user?.first_name} {user?.last_name}
                </span>
                <span className="text-xs text-gray-500 capitalize">
                  ({user?.role})
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="text-gray-400 hover:text-gray-500 p-2 rounded-md hover:bg-gray-100"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white border-t border-gray-200">
              {navigationItems.map((item) => (
                <button
                  key={item.name}
                  onClick={() => {
                    router.push(item.href);
                    setIsMobileMenuOpen(false);
                  }}
                  className="text-gray-500 hover:text-gray-900 block px-3 py-2 rounded-md text-base font-medium w-full text-left flex items-center"
                >
                  <item.icon className="h-4 w-4 mr-2" />
                  {item.name}
                </button>
              ))}
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
          </div>
          {children}
        </div>
      </main>
    </div>
  );
}
