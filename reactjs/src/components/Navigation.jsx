import React from 'react';
import '../styles/Navigation.css';

function Navigation({ activeTab, onTabChange }) {
  const tabs = [
    { id: 'search', label: '🔍 Search', icon: '🔍' },
    { id: 'results', label: '📋 Results', icon: '📋' },
    { id: 'leads', label: '📊 Database', icon: '📊' },
    { id: 'analytics', label: '📈 Analytics', icon: '📈' }
  ];

  return (
    <nav className="navigation">
      <div className="nav-brand">
        <h1>🎯 LeadGen</h1>
        <p className="brand-subtitle">B2B Lead Generation Platform</p>
      </div>

      <div className="nav-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => onTabChange(tab.id)}
          >
            <span className="nav-icon">{tab.icon}</span>
            <span className="nav-label">{tab.label}</span>
          </button>
        ))}
      </div>

      <div className="nav-info">
        <p className="info-text">
          Powered by LinkedIn, Google Maps & ScrapeGraph AI
        </p>
      </div>
    </nav>
  );
}

export default Navigation;
