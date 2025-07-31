import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is logged in on app start
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      authService.getProfile()
        .then(userData => {
          setUser(userData);
        })
        .catch(() => {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    try {
      setError(null);
      const response = await authService.login(email, password);
      const { user: userData, access_token, refresh_token } = response;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      setUser(userData);
      return userData;
    } catch (err) {
      setError(err.message || 'Login failed');
      throw err;
    }
  };

  const register = async (userData) => {
    try {
      setError(null);
      const response = await authService.register(userData);
      const { user: newUser, access_token, refresh_token } = response;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      setUser(newUser);
      return newUser;
    } catch (err) {
      setError(err.message || 'Registration failed');
      throw err;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    }
  };

  const updateProfile = async (profileData) => {
    try {
      setError(null);
      const updatedUser = await authService.updateProfile(profileData);
      setUser(updatedUser);
      return updatedUser;
    } catch (err) {
      setError(err.message || 'Profile update failed');
      throw err;
    }
  };

  const changePassword = async (currentPassword, newPassword) => {
    try {
      setError(null);
      await authService.changePassword(currentPassword, newPassword);
    } catch (err) {
      setError(err.message || 'Password change failed');
      throw err;
    }
  };

  const refreshToken = async () => {
    try {
      const refresh_token = localStorage.getItem('refresh_token');
      if (!refresh_token) {
        throw new Error('No refresh token available');
      }

      const response = await authService.refreshToken(refresh_token);
      const { access_token } = response;
      
      localStorage.setItem('access_token', access_token);
      return access_token;
    } catch (err) {
      logout();
      throw err;
    }
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    refreshToken,
    setError
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};