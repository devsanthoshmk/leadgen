import { useState, useEffect } from 'react';
import * as XLSX from 'xlsx';
import { Search, MapPin, Download, RefreshCw, Mail, Phone, ExternalLink, Settings2, Trash2 } from 'lucide-react';

export interface LeadData {
  id: string;
  company_name: string | null;
  job_title: string | null;
  contact_name: string | null;
  email: string | null;
  phone: string | null;
  linkedin_url: string | null;
  industry: string | null;
  location: string | null;
  website: string | null;
  source: string[];
  // custom UI fields
  status: 'pending' | 'contacted' | 'replied' | 'rejected';
  customMessage: string;
}

const API_BASE = 'http://localhost:5000/api';

export default function App() {
  const [leads, setLeads] = useState<LeadData[]>(() => {
    const saved = localStorage.getItem('leadgen_leads');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) { return []; }
    }
    return [];
  });
  
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Redo modal state
  const [redoLead, setRedoLead] = useState<LeadData | null>(null);
  const [redoSources, setRedoSources] = useState<string[]>(['scrapegraph']);
  const [redoLoading, setRedoLoading] = useState(false);
  const [redoResult, setRedoResult] = useState<Partial<LeadData> | null>(null);

  useEffect(() => {
    localStorage.setItem('leadgen_leads', JSON.stringify(leads));
  }, [leads]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, location, max_results: 10 })
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || 'Failed to fetch');
      
      const newLeads = data.leads.map((l: any) => ({
        ...l,
        id: crypto.randomUUID(),
        status: 'pending',
        customMessage: ''
      }));
      setLeads(prev => [...newLeads, ...prev]);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateLead = (id: string, updates: Partial<LeadData>) => {
    setLeads(prev => prev.map(l => l.id === id ? { ...l, ...updates } : l));
  };
  
  const removeLead = (id: string) => {
    if (window.confirm('Remove this lead?')) {
      setLeads(prev => prev.filter(l => l.id !== id));
    }
  };

  const clearAll = () => {
    if (window.confirm('Clear all leads? This cannot be undone.')) {
      setLeads([]);
    }
  };

  const handleExportXLSX = () => {
    if (leads.length === 0) return;
    const worksheetData = leads.map(l => ({
      Company: l.company_name,
      Contact: l.contact_name,
      Title: l.job_title,
      Email: l.email,
      Phone: l.phone,
      Location: l.location,
      Industry: l.industry,
      Website: l.website,
      LinkedIn: l.linkedin_url,
      Status: l.status,
      Message: l.customMessage,
      Sources: l.source?.join(', ')
    }));
    
    const ws = XLSX.utils.json_to_sheet(worksheetData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Leads");
    XLSX.writeFile(wb, "leadgen_export.xlsx");
  };

  const handleRedoLookup = async () => {
    if (!redoLead || !redoLead.company_name) return;
    setRedoLoading(true);
    setRedoResult(null);
    try {
      const resp = await fetch(`${API_BASE}/lookup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          company_name: redoLead.company_name,
          sources: redoSources
        })
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || 'Failed lookup');
      setRedoResult(data.lead);
    } catch (err: any) {
      alert("Error finding lead: " + err.message);
    } finally {
      setRedoLoading(false);
    }
  };

  const applyRedo = () => {
    if (redoLead && redoResult) {
      updateLead(redoLead.id, {
        ...redoResult,
        status: redoLead.status,
        customMessage: redoLead.customMessage
      } as Partial<LeadData>);
      setRedoLead(null);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <div>
          <h1>Mergex LeadGen</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>AI-Powered Sales Lead Generation Pipeline</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          {leads.length > 0 && (
            <>
              <button className="btn btn-danger" onClick={clearAll} title="Clear All">
                <Trash2 size={16} /> Clear All
              </button>
              <button className="btn btn-primary" onClick={handleExportXLSX}>
                <Download size={16} /> Export XLSX
              </button>
            </>
          )}
        </div>
      </header>

      {error && (
        <div className="toast error">
          <span>{error}</span>
        </div>
      )}

      <div className="panel">
        <form className="search-form" onSubmit={handleSearch}>
          <div className="form-group" style={{ flex: 2 }}>
            <label>Search Query / Prompt</label>
            <div style={{ position: 'relative' }}>
               <Search size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
               <input 
                 style={{ width: '100%', paddingLeft: '2.5rem' }} 
                 placeholder="e.g. Real Estate Agencies, Tech Startups..." 
                 value={query}
                 onChange={e => setQuery(e.target.value)}
                 required
               />
            </div>
          </div>
          <div className="form-group" style={{ flex: 1 }}>
            <label>Location (Optional)</label>
            <div style={{ position: 'relative' }}>
               <MapPin size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
               <input 
                 style={{ width: '100%', paddingLeft: '2.5rem' }} 
                 placeholder="e.g. New York, London..." 
                 value={location}
                 onChange={e => setLocation(e.target.value)}
               />
            </div>
          </div>
          <button className="btn btn-primary" style={{ height: '42px' }} type="submit" disabled={loading}>
            {loading ? <div className="loader" /> : <><Search size={16} /> Find Leads</>}
          </button>
        </form>
      </div>

      <div className="table-container">
        {leads.length === 0 ? (
          <div className="empty-state">
            <Search size={48} />
            <h3>No leads mapped yet</h3>
            <p>Start by entering a query and creating new connections.</p>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Company</th>
                <th>Contact Person</th>
                <th>Contact Info</th>
                <th>Sources</th>
                <th>Status</th>
                <th>Custom Message</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {leads.map(lead => (
                <tr key={lead.id}>
                  <td>
                    <div className="cell-title">{lead.company_name || 'Unknown'}</div>
                    <div className="cell-subtitle">{lead.industry || 'N/A'} {lead.location ? `• ${lead.location}` : ''}</div>
                    {lead.website && (
                       <a href={lead.website.startsWith('http') ? lead.website : `https://${lead.website}`} target="_blank" rel="noreferrer" className="link-btn" style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>
                         <ExternalLink size={12} /> Website
                       </a>
                    )}
                  </td>
                  <td>
                    <div className="cell-title">{lead.contact_name || '--'}</div>
                    <div className="cell-subtitle">{lead.job_title || ''}</div>
                    {lead.linkedin_url && (
                        <a href={lead.linkedin_url} target="_blank" rel="noreferrer" className="link-btn" style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>
                          <ExternalLink size={12} /> LinkedIn
                        </a>
                    )}
                  </td>
                  <td>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                      {lead.email && <span className="cell-subtitle" style={{display:'flex', alignItems:'center', gap:'4px'}}><Mail size={12}/> {lead.email}</span>}
                      {lead.phone && <span className="cell-subtitle" style={{display:'flex', alignItems:'center', gap:'4px'}}><Phone size={12}/> {lead.phone}</span>}
                      {!lead.email && !lead.phone && <span className="cell-subtitle">No info</span>}
                    </div>
                  </td>
                  <td>
                     <div className="pill-list" style={{ maxWidth: '120px' }}>
                       {lead.source?.map(s => <span className="pill" key={s}>{s}</span>)}
                     </div>
                  </td>
                  <td>
                    <select 
                      className={`status-select status-${lead.status}`} 
                      value={lead.status}
                      onChange={e => updateLead(lead.id, { status: e.target.value as any })}
                    >
                      <option value="pending">Pending</option>
                      <option value="contacted">Contacted</option>
                      <option value="replied">Replied</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </td>
                  <td style={{ minWidth: '200px' }}>
                    <textarea 
                      className="editable-textarea" 
                      placeholder="Add notes..." 
                      value={lead.customMessage}
                      onChange={e => updateLead(lead.id, { customMessage: e.target.value })}
                    />
                  </td>
                  <td>
                    <div className="actions-col">
                      <button className="icon-btn" title="Redo / Enhance Row" onClick={() => setRedoLead(lead)}>
                        <Settings2 size={16} />
                      </button>
                      <button className="icon-btn" title="Delete Row" onClick={() => removeLead(lead.id)}>
                         <Trash2 size={16} style={{ color: 'var(--danger)' }} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {redoLead && (
        <div className="modal-overlay" onClick={(e) => { if (e.target === e.currentTarget) setRedoLead(null); }}>
          <div className="modal-content">
            <div className="modal-header">
              <h2>Enhance / Redo Lead</h2>
              <button className="icon-btn" onClick={() => setRedoLead(null)}>✕</button>
            </div>
            
            <p className="cell-subtitle" style={{ marginBottom: '1.5rem' }}>
              Select sources to re-scrape and look up fresh data for <strong>{redoLead.company_name}</strong>.
            </p>
            
            <div className="source-checkboxes">
              <label className="checkbox-label">
                <input 
                  type="checkbox" 
                  checked={redoSources.includes('scrapegraph')} 
                  onChange={(e) => setRedoSources(prev => e.target.checked ? [...prev, 'scrapegraph'] : prev.filter(s => s !== 'scrapegraph'))}
                />
                ScrapeGraph AI
              </label>
              <label className="checkbox-label">
                <input 
                  type="checkbox" 
                  checked={redoSources.includes('linkedin')} 
                  onChange={(e) => setRedoSources(prev => e.target.checked ? [...prev, 'linkedin'] : prev.filter(s => s !== 'linkedin'))}
                />
                LinkedIn
              </label>
              <label className="checkbox-label">
                <input 
                  type="checkbox" 
                  checked={redoSources.includes('google_maps')} 
                  onChange={(e) => setRedoSources(prev => e.target.checked ? [...prev, 'google_maps'] : prev.filter(s => s !== 'google_maps'))}
                />
                Google Maps
              </label>
            </div>
            
            <button className="btn btn-primary" onClick={handleRedoLookup} disabled={redoLoading} style={{ marginBottom: '1.5rem' }}>
              {redoLoading ? "Searching..." : <><RefreshCw size={16} /> Extract Fresh Data</>}
            </button>
            
            {redoResult && (
              <>
                <div className="diff-view">
                  <div className="diff-panel">
                    <h3>Current Info</h3>
                    <div className="diff-item"><span className="diff-item-label">Name:</span> {redoLead.contact_name ?? '--'}</div>
                    <div className="diff-item"><span className="diff-item-label">Email:</span> {redoLead.email ?? '--'}</div>
                    <div className="diff-item"><span className="diff-item-label">Title:</span> {redoLead.job_title ?? '--'}</div>
                  </div>
                  <div className="diff-panel" style={{ borderColor: 'var(--accent-color)' }}>
                    <h3>New Info</h3>
                    <div className="diff-item"><span className="diff-item-label">Name:</span> {redoResult.contact_name ?? '--'}</div>
                    <div className="diff-item"><span className="diff-item-label">Email:</span> {redoResult.email ?? '--'}</div>
                    <div className="diff-item"><span className="diff-item-label">Title:</span> {redoResult.job_title ?? '--'}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                  <button className="btn" onClick={() => setRedoLead(null)}>Cancel</button>
                  <button className="btn btn-primary" onClick={applyRedo}>Approve & Replace</button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
