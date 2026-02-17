import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { keysApi } from '../api/keys';
import { Plus, Trash2, Copy, CheckCircle, Key as KeyIcon, AlertCircle } from 'lucide-react';

export default function APIKeys() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [generatedKey, setGeneratedKey] = useState<string | null>(null);
  const [copiedKey, setCopiedKey] = useState(false);
  const queryClient = useQueryClient();

  const { data: keys, isLoading } = useQuery({
    queryKey: ['api-keys'],
    queryFn: keysApi.list,
  });

  const generateMutation = useMutation({
    mutationFn: keysApi.generate,
    onSuccess: (data) => {
      setGeneratedKey(data.full_key || null);
      setNewKeyName('');
      setShowCreateForm(false);
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
      
      // Save the first key as the active key
      if (data.full_key && !localStorage.getItem('api_key')) {
        localStorage.setItem('api_key', data.full_key);
      }
    },
  });

  const revokeMutation = useMutation({
    mutationFn: keysApi.revoke,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
    },
  });

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    if (newKeyName.trim()) {
      generateMutation.mutate(newKeyName.trim());
    }
  };

  const handleRevoke = (id: string, name: string) => {
    if (confirm(`Are you sure you want to revoke the key "${name}"? This cannot be undone.`)) {
      revokeMutation.mutate(id);
    }
  };

  const copyKey = (key: string) => {
    navigator.clipboard.writeText(key);
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2000);
  };

  const useKey = (key: string) => {
    localStorage.setItem('api_key', key);
    alert('API key activated! It will be used for all API requests.');
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">API Keys</h1>
          <p className="text-gray-600 mt-1">Manage authentication keys for API access</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="btn btn-primary inline-flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Generate Key</span>
        </button>
      </div>

      {/* Generated Key Alert */}
      {generatedKey && (
        <div className="card bg-green-50 border-green-200 mb-6">
          <div className="flex items-start space-x-3">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-medium text-green-900 mb-2">
                API Key Generated Successfully!
              </h3>
              <p className="text-sm text-green-800 mb-3">
                Copy this key now — it won't be shown again.
              </p>
              <div className="flex items-center space-x-2">
                <code className="flex-1 px-3 py-2 bg-white border border-green-300 rounded text-sm font-mono break-all">
                  {generatedKey}
                </code>
                <button
                  onClick={() => copyKey(generatedKey)}
                  className="btn btn-secondary flex-shrink-0"
                >
                  {copiedKey ? (
                    <CheckCircle className="w-4 h-4" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
                <button
                  onClick={() => useKey(generatedKey)}
                  className="btn btn-primary flex-shrink-0"
                >
                  Use This Key
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Form */}
      {showCreateForm && !generatedKey && (
        <div className="card mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Generate New API Key</h3>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Key Name
              </label>
              <input
                type="text"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                placeholder="e.g., Production API, Development Key"
                className="input"
                required
              />
              <p className="mt-2 text-sm text-gray-500">
                Choose a descriptive name to identify this key
              </p>
            </div>
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => {
                  setShowCreateForm(false);
                  setNewKeyName('');
                }}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={generateMutation.isPending}
              >
                {generateMutation.isPending ? 'Generating...' : 'Generate Key'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Keys List */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Your API Keys</h2>
        
        {isLoading ? (
          <p className="text-gray-500">Loading...</p>
        ) : !keys || keys.length === 0 ? (
          <div className="text-center py-8">
            <KeyIcon className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">No API keys yet</p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="mt-4 text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              Generate your first key
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {keys.map((key) => (
              <div
                key={key.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <KeyIcon className="w-4 h-4 text-gray-400" />
                    <div>
                      <h3 className="font-medium text-gray-900">{key.name}</h3>
                      <div className="flex items-center space-x-2 mt-1">
                        <code className="text-xs font-mono text-gray-600 bg-gray-100 px-2 py-1 rounded">
                          {key.prefix}••••••••
                        </code>
                        <span className="text-xs text-gray-500">
                          Created {new Date(key.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {key.is_active ? (
                    <span className="px-2 py-1 text-xs font-semibold bg-green-100 text-green-800 rounded-full">
                      Active
                    </span>
                  ) : (
                    <span className="px-2 py-1 text-xs font-semibold bg-gray-100 text-gray-800 rounded-full">
                      Inactive
                    </span>
                  )}
                  <button
                    onClick={() => handleRevoke(key.id, key.name)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded"
                    title="Revoke key"
                    disabled={revokeMutation.isPending}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Info Box */}
      <div className="mt-6 card bg-blue-50 border-blue-200">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-900">
            <p className="font-medium mb-1">Security Best Practices</p>
            <ul className="list-disc list-inside space-y-1 text-blue-800">
              <li>Keep your API keys secret — never commit them to version control</li>
              <li>Rotate keys periodically for better security</li>
              <li>Revoke unused keys immediately</li>
              <li>Use different keys for different environments (dev, staging, prod)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
