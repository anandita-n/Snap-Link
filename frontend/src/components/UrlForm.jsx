import React, { useState } from 'react';

export default function UrlForm({ onUrlShortened }) {
  const [url, setUrl] = useState('');
  const [customAlias, setCustomAlias] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [shortUrl, setShortUrl] = useState('');
  const [generateQr, setGenerateQr] = useState(false);
  const [qrCode, setQrCode] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    setShortUrl('');
    setQrCode('');

    // Basic frontend validation
    const trimmedUrl = url.trim();
    if (!trimmedUrl) {
      setError('Please enter a URL to shorten.');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/shorten', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: trimmedUrl,
          custom_alias: customAlias.trim() || null,
          generate_qr: generateQr,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong. Please try again.');
      }

      setShortUrl(data.short_url);
      setQrCode(data.qr_code || '');
      setSuccessMsg('Successfully shortened your URL!');
      setUrl('');
      setCustomAlias('');
      setGenerateQr(false);
      
      // Trigger parent reload
      if (onUrlShortened) {
        onUrlShortened();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="card-title">Shorten a URL</h2>
      <form onSubmit={handleSubmit} data-testid="shorten-form">
        <div className="form-group">
          <label htmlFor="url-input" className="form-label">
            URL
          </label>
          <input
            id="url-input"
            type="text"
            className="form-input"
            placeholder="https://example.com/some/long/path"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="alias-input" className="form-label">
            Custom Alias
          </label>
          <input
            id="alias-input"
            type="text"
            className="form-input"
            placeholder="e.g. my-custom-link"
            value={customAlias}
            onChange={(e) => setCustomAlias(e.target.value)}
            disabled={isLoading}
          />
        </div>

        <div className="qr-checkbox-container">
          <input
            id="qr-checkbox"
            type="checkbox"
            checked={generateQr}
            onChange={(e) => setGenerateQr(e.target.checked)}
            disabled={isLoading}
            data-testid="qr-checkbox"
          />
          <label htmlFor="qr-checkbox">
            Generate QR Code
          </label>
        </div>

         <button
           type="submit"
           className="submit-btn"
           disabled={isLoading}
         >
           {isLoading ? (generateQr ? 'Generating...' : 'Shortening...') : (generateQr ? 'Shorten & Generate QR' : 'Shorten')}
         </button>
      </form>

      {error && (
        <div className="message error" data-testid="error-message">
          {error}
        </div>
      )}

      {successMsg && (
        <div className="message success" data-testid="success-message">
          <div style={{ fontWeight: 600, marginBottom: '0.5rem' }}>{successMsg}</div>
          {qrCode && (
            <div className="result-box" data-testid="result-box">
              <div className="qr-success-container" data-testid="qr-success-container">
                <span className="result-box-title">QR Code</span>
                <img src={qrCode} alt="QR Code" className="qr-image" data-testid="qr-success-image" />
                <a
                  href={qrCode}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="copy-btn"
                  style={{ textDecoration: 'none', display: 'inline-block', marginTop: '0.5rem' }}
                  data-testid="qr-download-btn"
                >
                  Download QR Code
                </a>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
