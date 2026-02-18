import { useQuery } from '@tanstack/react-query';
import { useParams, Link } from 'react-router-dom';
import { datasetsApi } from '../api/datasets';
import { Loader2, AlertCircle, ArrowLeft, FileJson, Code } from 'lucide-react';
import APIExplorer from './APIExplorer';
import SchemaTable from './SchemaTable';

export default function DatasetDetail() {
  const { slug } = useParams<{ slug: string }>();

  const { data: dataset, isLoading, error } = useQuery({
    queryKey: ['dataset', slug],
    queryFn: () => datasetsApi.get(slug!),
    enabled: !!slug,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  if (error || !dataset) {
    return (
      <div className="card">
        <div className="flex items-center space-x-2 text-red-400">
          <AlertCircle className="w-5 h-5" />
          <p>Failed to load dataset</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Link
          to="/"
          className="inline-flex items-center text-sm text-gray-300 hover:text-white mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to datasets
        </Link>
        
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">{dataset.name}</h1>
            <p className="text-gray-300 mt-1">{dataset.original_filename}</p>
            <div className="flex items-center space-x-4 mt-2 text-sm text-gray-400">
              <span>{dataset.row_count.toLocaleString()} rows</span>
              <span>•</span>
              <span>{dataset.columns.length} columns</span>
              <span>•</span>
              <span>Created {new Date(dataset.created_at).toLocaleDateString()}</span>
            </div>
          </div>
          
          <span
            className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${
              dataset.status === 'ready'
                ? 'bg-green-900/50 text-green-300'
                : dataset.status === 'processing'
                ? 'bg-yellow-900/50 text-yellow-300'
                : 'bg-red-900/50 text-red-300'
            }`}
          >
            {dataset.status}
          </span>
        </div>
      </div>

      {/* Error Message */}
      {dataset.status === 'error' && dataset.error_message && (
        <div className="card bg-red-900/30 border-red-700">
          <div className="flex items-start space-x-2">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-medium text-red-200">Processing Error</h3>
              <p className="text-sm text-red-300 mt-1">{dataset.error_message}</p>
            </div>
          </div>
        </div>
      )}

      {/* API Info */}
      {dataset.status === 'ready' && (
        <div className="card bg-blue-900/30 border-blue-700">
          <div className="flex items-start space-x-3">
            <FileJson className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-medium text-blue-200 mb-2">Your API is Ready!</h3>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="text-blue-300 font-medium">Base URL:</span>
                  <code className="ml-2 px-2 py-1 bg-gray-900 rounded border border-blue-800 text-blue-200">
                    {dataset.api_url}
                  </code>
                </div>
                <div>
                  <span className="text-blue-300 font-medium">Docs:</span>
                  <a
                    href={dataset.docs_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-2 text-blue-400 hover:text-blue-300 underline"
                  >
                    View OpenAPI Documentation
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Schema */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <Code className="w-5 h-5 text-gray-400" />
          <h2 className="text-xl font-semibold text-white">Schema</h2>
        </div>
        <SchemaTable columns={dataset.columns} />
      </div>

      {/* API Explorer */}
      {dataset.status === 'ready' && (
        <APIExplorer dataset={dataset} />
      )}
    </div>
  );
}
