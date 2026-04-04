import React, { useState } from 'react';
import '../styles/LeadDetail.css';

function LeadDetail({ lead, onUpdate, onDelete, onClose }) {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({ ...lead });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSave = () => {
    const updates = {};
    Object.keys(formData).forEach(key => {
      if (formData[key] !== lead[key]) {
        updates[key] = formData[key];
      }
    });

    if (Object.keys(updates).length > 0) {
      onUpdate(lead.id, updates);
    }
    setIsEditing(false);
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this lead?')) {
      onDelete(lead.id);
      onClose();
    }
  };

  return (
    <div className="lead-detail-container">
      <div className="detail-header">
        <div className="header-content">
          <h2>{lead.company_name}</h2>
          <p className="subtitle">{lead.contact_name} • {lead.job_title}</p>
        </div>

        <div className="detail-actions">
          {!isEditing && (
            <>
              <button
                className="btn btn-secondary"
                onClick={() => setIsEditing(true)}
              >
                ✏️ Edit
              </button>
              <button
                className="btn btn-danger"
                onClick={handleDelete}
              >
                🗑️ Delete
              </button>
            </>
          )}
          <button
            className="btn btn-secondary"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>

      <div className="detail-content">
        {/* Score Section */}
        <div className="detail-section score-section">
          <h3>Lead Score</h3>
          <div className="score-display">
            <div className="score-value">{lead.lead_score}/100</div>
            <div className="score-bar">
              <div
                className={`score-fill ${
                  lead.lead_score >= 75
                    ? 'hot'
                    : lead.lead_score >= 50
                      ? 'warm'
                      : 'cold'
                }`}
                style={{ width: `${lead.lead_score}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="detail-section">
          <h3>Contact Information</h3>
          <div className="form-group">
            <label>Contact Name</label>
            <input
              type="text"
              name="contact_name"
              value={formData.contact_name}
              onChange={handleInputChange}
              disabled={!isEditing}
            />
          </div>

          <div className="form-group">
            <label>Job Title</label>
            <input
              type="text"
              name="job_title"
              value={formData.job_title}
              onChange={handleInputChange}
              disabled={!isEditing}
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              disabled={!isEditing}
            />
          </div>

          <div className="form-group">
            <label>Phone</label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleInputChange}
              disabled={!isEditing}
            />
          </div>

          <div className="form-group">
            <label>LinkedIn URL</label>
            <input
              type="url"
              name="linkedin_url"
              value={formData.linkedin_url}
              onChange={handleInputChange}
              disabled={!isEditing}
            />
            {formData.linkedin_url && (
              <a
                href={formData.linkedin_url}
                target="_blank"
                rel="noopener noreferrer"
                className="link-button"
              >
                Open LinkedIn Profile →
              </a>
            )}
          </div>
        </div>

        {/* Company Information */}
        <div className="detail-section">
          <h3>Company Information</h3>
          <div className="form-group">
            <label>Company Name</label>
            <input
              type="text"
              name="company_name"
              value={formData.company_name}
              onChange={handleInputChange}
              disabled={!isEditing}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Industry</label>
              <input
                type="text"
                name="industry"
                value={formData.industry}
                onChange={handleInputChange}
                disabled={!isEditing}
              />
            </div>

            <div className="form-group">
              <label>Location</label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleInputChange}
                disabled={!isEditing}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Company Size</label>
              <input
                type="text"
                name="company_size"
                value={formData.company_size}
                onChange={handleInputChange}
                disabled={!isEditing}
              />
            </div>

            <div className="form-group">
              <label>Revenue Estimate</label>
              <input
                type="text"
                name="revenue_estimate"
                value={formData.revenue_estimate}
                onChange={handleInputChange}
                disabled={!isEditing}
              />
            </div>
          </div>
        </div>

        {/* Sales Information */}
        <div className="detail-section">
          <h3>Sales Information</h3>
          <div className="form-group">
            <label>Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleInputChange}
              disabled={!isEditing}
            >
              <option value="new">New</option>
              <option value="contacted">Contacted</option>
              <option value="qualified">Qualified</option>
              <option value="negotiation">Negotiation</option>
              <option value="closed_won">Closed Won</option>
              <option value="closed_lost">Closed Lost</option>
              <option value="archived">Archived</option>
            </select>
          </div>

          <div className="form-group">
            <label>Notes</label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              disabled={!isEditing}
              rows="4"
              placeholder="Add salesperson notes here..."
            ></textarea>
          </div>
        </div>

        {/* Metadata */}
        <div className="detail-section metadata">
          <h3>Metadata</h3>
          <div className="meta-info">
            <div className="meta-item">
              <span className="meta-label">Source:</span>
              <span className="meta-value">{lead.source}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Created:</span>
              <span className="meta-value">
                {new Date(lead.created_at).toLocaleDateString()}
              </span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Updated:</span>
              <span className="meta-value">
                {new Date(lead.last_updated).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Actions */}
      {isEditing && (
        <div className="detail-footer">
          <button
            className="btn btn-primary"
            onClick={handleSave}
          >
            ✓ Save Changes
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => {
              setFormData({ ...lead });
              setIsEditing(false);
            }}
          >
            ✕ Cancel
          </button>
        </div>
      )}
    </div>
  );
}

export default LeadDetail;
