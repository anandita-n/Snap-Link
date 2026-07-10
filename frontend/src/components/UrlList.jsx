import React from 'react';

export default function UrlList({ links, isLoading, isRefreshing, error, onRefresh }) {
  const formatDate = (isoString) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleString();
    } catch {
      return isoString;
    }
  };

  const copyToClipboard = (url) => {
    navigator.clipboard.writeText(url);
  };

  if (isLoading || isRefreshing) {
    return (
      <div className="card" data-testid="links-loading">
        <h2 className="card-title">All Links</h2>
        <div className="empty-state">Loading links...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card" data-testid="links-error">
        <h2 className="card-title">All Links</h2>
        <div className="message error">Failed to load links: {error}</div>
        {onRefresh && (
          <button onClick={onRefresh} className="submit-btn" style={{ marginTop: '1rem', width: 'auto' }}>
            Retry
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="card" data-testid="links-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 className="card-title" style={{ marginBottom: 0 }}>All Shortened Links</h2>
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="copy-btn"
            type="button"
            style={{ padding: '4px 8px' }}
            disabled={isRefreshing}
          >
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        )}
      </div>

      {links.length === 0 ? (
        <div className="empty-state" data-testid="empty-state">
          No shortened links yet. Shorten a URL above to see it here!
        </div>
      ) : (
        <div className="table-container">
          <table className="links-table" data-testid="links-table">
            <thead>
              <tr>
                <th>Original URL</th>
                <th>Short URL</th>
                <th style={{ textAlign: 'center' }}>Clicks</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              {links.map((link) => (
                <tr key={link.short_code} data-testid={`link-row-${link.short_code}`}>
                  <td className="url-cell" title={link.original_url}>
                    {link.original_url}
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <a
                        href={link.short_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="short-url-link"
                      >
                        {link.short_code}
                      </a>
                      <button
                        onClick={() => copyToClipboard(link.short_url)}
                        className="copy-btn"
                        type="button"
                        style={{ padding: '2px 6px', fontSize: '0.75rem' }}
                      >
                        Copy
                      </button>
                    </div>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <span className="clicks-badge">{link.clicks}</span>
                  </td>
                  <td>{formatDate(link.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
