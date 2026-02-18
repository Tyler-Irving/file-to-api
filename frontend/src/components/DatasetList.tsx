import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { datasetsApi } from '../api/datasets';
import { Link } from 'react-router-dom';
import { Trash2, ExternalLink, Loader2, Database, AlertCircle, Plus } from 'lucide-react';
import type { Dataset } from '../types';

export default function DatasetList() {
  const queryClient = useQueryClient();

  const { data: datasets, isLoading, error } = useQuery({
    queryKey: ['datasets'],
    queryFn: datasetsApi.list,
  });

  const deleteMutation = useMutation({
    mutationFn: datasetsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] });
    },
  });

  const handleDelete = (slug: string, name: string) => {
    if (confirm(`Are you sure you want to delete "${name}"? This cannot be undone.`)) {
      deleteMutation.mutate(slug);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="flex items-center space-x-2 text-red-400">
          <AlertCircle className="w-5 h-5" />
          <p>Failed to load datasets</p>
        </div>
      </div>
    );
  }

  if (!datasets || datasets.length === 0) {
    return (
      <div className="text-center py-12">
        <Database className="w-16 h-16 text-gray-600 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-white mb-2">No datasets yet</h2>
        <p className="text-gray-300 mb-6">
          Upload your first CSV or Excel file to get started
        </p>
        <Link to="/upload" className="btn btn-primary inline-flex items-center space-x-2">
          <Plus className="w-4 h-4" />
          <span>Upload Dataset</span>
        </Link>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white">Datasets</h1>
          <p className="text-gray-300 mt-1">{datasets.length} dataset(s)</p>
        </div>
        <Link to="/upload" className="btn btn-primary inline-flex items-center space-x-2">
          <Plus className="w-4 h-4" />
          <span>Upload New</span>
        </Link>
      </div>

      <div className="bg-gray-800 rounded-lg shadow-lg border border-gray-700 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-700">
          <thead className="bg-gray-750">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Rows
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Columns
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Created
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-gray-800 divide-y divide-gray-700">
            {datasets.map((dataset: Dataset) => (
              <tr key={dataset.id} className="hover:bg-gray-750">
                <td className="px-6 py-4 whitespace-nowrap">
                  <Link
                    to={`/datasets/${dataset.slug}`}
                    className="text-blue-400 hover:text-blue-300 font-medium"
                  >
                    {dataset.name}
                  </Link>
                  <div className="text-sm text-gray-400">{dataset.original_filename}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-200">
                  {dataset.row_count.toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-200">
                  {dataset.columns?.length || 0}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      dataset.status === 'ready'
                        ? 'bg-green-900/50 text-green-300'
                        : dataset.status === 'processing'
                        ? 'bg-yellow-900/50 text-yellow-300'
                        : 'bg-red-900/50 text-red-300'
                    }`}
                  >
                    {dataset.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                  {new Date(dataset.created_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex items-center justify-end space-x-2">
                    <Link
                      to={`/datasets/${dataset.slug}`}
                      className="text-blue-400 hover:text-blue-300"
                      title="View details"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </Link>
                    <button
                      onClick={() => handleDelete(dataset.slug, dataset.name)}
                      className="text-red-400 hover:text-red-300"
                      title="Delete dataset"
                      disabled={deleteMutation.isPending}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
