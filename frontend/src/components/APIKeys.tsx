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
          <h1 className="text-3xl font-bold text-white">API Keys</h1>
          <p className="text-gray-300 mt-1">Manage authentication keys for API access</p>
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
        <div className="card bg-green-900/30 border-green-700 mb-6">
          <div className="flex items-start space-x-3">
            <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-medium text-green-200 mb-2">
                API Key Generated Successfully!
              </h3>
              <p className="text-sm text-green-300 mb-3">
                Copy this key now — it won't be shown again.
              </p>
              <div className="flex items-center space-x-2">
                <code className="flex-1 px-3 py-2 bg-gray-900 border border-green-700 rounded text-sm font-mono break-all text-green-200">
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
          <h3 className="text-lg font-semibold text-white mb-4">Generate New API Key</h3>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-200 mb-2">
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
              <p className="mt-2 text-sm text-gray-400">
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
        <h2 className="text-lg font-semibold text-white mb-4">Your API Keys</h2>
        
        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : !keys || keys.length === 0 ? (
          <div className="text-center py-8">
            <KeyIcon className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-300">No API keys yet</p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="mt-4 text-blue-400 hover:text-blue-300 text-sm font-medium"
            >
              Generate your first key
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {keys.map((key) => (
              <div
                key={key.id}
                className="flex items-center justify-between p-4 border border-gray-700 rounded-lg hover:bg-gray-750"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <KeyIcon className="w-4 h-4 text-gray-500" />
                    <div>
                      <h3 className="font-medium text-white">{key.name}</h3>
                      <div className="flex items-center space-x-2 mt-1">
                        <code className="text-xs font-mono text-gray-300 bg-gray-900 px-2 py-1 rounded">
                          {key.prefix}••••••••
                        </code>
                        <span className="text-xs text-gray-400">
                          Created {new Date(key.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {key.is_active ? (
                    <span className="px-2 py-1 text-xs font-semibold bg-green-900/50 text-green-300 rounded-full">
                      Active
                    </span>
                  ) : (
                    <span className="px-2 py-1 text-xs font-semibold bg-gray-700 text-gray-300 rounded-full">
                      Inactive
                    </span>
                  )}
                  <button
                    onClick={() => handleRevoke(key.id, key.name)}
                    className="p-2 text-red-400 hover:bg-red-900/30 rounded"
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
      <div className="mt-6 card bg-blue-900/30 border-blue-700">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-200">
            <p className="font-medium mb-1">Security Best Practices</p>
            <ul className="list-disc list-inside space-y-1 text-blue-300">
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
