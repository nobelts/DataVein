import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../useAuth';

const Header: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Hide header on home page
  if (location.pathname === '/') {
    return null;
  }

  const handleLogoClick = () => {
    // If not logged in, go to home page
    // If logged in, stay on current page (do nothing)
    if (!isAuthenticated) {
      navigate('/');
    }
  };

  return (
    <header className="backdrop-blur-sm bg-gradient-to-r from-blue-200/95 to-purple-200/95 border-b border-purple-300/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div 
            onClick={handleLogoClick}
            className={`flex items-center ${!isAuthenticated ? 'cursor-pointer hover:opacity-80' : 'cursor-default'} transition-opacity`}
          >
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">D</span>
              </div>
              <span className="text-xl font-bold text-gray-900">DataVein</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
