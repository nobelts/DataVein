import React, { useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Download, Settings, BarChart3, Clock, CheckCircle, AlertCircle, LogOut } from 'lucide-react';
import { useAuth } from '../useAuth';

interface AugmentationMethod {
  id: string;
  name: string;
  description: string;
}

interface ProgressData {
  step: string;
  percentage: number;
  message: string;
}

interface TaskInfo {
  task_id: string;
  filename: string;
  rows: number;
  columns: number;
  column_names: string[];
}

interface ResultInfo {
  total_rows: number;
  original_rows: number;
  generated_rows: number;
}

const DataAugmentation: React.FC = () => {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskInfo, setTaskInfo] = useState<TaskInfo | null>(null);
  const [selectedMethod, setSelectedMethod] = useState<string>('noise_injection');
  const [targetSize, setTargetSize] = useState<number | null>(null);
  const [noiseLevel, setNoiseLevel] = useState<number>(0.1);
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [resultInfo, setResultInfo] = useState<ResultInfo | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isAugmenting, setIsAugmenting] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const progressIntervalRef = useRef<number | null>(null);

  const methods: AugmentationMethod[] = [
    {
      id: 'noise_injection',
      name: 'Noise Injection',
      description: 'Add Gaussian noise to numeric columns'
    },
    {
      id: 'bootstrap_sampling',
      name: 'Bootstrap Sampling',
      description: 'Create variations through resampling'
    },
    {
      id: 'interpolation',
      name: 'Interpolation',
      description: 'Generate synthetic rows by blending existing data'
    }
  ];

  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setProgress(null);
    setResultInfo(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/augmentation/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      setTaskId(data.task_id);
      setTaskInfo(data);
      setTargetSize(data.rows * 2); // Default to 2x the original size
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  }, []);

  const startAugmentation = useCallback(async () => {
    if (!taskId) return;

    setIsAugmenting(true);
    setProgress({ step: 'starting', percentage: 0, message: 'Starting augmentation...' });

    try {
      const formData = new FormData();
      formData.append('method', selectedMethod);
      if (targetSize) formData.append('target_size', targetSize.toString());
      formData.append('noise_level', noiseLevel.toString());

      const response = await fetch(`/api/augmentation/augment/${taskId}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Augmentation failed to start');
      }

      // Start polling for progress
      progressIntervalRef.current = setInterval(checkProgress, 1000);
    } catch (error) {
      console.error('Augmentation error:', error);
      alert('Augmentation failed to start. Please try again.');
      setIsAugmenting(false);
    }
  }, [taskId, selectedMethod, targetSize, noiseLevel]);

  const checkProgress = useCallback(async () => {
    if (!taskId) return;

    try {
      const response = await fetch(`/api/augmentation/progress/${taskId}`);
      if (!response.ok) return;

      const data = await response.json();
      setProgress(data.progress);

      if (data.result_info) {
        setResultInfo(data.result_info);
      }

      if (data.progress.step === 'completed' || data.progress.step === 'error') {
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current);
          progressIntervalRef.current = null;
        }
        setIsAugmenting(false);
      }
    } catch (error) {
      console.error('Progress check error:', error);
    }
  }, [taskId]);

  const downloadData = useCallback(async (format: 'csv' | 'parquet') => {
    if (!taskId) return;

    setIsDownloading(true);
    try {
      const response = await fetch(`/api/augmentation/download/${taskId}?format=${format}`);
      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `augmented_data_${taskId.slice(0, 8)}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download error:', error);
      alert('Download failed. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  }, [taskId]);

  const downloadViaPresignedUrl = useCallback(async (format: 'csv' | 'parquet') => {
    if (!taskId) return;

    try {
      const response = await fetch(`/api/augmentation/download-url/${taskId}?format=${format}`);
      if (!response.ok) {
        throw new Error('Failed to get download URL');
      }

      const { download_url } = await response.json();
      
      // Open presigned URL in new tab for download
      const a = document.createElement('a');
      a.href = download_url;
      a.download = `augmented_data_${taskId.slice(0, 8)}.${format}`;
      a.target = '_blank';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (error) {
      console.error('Presigned URL download error:', error);
      // Fallback to regular download
      downloadData(format);
    }
  }, [taskId, downloadData]);

  const getProgressIcon = () => {
    if (!progress) return <Clock className="w-5 h-5 text-gray-400" />;
    
    switch (progress.step) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />;
    }
  };

  const resetWorkflow = () => {
    setTaskId(null);
    setTaskInfo(null);
    setProgress(null);
    setResultInfo(null);
    setIsAugmenting(false);
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = null;
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleLogout = () => {
    logout();
    // Small delay to ensure logout completes before navigation
    setTimeout(() => {
      navigate('/');
    }, 100);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header with logout */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Data Augment</h1>
          <p className="text-gray-600">Select a file, pick your method, and expand your dataset</p>
        </div>
        <div className="flex flex-col items-end space-y-2">
          <button
            onClick={handleLogout}
            className="flex items-center bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </button>
          <span className="text-gray-600 text-sm">Welcome, {user?.email}</span>
        </div>
      </div>

      {/* Step 1: File Upload */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center mb-4">
          <Upload className="w-6 h-6 text-blue-600 mr-2" />
          <h2 className="text-xl font-semibold">Step 1: Upload Data</h2>
        </div>
        
        {!taskInfo ? (
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.tsv,.txt,.json,.xlsx,.xls,.parquet"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {isUploading ? 'Uploading...' : 'Choose Data File'}
            </button>
            <p className="text-gray-500 mt-2">Upload CSV, TSV, TXT, JSON, Excel, or Parquet files</p>
          </div>
        ) : (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold text-green-800">{taskInfo.filename}</h3>
                <p className="text-green-600">
                  {taskInfo.rows.toLocaleString()} rows × {taskInfo.columns} columns
                </p>
                <p className="text-sm text-green-600 mt-1">
                  Columns: {taskInfo.column_names.slice(0, 3).join(', ')}
                  {taskInfo.column_names.length > 3 && ` +${taskInfo.column_names.length - 3} more`}
                </p>
              </div>
              <button
                onClick={resetWorkflow}
                className="text-green-600 hover:text-green-800 text-sm underline"
              >
                Upload Different File
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Step 2: Configure Augmentation */}
      {taskInfo && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center mb-4">
            <Settings className="w-6 h-6 text-blue-600 mr-2" />
            <h2 className="text-xl font-semibold">Step 2: Configure Augmentation</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Augmentation Method
              </label>
              <div className="space-y-2">
                {methods.map((method) => (
                  <label key={method.id} className="flex items-start space-x-3 cursor-pointer">
                    <input
                      type="radio"
                      name="method"
                      value={method.id}
                      checked={selectedMethod === method.id}
                      onChange={(e) => setSelectedMethod(e.target.value)}
                      className="mt-1 text-blue-600"
                    />
                    <div>
                      <div className="font-medium text-gray-900">{method.name}</div>
                      <div className="text-sm text-gray-600">{method.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Dataset Size
                </label>
                <input
                  type="number"
                  value={targetSize || ''}
                  onChange={(e) => setTargetSize(parseInt(e.target.value) || null)}
                  placeholder={`Default: ${taskInfo.rows * 2}`}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-sm text-gray-500 mt-1">
                  Current: {taskInfo.rows.toLocaleString()} rows
                </p>
              </div>

              {selectedMethod === 'noise_injection' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Noise Level ({(noiseLevel * 100).toFixed(1)}%)
                  </label>
                  <input
                    type="range"
                    min="0.01"
                    max="0.5"
                    step="0.01"
                    value={noiseLevel}
                    onChange={(e) => setNoiseLevel(parseFloat(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>1%</span>
                    <span>50%</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="mt-6">
            <button
              onClick={startAugmentation}
              disabled={isAugmenting || !taskInfo}
              className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {isAugmenting ? 'Augmenting...' : 'Start Augmentation'}
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Progress Tracking */}
      {progress && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center mb-4">
            {getProgressIcon()}
            <h2 className="text-xl font-semibold ml-2">Progress</h2>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">
                  {progress.step.charAt(0).toUpperCase() + progress.step.slice(1)}
                </span>
                <span className="text-sm text-gray-600">{progress.percentage}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    progress.step === 'error' ? 'bg-red-500' : 
                    progress.step === 'completed' ? 'bg-green-500' : 'bg-blue-500'
                  }`}
                  style={{ width: `${progress.percentage}%` }}
                ></div>
              </div>
            </div>

            {progress.message && (
              <p className="text-sm text-gray-600">{progress.message}</p>
            )}

            {resultInfo && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <BarChart3 className="w-5 h-5 text-blue-600 mr-2" />
                  <h3 className="font-semibold text-blue-800">Results</h3>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <div className="text-blue-600 font-medium">Original Rows</div>
                    <div className="text-xl font-bold text-blue-800">
                      {resultInfo.original_rows.toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-blue-600 font-medium">Generated Rows</div>
                    <div className="text-xl font-bold text-blue-800">
                      {resultInfo.generated_rows.toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-blue-600 font-medium">Total Rows</div>
                    <div className="text-xl font-bold text-blue-800">
                      {resultInfo.total_rows.toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Step 4: Download Results */}
      {progress?.step === 'completed' && resultInfo && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center mb-4">
            <Download className="w-6 h-6 text-blue-600 mr-2" />
            <h2 className="text-xl font-semibold">Download Augmented Data</h2>
          </div>

          <div className="flex space-x-4">
            <button
              onClick={() => downloadData('csv')}
              disabled={isDownloading}
              className="bg-blue-800 text-white px-6 py-3 rounded-lg hover:bg-blue-900 disabled:opacity-50 flex items-center"
            >
              <Download className="w-4 h-4 mr-2" />
              Download CSV
            </button>
            <button
              onClick={() => downloadData('parquet')}
              disabled={isDownloading}
              className="bg-blue-800 text-white px-6 py-3 rounded-lg hover:bg-blue-900 disabled:opacity-50 flex items-center"
            >
              <Download className="w-4 h-4 mr-2" />
              Download Parquet
            </button>
          </div>

          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-2">Storage & Export Information</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Files are stored securely in MinIO object storage</li>
              <li>• CSV format: Human-readable, compatible with Excel and most tools</li>
              <li>• Parquet format: Efficient binary format, ideal for data processing pipelines</li>
              <li>• Download links are pre-signed and secure</li>
              <li>• Both formats contain the complete augmented dataset</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataAugmentation;
