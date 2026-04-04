import React, { useState } from 'react';
import '../styles/LeadsTable.css';

function LeadsTable({ leads, onSelectLead, onDelete, onAddToDatabase, editable = false }) {
  const [sortBy, setSortBy] = useState('lead_score');
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = leads.filter(lead => {
    const matchesStatus = filterStatus === 'all' || lead.status === filterStatus;
    const matchesSearch = searchQuery === '' ||
      lead.company_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      lead.contact_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      lead.email.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  const sorted = [...filtered].sort((a, b) => {
    switch (sortBy) {
      case 'lead_score':
        return (b.lead_score || 0) - (a.lead_score || 0);
      case 'company':
        return a.company_name.localeCompare(b.company_name);
      case 'date':
        return new Date(b.created_at) - new Date(a.created_at);
      default:
        return 0;
    }
  });

  const getScoreBadge = (score) => {
    if (score >= 75) return 'badge-hot';
    if (score >= 50) return 'badge-warm';
    return 'badge-cold';
  };

  const getStatusBadge = (status) => {
    const colors = {
      'new': 'badge-new',
      'contacted': 'badge-contacted',
      'qualified': 'badge-qualified',
      'negotiation': 'badge-negotiation',
      'closed_won': 'badge-won',
      'closed_lost': 'badge-lost',
      'archived': 'badge-archived'
    };
    return colors[status] || 'badge-new';
  };

  return (
    <div className="leads-table-container">
      {/* Toolbar */}
      <div className="table-toolbar">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search by company, contact, or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="toolbar-controls">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Status</option>
            <option value="new">New</option>
            <option value="contacted">Contacted</option>
            <option value="qualified">Qualified</option>
            <option value="negotiation">Negotiation</option>
            <option value="closed_won">Closed Won</option>
            <option value="closed_lost">Closed Lost</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="lead_score">Sort by Score</option>
            <option value="company">Sort by Company</option>
            <option value="date">Sort by Date</option>
          </select>
        </div>
      </div>

      {/* Table */}
      {sorted.length === 0 ? (
        <div className="empty-state">
          <p>No leads found</p>
          {editable && <p className="small">Try searching to add leads</p>}
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="leads-table">
            <thead>
              <tr>
                <th>Score</th>
                <th>Company</th>
                <th>Contact</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Industry</th>
                <th>Location</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((lead, idx) => (
                <tr key={lead.id || idx} className="lead-row">
                  <td>
                    <div className={`score-badge ${getScoreBadge(lead.lead_score)}`}>
                      {lead.lead_score}
                    </div>
                  </td>
                  <td className="company-cell">
                    <strong>{lead.company_name}</strong>
                  </td>
                  <td>
                    <div className="contact-info">
                      <strong>{lead.contact_name}</strong>
                      <small>{lead.job_title}</small>
                    </div>
                  </td>
                  <td className="email-cell">
                    <a href={`mailto:${lead.email}`}>{lead.email}</a>
                  </td>
                  <td>
                    {lead.phone ? (
                      <a href={`tel:${lead.phone}`}>{lead.phone}</a>
                    ) : (
                      <span className="text-muted">-</span>
                    )}
                  </td>
                  <td>{lead.industry || '-'}</td>
                  <td className="location-cell">{lead.location}</td>
                  <td>
                    <span className={`status-badge ${getStatusBadge(lead.status)}`}>
                      {lead.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="actions-cell">
                    <div className="action-buttons">
                      {lead.linkedin_url && (
                        <a
                          href={lead.linkedin_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn-icon"
                          title="Open LinkedIn"
                        >
                          in
                        </a>
                      )}
                      <button
                        className="btn-icon"
                        onClick={() => onSelectLead(lead)}
                        title="View details"
                      >
                        👁️
                      </button>
                      {onAddToDatabase && (
                        <button
                          className="btn-icon btn-add"
                          onClick={() => onAddToDatabase(lead)}
                          title="Add to database"
                        >
                          ➕
                        </button>
                      )}
                      {onDelete && editable && (
                        <button
                          className="btn-icon btn-delete"
                          onClick={() => {
                            if (window.confirm('Delete this lead?')) {
                              onDelete(lead.id);
                            }
                          }}
                          title="Delete"
                        >
                          🗑️
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Stats */}
      <div className="table-footer">
        <p className="result-count">Showing {sorted.length} of {leads.length} leads</p>
      </div>
    </div>
  );
}

export default LeadsTable;
