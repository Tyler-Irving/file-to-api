import { useState, useCallback } from 'react';
import { Upload, FileSpreadsheet, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import { datasetsApi } from '../api/datasets';
import { useNavigate } from 'react-router-dom';
import { cn } from '../utils/cn';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_TYPES = [
  'text/csv',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
];

export default function FileUpload() {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string>('');
  const [datasetName, setDatasetName] = useState('');
  const navigate = useNavigate();

  const uploadMutation = useMutation({
    mutationFn: (data: { file: File; name?: string }) =>
      datasetsApi.upload(data.file, data.name),
    onSuccess: (dataset: any) => {
      // Store API key if this is a new upload (first time)
      // Backend returns 'api_key' field for new uploads
      console.log('Upload response:', dataset);
      console.log('API key from response:', dataset.api_key);
      
      if (dataset.api_key) {
        localStorage.setItem('api_key', dataset.api_key);
        console.log('Stored API key in localStorage');
        
        // Give localStorage time to flush and interceptor to pick it up
        setTimeout(() => {
          console.log('Navigating to dataset detail...');
          navigate(`/datasets/${dataset.slug}`);
        }, 100);
      } else {
        console.error('No API key in response!');
        navigate(`/datasets/${dataset.slug}`);
      }
    },
    onError: (error: any) => {
      setError(error.response?.data?.message || 'Failed to upload file');
    },
  });

  const validateFile = (file: File): string | null => {
    if (file.size > MAX_FILE_SIZE) {
      return 'File size must be less than 10MB';
    }
    
    if (!ALLOWED_TYPES.includes(file.type) && 
        !file.name.match(/\.(csv|xlsx|xls)$/i)) {
      return 'Only CSV and Excel files are supported';
    }
    
    return null;
  };

  const handleFile = (selectedFile: File) => {
    const validationError = validateFile(selectedFile);
    
    if (validationError) {
      setError(validationError);
      setFile(null);
      return;
    }
    
    setFile(selectedFile);
    setError('');
    
    // Auto-set dataset name from filename
    if (!datasetName) {
      const name = selectedFile.name.replace(/\.(csv|xlsx|xls)$/i, '');
      setDatasetName(name);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFile(droppedFile);
    }
  }, [datasetName]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      handleFile(selectedFile);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }
    
    uploadMutation.mutate({
      file,
      name: datasetName || undefined,
    });
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-white mb-2">Upload Dataset</h1>
      <p className="text-gray-300 mb-8">
        Upload a CSV or Excel file to generate a REST API instantly
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Drag & Drop Zone */}
        <div
          className={cn(
            'border-2 border-dashed rounded-lg p-12 text-center transition-colors',
            isDragging
              ? 'border-blue-500 bg-blue-900/20'
              : file
              ? 'border-green-500 bg-green-900/20'
              : 'border-gray-600 hover:border-gray-500 bg-gray-800/50'
          )}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          {file ? (
            <div className="flex flex-col items-center space-y-2">
              <CheckCircle2 className="w-12 h-12 text-green-500" />
              <div className="flex items-center space-x-2">
                <FileSpreadsheet className="w-5 h-5 text-green-500" />
                <span className="font-medium text-white">{file.name}</span>
              </div>
              <span className="text-sm text-gray-400">
                {(file.size / 1024).toFixed(2)} KB
              </span>
              <button
                type="button"
                onClick={() => setFile(null)}
                className="text-sm text-blue-400 hover:text-blue-300"
              >
                Choose a different file
              </button>
            </div>
          ) : (
            <>
              <Upload className={cn(
                'w-12 h-12 mx-auto mb-4',
                isDragging ? 'text-blue-500' : 'text-gray-500'
              )} />
              <p className="text-lg font-medium text-white mb-2">
                Drop your file here, or{' '}
                <label className="text-blue-400 hover:text-blue-300 cursor-pointer">
                  browse
                  <input
                    type="file"
                    className="hidden"
                    accept=".csv,.xlsx,.xls"
                    onChange={handleFileInput}
                  />
                </label>
              </p>
              <p className="text-sm text-gray-400">
                CSV or Excel files up to 10MB
              </p>
            </>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="flex items-center space-x-2 p-4 bg-red-900/30 border border-red-700 rounded-md">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
            <p className="text-sm text-red-200">{error}</p>
          </div>
        )}

        {/* Dataset Name Input */}
        {file && (
          <div>
            <label className="block text-sm font-medium text-gray-200 mb-2">
              Dataset Name (optional)
            </label>
            <input
              type="text"
              value={datasetName}
              onChange={(e) => setDatasetName(e.target.value)}
              placeholder="Leave blank to use filename"
              className="input"
            />
            <p className="mt-2 text-sm text-gray-400">
              A URL-friendly slug will be auto-generated for the API
            </p>
          </div>
        )}

        {/* Submit Button */}
        {file && (
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => {
                setFile(null);
                setDatasetName('');
                setError('');
              }}
              className="btn btn-secondary"
              disabled={uploadMutation.isPending}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={uploadMutation.isPending}
            >
              {uploadMutation.isPending ? 'Uploading...' : 'Upload & Create API'}
            </button>
          </div>
        )}
      </form>
    </div>
  );
}
