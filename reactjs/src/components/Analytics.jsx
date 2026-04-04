import React, { useMemo } from 'react';
import '../styles/Analytics.css';

function Analytics({ stats, leads, onRefresh }) {
  const analytics = useMemo(() => {
    if (!leads || leads.length === 0) {
      return {
        total: 0,
        by_status: {},
        by_industry: {},
        avg_score: 0,
        high_priority: 0,
        conversion_rate: 0
      };
    }

    const total = leads.length;
    const by_status = {};
    const by_industry = {};
    let total_score = 0;
    let high_priority = 0;

    leads.forEach(lead => {
      // By status
      const status = lead.status || 'new';
      by_status[status] = (by_status[status] || 0) + 1;

      // By industry
      const industry = lead.industry || 'Unknown';
      by_industry[industry] = (by_industry[industry] || 0) + 1;

      // Score tracking
      total_score += lead.lead_score || 0;
      if ((lead.lead_score || 0) >= 75) high_priority++;
    });

    const avg_score = Math.round(total_score / total);
    const conversion_rate = Math.round((by_status['qualified'] || 0) / total * 100);

    return {
      total,
      by_status,
      by_industry,
      avg_score,
      high_priority,
      conversion_rate
    };
  }, [leads]);

  return (
    <div className="analytics-container">
      <div className="analytics-header">
        <h2>📈 Sales Analytics</h2>
        <button className="btn btn-secondary" onClick={onRefresh}>
          🔄 Refresh
        </button>
      </div>

      {/* Key Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-value">{analytics.total}</div>
          <div className="metric-label">Total Leads</div>
          <div className="metric-subtext">In database</div>
        </div>

        <div className="metric-card">
          <div className="metric-value">{analytics.avg_score}</div>
          <div className="metric-label">Avg Lead Score</div>
          <div className="metric-subtext">/100</div>
        </div>

        <div className="metric-card">
          <div className="metric-value">{analytics.high_priority}</div>
          <div className="metric-label">High Priority</div>
          <div className="metric-subtext">Score ≥ 75</div>
        </div>

        <div className="metric-card">
          <div className="metric-value">{analytics.conversion_rate}%</div>
          <div className="metric-label">Qualification Rate</div>
          <div className="metric-subtext">Qualified leads</div>
        </div>
      </div>

      {/* Status Distribution */}
      <div className="analytics-section">
        <h3>Status Distribution</h3>
        <div className="chart-container">
          {Object.entries(analytics.by_status).length === 0 ? (
            <p className="empty-message">No data yet</p>
          ) : (
            <div className="status-bars">
              {Object.entries(analytics.by_status).map(([status, count]) => {
                const percentage = (count / analytics.total) * 100;
                return (
                  <div key={status} className="status-bar">
                    <div className="status-label">
                      <span className="status-name">{status.replace('_', ' ')}</span>
                      <span className="status-count">{count} ({percentage.toFixed(1)}%)</span>
                    </div>
                    <div className="bar-background">
                      <div
                        className={`bar-fill status-${status}`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Industry Distribution */}
      <div className="analytics-section">
        <h3>Leads by Industry</h3>
        <div className="chart-container">
          {Object.entries(analytics.by_industry).length === 0 ? (
            <p className="empty-message">No data yet</p>
          ) : (
            <div className="industry-list">
              {Object.entries(analytics.by_industry)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 10)
                .map(([industry, count]) => {
                  const percentage = (count / analytics.total) * 100;
                  return (
                    <div key={industry} className="industry-item">
                      <div className="industry-header">
                        <span className="industry-name">{industry}</span>
                        <span className="industry-count">{count} leads</span>
                      </div>
                      <div className="industry-bar">
                        <div
                          className="industry-fill"
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
            </div>
          )}
        </div>
      </div>

      {/* Funnel Analysis */}
      <div className="analytics-section">
        <h3>Sales Funnel</h3>
        <div className="funnel-container">
          {[
            { stage: 'New', status: 'new', color: 'new' },
            { stage: 'Contacted', status: 'contacted', color: 'contacted' },
            { stage: 'Qualified', status: 'qualified', color: 'qualified' },
            { stage: 'Negotiation', status: 'negotiation', color: 'negotiation' },
            { stage: 'Closed Won', status: 'closed_won', color: 'won' }
          ].map((stage, index) => {
            const count = analytics.by_status[stage.status] || 0;
            const percentage = analytics.total > 0 ? (count / analytics.total) * 100 : 0;

            return (
              <div
                key={stage.status}
                className="funnel-stage"
                style={{
                  width: `${Math.max(20, percentage)}%`
                }}
              >
                <div className={`funnel-content funnel-${stage.color}`}>
                  <div className="funnel-stage-name">{stage.stage}</div>
                  <div className="funnel-stage-count">{count}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Score Distribution */}
      <div className="analytics-section">
        <h3>Lead Score Distribution</h3>
        <div className="score-buckets">
          {[
            { range: '75-100', min: 75, max: 100, color: 'hot' },
            { range: '50-74', min: 50, max: 74, color: 'warm' },
            { range: '25-49', min: 25, max: 49, color: 'cool' },
            { range: '0-24', min: 0, max: 24, color: 'cold' }
          ].map(bucket => {
            const count = leads.filter(
              l => (l.lead_score || 0) >= bucket.min && (l.lead_score || 0) <= bucket.max
            ).length;

            return (
              <div key={bucket.range} className={`score-bucket bucket-${bucket.color}`}>
                <div className="bucket-count">{count}</div>
                <div className="bucket-label">{bucket.range}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Top Performing Industries */}
      <div className="analytics-section">
        <h3>Top Industries by Avg Score</h3>
        <div className="table-container">
          {Object.entries(analytics.by_industry).length === 0 ? (
            <p className="empty-message">No data yet</p>
          ) : (
            <table className="performance-table">
              <thead>
                <tr>
                  <th>Industry</th>
                  <th>Count</th>
                  <th>Avg Score</th>
                  <th>Qualified %</th>
                </tr>
              </thead>
              <tbody>
                {Object.keys(analytics.by_industry)
                  .map(industry => {
                    const industry_leads = leads.filter(l => l.industry === industry);
                    const avg_score = Math.round(
                      industry_leads.reduce((sum, l) => sum + (l.lead_score || 0), 0) /
                      industry_leads.length
                    );
                    const qualified = industry_leads.filter(
                      l => l.status === 'qualified'
                    ).length;
                    const qualified_pct = Math.round(
                      (qualified / industry_leads.length) * 100
                    );

                    return (
                      <tr key={industry}>
                        <td>{industry}</td>
                        <td>{industry_leads.length}</td>
                        <td>
                          <span className={`score-badge ${
                            avg_score >= 75 ? 'hot' : avg_score >= 50 ? 'warm' : 'cold'
                          }`}>
                            {avg_score}
                          </span>
                        </td>
                        <td>{qualified_pct}%</td>
                      </tr>
                    );
                  })
                  .sort((a, b) => {
                    const score_a = leads
                      .filter(l => l.industry === a.props.children[0].props.children)
                      .reduce((sum, l) => sum + (l.lead_score || 0), 0) || 0;
                    const score_b = leads
                      .filter(l => l.industry === b.props.children[0].props.children)
                      .reduce((sum, l) => sum + (l.lead_score || 0), 0) || 0;
                    return score_b - score_a;
                  })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

export default Analytics;
