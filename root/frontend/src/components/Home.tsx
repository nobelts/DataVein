import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../useAuth';

const Home: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogoClick = () => {
    // If not logged in, go to home page
    // If logged in, stay on current page (do nothing)
    if (!isAuthenticated) {
      navigate('/');
    }
  };
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-500">
      {/* Navigation */}
      <nav className="backdrop-blur-sm bg-white/60 border-b border-white/20">
        <div className="max-w-6xl mx-auto px-6">
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
            <div className="flex items-center space-x-4">
              <Link
                to="/login"
                className="text-gray-700 hover:text-blue-600 font-medium text-sm transition-colors px-3 py-2"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="bg-black text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-800 transition-all"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-16">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h1 className="text-4xl font-bold text-black mb-4 drop-shadow-sm">
            Seamlessly Transform Your Data
          </h1>
          <p className="text-lg text-black mb-8 max-w-2xl mx-auto drop-shadow-sm">
            Upload your files and instantly augment your data. Generate larger training datasets in multiple formats with ease, and boost your workflow in just a few clicks
          </p>
          <div className="flex justify-center">
            <Link
              to="/register"
              className="backdrop-blur-sm bg-white/40 text-gray-900 px-8 py-3 rounded-xl font-semibold hover:bg-white/50 transition-all duration-200 border border-white/20"
            >
              Start Processing Data
            </Link>
          </div>
        </div>
      </section>

      {/* Simple Features */}
      <section className="py-8">
        <div className="max-w-5xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="backdrop-blur-sm bg-white/40 rounded-lg p-4 text-center">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center mx-auto mb-3">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <h3 className="text-sm font-semibold text-gray-900 mb-1">Upload</h3>
              <p className="text-xs text-gray-600">Drop your files and we'll handle the rest</p>
            </div>

            <div className="backdrop-blur-sm bg-white/40 rounded-lg p-4 text-center">
              <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg flex items-center justify-center mx-auto mb-3">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-sm font-semibold text-gray-900 mb-1">Process</h3>
              <p className="text-xs text-gray-600">Secure data processing and transformation</p>
            </div>

            <div className="backdrop-blur-sm bg-white/40 rounded-lg p-4 text-center">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center mx-auto mb-3">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-sm font-semibold text-gray-900 mb-1">Augment</h3>
              <p className="text-xs text-gray-600">Get augmented data with your customization</p>
            </div>
          </div>
        </div>
      </section>

      {/* Simple About Section */}
      <section className="py-8 text-center">
        <div className="max-w-3xl mx-auto px-6">
          <p className="text-black text-sm leading-relaxed drop-shadow-sm">
            DataVein is built for users who need reliable data augmentation without complexity. Making it effortless to expand and enhance datasets.
            Whether you're working with production data, conducting research, or preparing for a student hackathon demo, augmentation is fast and stress free.
          </p>
          <p className="text-black text-sm font-medium mt-2 drop-shadow-sm">
            <span className="font-medium">Upload → Process → Augment</span> - it's that simple.
          </p>
        </div>
      </section>
    </div>
  );
};

export default Home;