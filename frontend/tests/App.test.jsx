import React from 'react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../src/App';
import UrlForm from '../src/components/UrlForm';
import UrlList from '../src/components/UrlList';

// Mock global fetch
beforeEach(() => {
  global.fetch = vi.fn();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('URL Shortener Frontend App', () => {

  it('renders the app header and form correctly', async () => {
    // Mock GET /links response
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(<App />);

    expect(screen.getByText('SnapLink')).toBeInTheDocument();
    expect(screen.getByText('A minimal, clean, and fast URL shortener service')).toBeInTheDocument();
    expect(screen.getByLabelText(/URL/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Custom Alias/i)).toBeInTheDocument();

    // Wait for the mock fetch to resolve and state updates to process
    await waitFor(() => {
      expect(screen.getByTestId('empty-state')).toBeInTheDocument();
    });
  });

  it('validates that URL input cannot be empty', async () => {
    const handleUrlShortened = vi.fn();
    render(<UrlForm onUrlShortened={handleUrlShortened} />);

    const submitBtn = screen.getByRole('button', { name: /Shorten/i });
    fireEvent.click(submitBtn);

    // Should display validation error
    const errorMsg = await screen.findByTestId('error-message');
    expect(errorMsg).toHaveTextContent('Please enter a URL to shorten.');
    expect(handleUrlShortened).not.toHaveBeenCalled();
  });

  it('submits form successfully and displays short URL', async () => {
    const handleUrlShortened = vi.fn();

    // Mock POST /shorten response
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        short_code: 'abc123',
        short_url: 'http://localhost:8000/abc123',
        original_url: 'https://google.com',
      }),
    });

    render(<UrlForm onUrlShortened={handleUrlShortened} />);

    const urlInput = screen.getByLabelText(/URL/i);
    const aliasInput = screen.getByLabelText(/Custom Alias/i);
    const submitBtn = screen.getByRole('button', { name: /Shorten/i });

    fireEvent.change(urlInput, { target: { value: 'https://google.com' } });
    fireEvent.change(aliasInput, { target: { value: 'abc123' } });
    fireEvent.click(submitBtn);

    // Verify success alerts
    const successMsg = await screen.findByTestId('success-message');
    expect(successMsg).toHaveTextContent('Successfully shortened your URL!');

    expect(handleUrlShortened).toHaveBeenCalledTimes(1);
  });

  it('submits form with generate QR code checked and displays QR code', async () => {
    const handleUrlShortened = vi.fn();

    // Mock POST /shorten response returning a qr_code
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        short_code: 'abc123',
        short_url: 'http://localhost:8000/abc123',
        original_url: 'https://google.com',
        qr_code: 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://google.com',
      }),
    });

    render(<UrlForm onUrlShortened={handleUrlShortened} />);

    const urlInput = screen.getByLabelText(/URL/i);
    const qrCheckbox = screen.getByTestId('qr-checkbox');
    const submitBtn = screen.getByRole('button', { name: /Shorten/i });

    fireEvent.change(urlInput, { target: { value: 'https://google.com' } });
    fireEvent.click(qrCheckbox);
    
    expect(qrCheckbox.checked).toBe(true);
    
    fireEvent.click(submitBtn);

    const successMsg = await screen.findByTestId('success-message');
    expect(successMsg).toHaveTextContent('Successfully shortened your URL!');
    
    expect(screen.getByTestId('qr-success-container')).toBeInTheDocument();
    expect(screen.getByTestId('qr-success-image')).toHaveAttribute('src', 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://google.com');
    expect(screen.getByTestId('qr-download-btn')).toBeInTheDocument();

    expect(handleUrlShortened).toHaveBeenCalledTimes(1);
    
    const fetchBody = JSON.parse(global.fetch.mock.calls[0][1].body);
    expect(fetchBody.generate_qr).toBe(true);
  });

  it('renders list of shortened links with and without QR codes correctly', () => {
    const mockLinks = [
      {
        short_code: 'abc123',
        original_url: 'https://google.com',
        clicks: 15,
        created_at: '2026-07-08T06:00:00Z',
        short_url: 'http://localhost:8000/abc123',
        qr_code: 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://google.com',
      },
      {
        short_code: 'xyz789',
        original_url: 'https://github.com',
        clicks: 42,
        created_at: '2026-07-08T06:05:00Z',
        short_url: 'http://localhost:8000/xyz789',
        qr_code: null,
      },
    ];

    render(<UrlList links={mockLinks} isLoading={false} error="" />);

    expect(screen.getByTestId('links-table')).toBeInTheDocument();
    expect(screen.getByText('https://google.com')).toBeInTheDocument();
    expect(screen.getByText('https://github.com')).toBeInTheDocument();
  });

  it('displays empty state message when no links are available', () => {
    render(<UrlList links={[]} isLoading={false} error="" />);
    expect(screen.getByTestId('empty-state')).toHaveTextContent(
      'No shortened links yet. Shorten a URL above to see it here!'
    );
  });

  it('refreshes the list of links when the refresh button is clicked', async () => {
    const mockLinks = [
      {
        short_code: 'abc123',
        original_url: 'https://google.com',
        clicks: 1,
        created_at: '2026-07-08T06:00:00Z',
        short_url: 'http://localhost:8000/abc123',
      }
    ];

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockLinks,
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('https://google.com')).toBeInTheDocument();
    });

    const updatedLinks = [
      {
        ...mockLinks[0],
        clicks: 2
      }
    ];

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => updatedLinks,
    });

    const refreshBtn = screen.getByRole('button', { name: /Refresh/i });
    fireEvent.click(refreshBtn);

    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument();
    });

    expect(global.fetch).toHaveBeenCalledTimes(2);
    const secondFetchUrl = global.fetch.mock.calls[1][0];
    expect(secondFetchUrl).toContain('clear=false');
  });

  it('handles toggleable test failure mode for demoing CI failures', () => {
    const toggleVar = process.env.VITE_TOGGLE_TEST_FAILURE || process.env.TOGGLE_TEST_FAILURE;
    const isTriggered = toggleVar === 'true';

    if (isTriggered) {
      expect('Test should fail').toBe('Intentionally failed via toggle');
    } else {
      expect(true).toBe(true);
    }
  });

});
