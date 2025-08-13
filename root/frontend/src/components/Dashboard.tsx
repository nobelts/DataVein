import { useState, useEffect } from 'react';
import { useAuth } from '../useAuth';
import { apiClient, UploadResponse, Pipeline } from '../api';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [uploads, setUploads] = useState<UploadResponse[]>([]);
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [uploadsData, pipelinesData] = await Promise.all([
          apiClient.getUploads(),
          apiClient.getPipelines(),
        ]);
        setUploads(uploadsData);
        setPipelines(pipelinesData);
      } catch (error: any) {
        setError('Failed to load dashboard data');
        console.error('Dashboard error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleLogout = () => {
    logout();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-lg">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">Welcome, {user?.full_name}</span>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Link
              to="/augmentation"
              className="relative group bg-white p-6 border border-gray-300 rounded-lg hover:border-green-500 hover:shadow-md transition-all"
            >
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-10 w-10 rounded-md bg-green-500 text-white">
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-medium text-gray-900 group-hover:text-green-600">
                    Data Augmentation
                  </h3>
                  <p className="text-sm text-gray-500">Generate synthetic data using AI methods</p>
                </div>
              </div>
            </Link>

            <Link
              to="/pipelines"
              className="relative group bg-white p-6 border border-gray-300 rounded-lg hover:border-indigo-500 hover:shadow-md transition-all"
            >
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-10 w-10 rounded-md bg-indigo-500 text-white">
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-medium text-gray-900 group-hover:text-indigo-600">
                    Manage Pipelines
                  </h3>
                  <p className="text-sm text-gray-500">Create and manage data processing pipelines</p>
                </div>
              </div>
            </Link>
          </div>
        </div>

        {/* Recent Uploads */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-medium text-gray-900">Recent Uploads</h2>
            <Link
              to="/upload"
              className="text-sm text-indigo-600 hover:text-indigo-500"
            >
              View all uploads
            </Link>
          </div>
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            {uploads.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                No uploads yet. <Link to="/upload" className="text-indigo-600 hover:text-indigo-500">Upload your first file</Link>
              </div>
            ) : (
              <ul className="divide-y divide-gray-200">
                {uploads.slice(0, 5).map((upload) => (
                  <li key={upload.id} className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center">
                            <svg className="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          </div>
                        </div>
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-900">{upload.filename}</p>
                          <p className="text-sm text-gray-500">
                            {new Date(upload.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          upload.status === 'completed' ? 'bg-green-100 text-green-800' :
                          upload.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                          upload.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {upload.status}
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Recent Pipelines */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-medium text-gray-900">Recent Pipelines</h2>
            <Link
              to="/pipelines"
              className="text-sm text-indigo-600 hover:text-indigo-500"
            >
              View all pipelines
            </Link>
          </div>
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            {pipelines.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                No pipelines yet. <Link to="/pipelines" className="text-indigo-600 hover:text-indigo-500">Create your first pipeline</Link>
              </div>
            ) : (
              <ul className="divide-y divide-gray-200">
                {pipelines.slice(0, 5).map((pipeline) => (
                  <li key={pipeline.id} className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center">
                            <svg className="h-4 w-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                            </svg>
                          </div>
                        </div>
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-900">Pipeline {pipeline.id.slice(0, 8)}</p>
                          <p className="text-sm text-gray-500">Data processing pipeline</p>
                          {pipeline.status === 'running' && (
                            <div className="mt-2">
                              <div className="flex items-center text-xs text-blue-600">
                                <span>Processing...</span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                                <div className="bg-blue-600 h-1.5 rounded-full animate-pulse" style={{width: '60%'}}></div>
                              </div>
                            </div>
                          )}
                          {pipeline.status === 'completed' && (
                            <div className="mt-1 text-xs text-green-600">
                              ✓ Pipeline completed successfully
                            </div>
                          )}
                          {pipeline.status === 'failed' && (
                            <div className="mt-1 text-xs text-red-600">
                              ✗ Pipeline failed
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          pipeline.status === 'completed' ? 'bg-green-100 text-green-800' :
                          pipeline.status === 'running' ? 'bg-yellow-100 text-yellow-800' :
                          pipeline.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {pipeline.status}
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
