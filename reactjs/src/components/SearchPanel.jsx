import React, { useState } from 'react';
import '../styles/SearchPanel.css';

function SearchPanel({ onSearch, loading }) {
  const [searchType, setSearchType] = useState('industry');
  const [formData, setFormData] = useState({
    industry: '',
    location: '',
    company_name: '',
    keywords: '',
    limit: 50
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSearchTypeChange = (type) => {
    setSearchType(type);
    setFormData(prev => ({ ...prev }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const params = {
      limit: parseInt(formData.limit) || 50
    };

    switch (searchType) {
      case 'industry':
        if (!formData.industry) {
          alert('Please enter an industry');
          return;
        }
        params.industry = formData.industry;
        if (formData.location) params.location = formData.location;
        break;

      case 'company':
        if (!formData.company_name) {
          alert('Please enter a company name');
          return;
        }
        params.company_name = formData.company_name;
        break;

      case 'location':
        if (!formData.location) {
          alert('Please enter a location');
          return;
        }
        params.location = formData.location;
        if (formData.keywords) params.keywords = formData.keywords;
        break;

      case 'keywords':
        if (!formData.keywords) {
          alert('Please enter keywords');
          return;
        }
        params.keywords = formData.keywords;
        if (formData.location) params.location = formData.location;
        break;

      default:
        return;
    }

    onSearch(searchType, params);
  };

  return (
    <div className="search-panel">
      <div className="search-header">
        <h2>🔍 Lead Search</h2>
        <p>Find qualified leads using LinkedIn, Google Maps, and web scraping</p>
      </div>

      <form onSubmit={handleSubmit} className="search-form">
        {/* Search Type Selection */}
        <div className="search-type-selector">
          {['industry', 'company', 'location', 'keywords'].map(type => (
            <button
              key={type}
              type="button"
              className={`search-type-btn ${searchType === type ? 'active' : ''}`}
              onClick={() => handleSearchTypeChange(type)}
              disabled={loading}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>

        {/* Search Type: Industry */}
        {searchType === 'industry' && (
          <div className="form-group">
            <label>Industry *</label>
            <input
              type="text"
              name="industry"
              value={formData.industry}
              onChange={handleInputChange}
              placeholder="e.g., Software Development, Marketing, Finance"
              disabled={loading}
            />
            <label>Location (Optional)</label>
            <input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleInputChange}
              placeholder="e.g., San Francisco, California"
              disabled={loading}
            />
          </div>
        )}

        {/* Search Type: Company */}
        {searchType === 'company' && (
          <div className="form-group">
            <label>Company Name *</label>
            <input
              type="text"
              name="company_name"
              value={formData.company_name}
              onChange={handleInputChange}
              placeholder="e.g., Google, Microsoft, Amazon"
              disabled={loading}
            />
          </div>
        )}

        {/* Search Type: Location */}
        {searchType === 'location' && (
          <div className="form-group">
            <label>Location *</label>
            <input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleInputChange}
              placeholder="e.g., New York, London, Tokyo"
              disabled={loading}
            />
            <label>Keywords (Optional)</label>
            <input
              type="text"
              name="keywords"
              value={formData.keywords}
              onChange={handleInputChange}
              placeholder="e.g., Sales Manager, CTO"
              disabled={loading}
            />
          </div>
        )}

        {/* Search Type: Keywords */}
        {searchType === 'keywords' && (
          <div className="form-group">
            <label>Keywords *</label>
            <input
              type="text"
              name="keywords"
              value={formData.keywords}
              onChange={handleInputChange}
              placeholder="e.g., VP Sales, Technology Director"
              disabled={loading}
            />
            <label>Location (Optional)</label>
            <input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleInputChange}
              placeholder="e.g., San Francisco"
              disabled={loading}
            />
          </div>
        )}

        {/* Common Options */}
        <div className="form-group">
          <label>Results Limit</label>
          <select
            name="limit"
            value={formData.limit}
            onChange={handleInputChange}
            disabled={loading}
          >
            <option value="10">10 results</option>
            <option value="25">25 results</option>
            <option value="50">50 results</option>
            <option value="100">100 results</option>
            <option value="200">200 results</option>
          </select>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="btn btn-primary btn-large"
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              Searching...
            </>
          ) : (
            'Start Search'
          )}
        </button>
      </form>

      {/* Search Tips */}
      <div className="search-tips">
        <h3>💡 Search Tips</h3>
        <ul>
          <li><strong>Industry Search:</strong> Find professionals in a specific industry</li>
          <li><strong>Company Search:</strong> Get contacts from a specific company</li>
          <li><strong>Location Search:</strong> Discover leads in a geographic area</li>
          <li><strong>Keywords Search:</strong> Advanced search by job titles or skills</li>
          <li><strong>Data Sources:</strong> Uses LinkedIn (primary) + Google Maps (fallback)</li>
        </ul>
      </div>
    </div>
  );
}

export default SearchPanel;
