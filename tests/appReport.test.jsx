/* @vitest-environment jsdom */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import App from '../src/App.jsx';

vi.mock('../src/utils/api.js', async () => {
  const actual = await vi.importActual('../src/utils/api.js');
  return {
    ...actual,
    fetchAgentChecks: vi.fn().mockResolvedValue({ agents: [] }),
  };
});

const telemetrySnapshot = {
  subsystems: {
    web: { cpu: 12, ram: 512 },
    app: { cpu: 22, ram: 256 },
    db: { cpu: 74, ram: 2048 },
  },
};

const persistedReport = {
  id: 'report-1',
  system_name: 'iMonitor',
  environment: 'production',
  status: 'warning',
  health_score: 0.73,
  primary_issue: 'Database latency is elevated',
  suggestions: ['Review query load', 'Check for storage contention'],
  created_at: '2026-06-12T11:30:00.000Z',
};

function mockDashboardFetch() {
  return vi.fn((url) => {
    if (url.includes('/api/simulator/health')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({ status: 'healthy' }),
      });
    }

    if (url.includes('/api/simulator/metrics')) {
      return Promise.resolve({
        ok: true,
        json: async () => telemetrySnapshot,
      });
    }

    if (url.includes('/api/simulator/ingest')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({ status: 'ingested' }),
      });
    }

    if (url.includes('/api/reports/latest')) {
      return Promise.resolve({
        ok: true,
        json: async () => persistedReport,
      });
    }

    return Promise.reject(new Error(`Unexpected fetch: ${url}`));
  });
}

describe('report exports in the dashboard', () => {
  let createObjectURLSpy;
  let revokeObjectURLSpy;
  let anchorClickSpy;
  let scrollIntoViewSpy;
  let focusSpy;
  let setIntervalSpy;
  let clearIntervalSpy;
  let fetchMock;

  beforeEach(() => {
    fetchMock = mockDashboardFetch();
    vi.stubGlobal('fetch', fetchMock);
    setIntervalSpy = vi.spyOn(globalThis, 'setInterval').mockImplementation(() => 1);
    clearIntervalSpy = vi.spyOn(globalThis, 'clearInterval').mockImplementation(() => undefined);
    if (!HTMLElement.prototype.scrollIntoView) {
      Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
        configurable: true,
        value: () => undefined,
      });
    }
    if (!HTMLElement.prototype.focus) {
      Object.defineProperty(HTMLElement.prototype, 'focus', {
        configurable: true,
        value: () => undefined,
      });
    }
    if (!URL.createObjectURL) {
      Object.defineProperty(URL, 'createObjectURL', {
        configurable: true,
        value: () => 'blob:report',
      });
    }
    if (!URL.revokeObjectURL) {
      Object.defineProperty(URL, 'revokeObjectURL', {
        configurable: true,
        value: () => undefined,
      });
    }
    scrollIntoViewSpy = vi.spyOn(HTMLElement.prototype, 'scrollIntoView').mockImplementation(() => undefined);
    focusSpy = vi.spyOn(HTMLElement.prototype, 'focus').mockImplementation(() => undefined);
    createObjectURLSpy = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:report');
    revokeObjectURLSpy = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => undefined);
    anchorClickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it('scrolls and focuses the report section when Open report is clicked', async () => {
    render(<App />);
    const openReportButton = await screen.findByRole('button', { name: /open report/i });

    fireEvent.click(openReportButton);

    await waitFor(() => {
      expect(scrollIntoViewSpy).toHaveBeenCalledWith({ behavior: 'smooth', block: 'start' });
      expect(focusSpy).toHaveBeenCalledWith({ preventScroll: true });
    });
  });

  it('downloads json exports once even when repeatedly clicked', async () => {
    let resolveJson;
    fetchMock.mockImplementation((url) => {
      if (url.includes('/api/simulator/export/json')) {
        return new Promise((resolve) => {
          resolveJson = resolve;
        });
      }
      if (url.includes('/api/simulator/export/xml')) {
        return Promise.resolve({ ok: true, json: async () => ({ xml: '<root />' }) });
      }
      if (url.includes('/api/simulator/health')) {
        return Promise.resolve({ ok: true, json: async () => ({ status: 'healthy' }) });
      }
      if (url.includes('/api/simulator/metrics')) {
        return Promise.resolve({ ok: true, json: async () => telemetrySnapshot });
      }
      if (url.includes('/api/simulator/ingest')) {
        return Promise.resolve({ ok: true, json: async () => ({ status: 'ingested' }) });
      }
      if (url.includes('/api/reports/latest')) {
        return Promise.resolve({ ok: true, json: async () => persistedReport });
      }
      return Promise.reject(new Error(`Unexpected fetch: ${url}`));
    });

    render(<App />);
    await screen.findByRole('button', { name: /download json/i });
    fetchMock.mockClear();

    fireEvent.click(screen.getByRole('button', { name: /download json/i }));
    await waitFor(() => expect(screen.getByRole('button', { name: /downloading json/i }).disabled).toBe(true));
    fireEvent.click(screen.getByRole('button', { name: /downloading json/i }));

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith('http://localhost:8000/api/simulator/export/json', { method: 'GET' });

    resolveJson({
      ok: true,
      json: async () => ({ tick: 1, preset: 'default' }),
    });

    await waitFor(() => {
      expect(screen.queryByText(/JSON download started/i)).not.toBeNull();
    });
  });

  it('downloads xml exports and surfaces missing-content failures', async () => {
    fetchMock.mockImplementation((url) => {
      if (url.includes('/api/simulator/export/xml')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({}),
        });
      }
      if (url.includes('/api/simulator/health')) {
        return Promise.resolve({ ok: true, json: async () => ({ status: 'healthy' }) });
      }
      if (url.includes('/api/simulator/metrics')) {
        return Promise.resolve({ ok: true, json: async () => telemetrySnapshot });
      }
      if (url.includes('/api/simulator/export/json')) {
        return Promise.resolve({ ok: true, json: async () => ({}) });
      }
      if (url.includes('/api/simulator/ingest')) {
        return Promise.resolve({ ok: true, json: async () => ({ status: 'ingested' }) });
      }
      if (url.includes('/api/reports/latest')) {
        return Promise.resolve({ ok: true, json: async () => persistedReport });
      }
      return Promise.reject(new Error(`Unexpected fetch: ${url}`));
    });

    render(<App />);
    await screen.findByRole('button', { name: /download xml/i });
    fetchMock.mockClear();

    fireEvent.click(screen.getByRole('button', { name: /download xml/i }));

    await waitFor(() => {
      expect(screen.queryByText(/XML download failed/i)).not.toBeNull();
    });
    expect(createObjectURLSpy).not.toHaveBeenCalled();
  });

  it('creates a pdf download using the latest dashboard telemetry snapshot', async () => {
    render(<App />);
    await screen.findByRole('button', { name: /download pdf/i });
    fetchMock.mockClear();

    const startedAt = performance.now();
    fireEvent.click(screen.getByRole('button', { name: /download pdf/i }));

    await waitFor(() => {
      expect(createObjectURLSpy).toHaveBeenCalled();
    });
    expect(performance.now() - startedAt).toBeLessThan(3000);

    const pdfBlob = createObjectURLSpy.mock.calls[0][0];

    expect(pdfBlob.type).toBe('application/pdf');
    expect(pdfBlob.size).toBeGreaterThan(0);
    expect(screen.queryByText(/PDF download started/i)).not.toBeNull();
  });

  it('renders the persisted database report when it is available', async () => {
    render(<App />);

    const summaryMatches = await screen.findAllByText(/database latency is elevated/i);
    expect(summaryMatches.length).toBeGreaterThanOrEqual(3);
    expect(screen.getAllByText('73').length).toBeGreaterThan(0);
    expect(screen.getByText(/Review query load/i)).toBeTruthy();
    expect(screen.getByText(/Source: Backend/i)).toBeTruthy();
  });
});
