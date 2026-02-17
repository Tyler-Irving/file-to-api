import { useState } from 'react';
import type { Dataset } from '../types';
import { Code2, Copy, CheckCircle } from 'lucide-react';
import { cn } from '../utils/cn';

interface APIExplorerProps {
  dataset: Dataset;
}

interface Endpoint {
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  path: string;
  description: string;
  exampleCurl: string;
  exampleBody?: string;
}

export default function APIExplorer({ dataset }: APIExplorerProps) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const baseUrl = dataset.api_url.replace(/\/$/, '');
  const apiKey = localStorage.getItem('api_key') || 'your_api_key_here';

  const endpoints: Endpoint[] = [
    {
      method: 'GET',
      path: `${baseUrl}/`,
      description: 'List all records (paginated)',
      exampleCurl: `curl -X GET "${baseUrl}/?page=1&page_size=25" \\
  -H "Authorization: Api-Key ${apiKey}"`,
    },
    {
      method: 'POST',
      path: `${baseUrl}/`,
      description: 'Create a new record',
      exampleCurl: `curl -X POST "${baseUrl}/" \\
  -H "Authorization: Api-Key ${apiKey}" \\
  -H "Content-Type: application/json" \\
  -d '${JSON.stringify(
    dataset.columns.reduce((acc, col) => {
      acc[col.field_name] = col.data_type === 'integer' ? 123 : 
                            col.data_type === 'float' ? 45.67 :
                            col.data_type === 'boolean' ? true :
                            'example_value';
      return acc;
    }, {} as Record<string, any>),
    null,
    2
  )}'`,
      exampleBody: JSON.stringify(
        dataset.columns.reduce((acc, col) => {
          acc[col.field_name] = col.data_type === 'integer' ? 123 : 
                                col.data_type === 'float' ? 45.67 :
                                col.data_type === 'boolean' ? true :
                                'example_value';
          return acc;
        }, {} as Record<string, any>),
        null,
        2
      ),
    },
    {
      method: 'GET',
      path: `${baseUrl}/{id}/`,
      description: 'Get a specific record by ID',
      exampleCurl: `curl -X GET "${baseUrl}/1/" \\
  -H "Authorization: Api-Key ${apiKey}"`,
    },
    {
      method: 'PUT',
      path: `${baseUrl}/{id}/`,
      description: 'Update a record (full replacement)',
      exampleCurl: `curl -X PUT "${baseUrl}/1/" \\
  -H "Authorization: Api-Key ${apiKey}" \\
  -H "Content-Type: application/json" \\
  -d '${JSON.stringify(
    dataset.columns.reduce((acc, col) => {
      acc[col.field_name] = col.data_type === 'integer' ? 456 : 
                            col.data_type === 'float' ? 78.90 :
                            col.data_type === 'boolean' ? false :
                            'updated_value';
      return acc;
    }, {} as Record<string, any>),
    null,
    2
  )}'`,
    },
    {
      method: 'PATCH',
      path: `${baseUrl}/{id}/`,
      description: 'Partially update a record',
      exampleCurl: `curl -X PATCH "${baseUrl}/1/" \\
  -H "Authorization: Api-Key ${apiKey}" \\
  -H "Content-Type: application/json" \\
  -d '{"${dataset.columns[0]?.field_name || 'field'}": "new_value"}'`,
    },
    {
      method: 'DELETE',
      path: `${baseUrl}/{id}/`,
      description: 'Delete a record',
      exampleCurl: `curl -X DELETE "${baseUrl}/1/" \\
  -H "Authorization: Api-Key ${apiKey}"`,
    },
  ];

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const getMethodColor = (method: string) => {
    const colors = {
      GET: 'bg-blue-100 text-blue-800',
      POST: 'bg-green-100 text-green-800',
      PUT: 'bg-yellow-100 text-yellow-800',
      PATCH: 'bg-orange-100 text-orange-800',
      DELETE: 'bg-red-100 text-red-800',
    };
    return colors[method as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="card">
      <div className="flex items-center space-x-2 mb-6">
        <Code2 className="w-5 h-5 text-gray-600" />
        <h2 className="text-xl font-semibold text-gray-900">API Explorer</h2>
      </div>

      <div className="space-y-6">
        {endpoints.map((endpoint, index) => (
          <div key={index} className="border border-gray-200 rounded-lg overflow-hidden">
            {/* Header */}
            <div className="bg-gray-50 px-4 py-3 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span
                  className={cn(
                    'px-2 py-1 text-xs font-bold rounded',
                    getMethodColor(endpoint.method)
                  )}
                >
                  {endpoint.method}
                </span>
                <code className="text-sm font-mono text-gray-900">
                  {endpoint.path}
                </code>
              </div>
            </div>

            {/* Description */}
            <div className="px-4 py-3 bg-white border-b border-gray-200">
              <p className="text-sm text-gray-700">{endpoint.description}</p>
            </div>

            {/* Code Example */}
            <div className="relative">
              <div className="absolute top-2 right-2 z-10">
                <button
                  onClick={() => copyToClipboard(endpoint.exampleCurl, index)}
                  className="p-2 bg-gray-700 hover:bg-gray-600 rounded text-white"
                  title="Copy to clipboard"
                >
                  {copiedIndex === index ? (
                    <CheckCircle className="w-4 h-4" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
              </div>
              <pre className="bg-gray-900 text-gray-100 px-4 py-4 overflow-x-auto text-sm">
                <code>{endpoint.exampleCurl}</code>
              </pre>
            </div>

            {/* Request Body Example */}
            {endpoint.exampleBody && (
              <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
                <p className="text-xs font-medium text-gray-600 mb-2">Request Body:</p>
                <pre className="bg-white border border-gray-200 rounded px-3 py-2 text-xs overflow-x-auto">
                  <code>{endpoint.exampleBody}</code>
                </pre>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Additional Info */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h3 className="font-medium text-blue-900 mb-2">Query Parameters</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li><code className="bg-blue-100 px-1 rounded">?page=1</code> — Page number (default: 1)</li>
          <li><code className="bg-blue-100 px-1 rounded">?page_size=25</code> — Results per page (default: 25, max: 100)</li>
          <li><code className="bg-blue-100 px-1 rounded">?ordering=field_name</code> — Sort by field (prefix with <code>-</code> for descending)</li>
          <li><code className="bg-blue-100 px-1 rounded">?field_name=value</code> — Filter by exact match</li>
        </ul>
      </div>
    </div>
  );
}
