import React, { useState, useCallback, useRef, useEffect } from 'react';
import './App.css';
import SearchPanel from './components/SearchPanel';
import LeadsTable from './components/LeadsTable';
import LeadDetail from './components/LeadDetail';
import Analytics from './components/Analytics';
import Navigation from './components/Navigation';

// Python bridge for Android/Chaquopy
const PythonBridge = {
  isAndroid: typeof window !== 'undefined' && window.Android !== undefined,

  send: async (action, params = {}) => {
    const message = JSON.stringify({ action, params });
    console.log('[Bridge] Sending:', action, params);

    if (PythonBridge.isAndroid && window.Android.bridge) {
      try {
        const response = await window.Android.bridge(message);
        const result = JSON.parse(response);
        console.log('[Bridge] Response:', result);
        return result;
      } catch (e) {
        console.error('[Bridge] Error:', e);
        return { success: false, error: e.message };
      }
    } else {
      // Mock response for development/web
      console.warn('[Bridge] Android not available, using mock response');
      return {
        success: true,
        message: 'Mock response (not on Android)',
        data: []
      };
    }
  }
};

function App() {
  const [leads, setLeads] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('search');
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  // Load leads from Python backend on mount
  useEffect(() => {
    loadLeads();
    loadStats();
  }, []);

  const loadLeads = useCallback(async () => {
    try {
      const response = await PythonBridge.send('get_leads');
      if (response.success) {
        setLeads(response.data || []);
      }
    } catch (e) {
      console.error('Error loading leads:', e);
    }
  }, []);

  const loadStats = useCallback(async () => {
    try {
      const response = await PythonBridge.send('get_stats');
      if (response.success) {
        setStats(response.data);
      }
    } catch (e) {
      console.error('Error loading stats:', e);
    }
  }, []);

  // Search operations
  const handleSearch = useCallback(async (searchType, searchParams) => {
    setLoading(true);
    setError(null);

    try {
      let action;
      switch (searchType) {
        case 'industry':
          action = 'search_industry';
          break;
        case 'company':
          action = 'search_company';
          break;
        case 'location':
          action = 'search_location';
          break;
        default:
          action = 'search_keywords';
      }

      const response = await PythonBridge.send(action, searchParams);

      if (response.success) {
        setSearchResults(response.data || []);
        setActiveTab('results');
      } else {
        setError(response.error || 'Search failed');
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Lead management
  const handleAddLead = useCallback(async (leadData) => {
    try {
      const response = await PythonBridge.send('add_lead', {
        lead_data: leadData
      });

      if (response.success) {
        setLeads([...leads, response.data.lead]);
        loadStats();
        return response.data.id;
      } else {
        setError(response.error || 'Failed to add lead');
        return null;
      }
    } catch (e) {
      setError(e.message);
      return null;
    }
  }, [leads, loadStats]);

  const handleUpdateLead = useCallback(async (leadId, updates) => {
    try {
      const response = await PythonBridge.send('update_lead', {
        lead_id: leadId,
        updates
      });

      if (response.success) {
        setLeads(leads.map(lead =>
          lead.id === leadId ? response.data : lead
        ));
        setSelectedLead(response.data);
        loadStats();
      } else {
        setError(response.error || 'Failed to update lead');
      }
    } catch (e) {
      setError(e.message);
    }
  }, [leads, loadStats]);

  const handleDeleteLead = useCallback(async (leadId) => {
    try {
      const response = await PythonBridge.send('delete_lead', {
        lead_id: leadId
      });

      if (response.success) {
        setLeads(leads.filter(lead => lead.id !== leadId));
        setSelectedLead(null);
        loadStats();
      } else {
        setError(response.error || 'Failed to delete lead');
      }
    } catch (e) {
      setError(e.message);
    }
  }, [leads, loadStats]);

  const handleImportResults = useCallback(async () => {
    // Add all search results to leads database
    const newLeads = [];
    for (const result of searchResults) {
      const id = await handleAddLead(result);
      if (id) {
        newLeads.push({ ...result, id });
      }
    }

    if (newLeads.length > 0) {
      setLeads([...leads, ...newLeads]);
      setSearchResults([]);
      setActiveTab('leads');
    }
  }, [searchResults, leads, handleAddLead]);

  const handleExport = useCallback(async (format) => {
    try {
      const response = await PythonBridge.send('export_leads', { format });
      if (response.success) {
        const data = response.data.export;
        const blob = new Blob([data], {
          type: format === 'json' ? 'application/json' : 'text/csv'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `leads.${format}`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (e) {
      setError(e.message);
    }
  }, []);

  return (
    <div className="app">
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />

      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      <div className="app-content">
        {activeTab === 'search' && (
          <SearchPanel
            onSearch={handleSearch}
            loading={loading}
          />
        )}

        {activeTab === 'results' && (
          <div className="results-panel">
            <div className="results-header">
              <h2>Search Results ({searchResults.length})</h2>
              {searchResults.length > 0 && (
                <button
                  className="btn btn-primary"
                  onClick={handleImportResults}
                  disabled={loading}
                >
                  Import All to Database
                </button>
              )}
            </div>
            <LeadsTable
              leads={searchResults}
              onSelectLead={setSelectedLead}
              onAddToDatabase={(lead) => handleAddLead(lead)}
            />
          </div>
        )}

        {activeTab === 'leads' && (
          <div className="leads-panel">
            <div className="leads-header">
              <h2>Lead Database ({leads.length})</h2>
              <div className="leads-actions">
                <button
                  className="btn btn-secondary"
                  onClick={() => handleExport('json')}
                >
                  Export JSON
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => handleExport('csv')}
                >
                  Export CSV
                </button>
              </div>
            </div>
            <LeadsTable
              leads={leads}
              onSelectLead={setSelectedLead}
              onDelete={handleDeleteLead}
              editable
            />
          </div>
        )}

        {activeTab === 'detail' && selectedLead && (
          <LeadDetail
            lead={selectedLead}
            onUpdate={handleUpdateLead}
            onDelete={handleDeleteLead}
            onClose={() => {
              setSelectedLead(null);
              setActiveTab('leads');
            }}
          />
        )}

        {activeTab === 'analytics' && (
          <Analytics
            stats={stats}
            leads={leads}
            onRefresh={loadStats}
          />
        )}
      </div>

      {selectedLead && activeTab !== 'detail' && (
        <div className="lead-preview">
          <div className="lead-preview-content">
            <h3>{selectedLead.company_name}</h3>
            <p>{selectedLead.contact_name} • {selectedLead.job_title}</p>
            <p className="email">{selectedLead.email}</p>
            <button
              className="btn btn-primary"
              onClick={() => setActiveTab('detail')}
            >
              View Details
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => setSelectedLead(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
