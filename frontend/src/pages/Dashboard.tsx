import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Globe, Trash2 } from 'lucide-react';
import { sitesAPI } from '../services/api';

interface Site {
  id: string;
  site_name: string;
  domain: string;
  site_key: string;
  is_verified: boolean;
  is_active: boolean;
  model_provider: string;
  model_name: string;
  created_at: string;
}

export default function Dashboard() {
  const [sites, setSites] = useState<Site[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [newSiteName, setNewSiteName] = useState('');
  const [newDomain, setNewDomain] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadSites();
  }, []);

  const loadSites = async () => {
    try {
      const res = await sitesAPI.list();
      setSites(res.data);
    } catch (err) {
      console.error('Failed to load sites', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSite = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await sitesAPI.create({ site_name: newSiteName, domain: newDomain });
      setNewSiteName('');
      setNewDomain('');
      setShowCreate(false);
      loadSites();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create site');
    }
  };

  const handleDeleteSite = async (id: string) => {
    if (!confirm('Are you sure you want to delete this site? This will remove all documents and chat history.')) return;
    try {
      await sitesAPI.delete(id);
      loadSites();
    } catch (err) {
      alert('Failed to delete site');
    }
  };

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Your Sites</h1>
          <p className="text-gray-500 mt-1">Manage your website chatbots</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus size={18} />
          Add Site
        </button>
      </div>

      {/* Create Site Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-4">Register New Site</h3>
            <form onSubmit={handleCreateSite} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Site Name</label>
                <input
                  type="text"
                  value={newSiteName}
                  onChange={(e) => setNewSiteName(e.target.value)}
                  placeholder="My Website"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Domain</label>
                <input
                  type="text"
                  value={newDomain}
                  onChange={(e) => setNewDomain(e.target.value)}
                  placeholder="example.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                  required
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowCreate(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Sites Grid */}
      {sites.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-gray-200">
          <Globe size={48} className="mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-600">No sites yet</h3>
          <p className="text-gray-400 mt-1">Add your first website to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sites.map((site) => (
            <div
              key={site.id}
              className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => navigate(`/sites/${site.id}`)}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{site.site_name}</h3>
                  <p className="text-sm text-gray-500 mt-1">{site.domain}</p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${site.is_verified ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                  {site.is_verified ? 'Verified' : 'Pending'}
                </span>
              </div>
              <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
                <span>{site.model_provider} / {site.model_name}</span>
                <button
                  onClick={(e) => { e.stopPropagation(); handleDeleteSite(site.id); }}
                  className="text-red-400 hover:text-red-600 p-1"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
