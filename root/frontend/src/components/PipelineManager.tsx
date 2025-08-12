import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient, Pipeline, UploadResponse, PipelineConfig } from '../api';

const PipelineManager = () => {
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [uploads, setUploads] = useState<UploadResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedUpload, setSelectedUpload] = useState<string>('');
  const [config, setConfig] = useState<PipelineConfig>({
    synthetic_multiplier: 1,
    include_nulls: false,
  });
  const [creating, setCreating] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [pipelinesData, uploadsData] = await Promise.all([
          apiClient.getPipelines(),
          apiClient.getUploads(),
        ]);
        setPipelines(pipelinesData);
        setUploads(uploadsData.filter(upload => upload.status === 'completed'));
      } catch (error: any) {
        setError('Failed to load pipeline data');
        console.error('Pipeline manager error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleCreatePipeline = async () => {
    if (!selectedUpload) {
      setError('Please select an upload to create a pipeline');
      return;
    }

    setCreating(true);
    setError('');

    try {
      const newPipeline = await apiClient.startPipeline({
        upload_id: selectedUpload,
        config,
      });

      setPipelines(prev => [newPipeline, ...prev]);
      setShowCreateForm(false);
      setSelectedUpload('');
      setConfig({ synthetic_multiplier: 1, include_nulls: false });
    } catch (error: any) {
      setError('Failed to create pipeline');
      console.error('Create pipeline error:', error);
    } finally {
      setCreating(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'running':
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-lg">Loading pipelines...</div>
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
              <button
                onClick={() => navigate('/dashboard')}
                className="mr-4 text-gray-600 hover:text-gray-900"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <h1 className="text-2xl font-bold text-gray-900">Pipeline Manager</h1>
            </div>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Create Pipeline
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Create Pipeline Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Pipeline</h3>
                
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Upload
                  </label>
                  <select
                    value={selectedUpload}
                    onChange={(e) => setSelectedUpload(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">Choose an upload...</option>
                    {uploads.map((upload) => (
                      <option key={upload.id} value={upload.id}>
                        {upload.filename}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Synthetic Multiplier
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={config.synthetic_multiplier}
                    onChange={(e) => setConfig({ ...config, synthetic_multiplier: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    Number of synthetic records to generate per original record
                  </p>
                </div>

                <div className="mb-6">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={config.include_nulls}
                      onChange={(e) => setConfig({ ...config, include_nulls: e.target.checked })}
                      className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">Include null values in synthetic data</span>
                  </label>
                </div>

                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => setShowCreateForm(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleCreatePipeline}
                    disabled={creating || !selectedUpload}
                    className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-md"
                  >
                    {creating ? 'Creating...' : 'Create Pipeline'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Pipelines List */}
        <div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-medium text-gray-900">All Pipelines</h2>
          </div>

          {pipelines.length === 0 ? (
            <div className="bg-white shadow rounded-lg p-6 text-center">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No pipelines</h3>
              <p className="mt-1 text-sm text-gray-500">Get started by creating your first pipeline.</p>
              <div className="mt-6">
                <button
                  onClick={() => setShowCreateForm(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  Create Pipeline
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {pipelines.map((pipeline) => (
                  <li key={pipeline.id} className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                            <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                            </svg>
                          </div>
                        </div>
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-900">Pipeline {pipeline.id.slice(0, 8)}</p>
                          <p className="text-sm text-gray-500">Data processing pipeline</p>
                          <p className="text-xs text-gray-400 mt-1">
                            Created: {new Date(pipeline.created_at).toLocaleString()}
                          </p>
                          {pipeline.config && (
                            <div className="text-xs text-gray-500 mt-1">
                              Multiplier: {pipeline.config.synthetic_multiplier || 1}, 
                              Include nulls: {pipeline.config.include_nulls ? 'Yes' : 'No'}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(pipeline.status)}`}>
                          {pipeline.status}
                        </span>
                        <button
                          onClick={() => {/* Handle view pipeline details */}}
                          className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
                        >
                          View Details
                        </button>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default PipelineManager;
