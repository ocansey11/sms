import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'teacher' | 'student' | 'guardian';
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean | null; // ✅ FIXED - Allow null for loading state
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null); // ✅ Start as loading
  const navigate = useNavigate();

  useEffect(() => {
    console.log('🔍 AuthContext: Checking stored auth on app load...');
    const token = localStorage.getItem('auth_token');
    const userData = localStorage.getItem('user_data');
    
    console.log('🔍 Found token:', token ? 'Yes' : 'No');
    console.log('🔍 Found userData:', userData ? 'Yes' : 'No');
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        console.log('🔍 Parsed user:', parsedUser);
        setUser(parsedUser);
        setIsAuthenticated(true);
        console.log('✅ User restored from localStorage');
      } catch (error) {
        console.error('❌ Error parsing stored user data:', error);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        setIsAuthenticated(false);
      }
    } else {
      console.log('❌ No stored auth found');
      setIsAuthenticated(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      console.log('Backend response:', data);
      
      const tokenPayload = JSON.parse(atob(data.access_token.split('.')[1]));
      console.log('Token payload:', tokenPayload);
      
      const user = {
        id: tokenPayload.sub,
        email: tokenPayload.email,
        role: tokenPayload.role,
        first_name: tokenPayload.first_name || '',
        last_name: tokenPayload.last_name || ''
      };
      
      console.log('Decoded user:', user);
      
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('user_data', JSON.stringify(user));
      setUser(user);
      setIsAuthenticated(true);
      
      console.log('Navigating to:', `/${user.role}`);
      navigate(`/${user.role}`);
      
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      login, 
      logout, 
      isAuthenticated // ✅ FIXED - Let null pass through
    }}>
      {children}
    </AuthContext.Provider>
  );
};
