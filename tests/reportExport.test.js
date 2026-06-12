import { describe, expect, it } from 'vitest';
import {
  buildReportPdfBlob,
  buildTelemetrySnapshot,
  formatExportTimestamp,
  formatReadableTimestamp,
} from '../src/utils/reportExport.js';

describe('report export helpers', () => {
  it('formats export filenames with a compact timestamp', () => {
    const timestamp = formatExportTimestamp(new Date('2026-06-12T08:59:04'));
    expect(timestamp).toBe('20260612-085904');
  });

  it('formats generated-at timestamps in a human-readable style', () => {
    const formatted = formatReadableTimestamp(new Date('2026-06-12T08:59:04'));
    expect(formatted).toMatch(/Jun 12, 2026/i);
    expect(formatted).toMatch(/\d{1,2}:\d{2}\s?(AM|PM)/i);
  });

  it('normalizes telemetry snapshots for the pdf export', () => {
    expect(
      buildTelemetrySnapshot([
        { name: 'web', cpu: '17', ram: '512' },
        { name: 'db', cpu: 61.2, ram: 1024.8 },
      ]),
    ).toEqual([
      { name: 'web', cpu: 17, ram: 512 },
      { name: 'db', cpu: 61.2, ram: 1024.8 },
    ]);
  });

  it('builds a valid readable pdf with dashboard sections and telemetry', async () => {
    const blob = buildReportPdfBlob({
      environment: 'PROD',
      generatedAt: new Date('2026-06-12T08:59:04'),
      report: {
        healthScore: 84,
        result: 'One or more subsystem metrics are elevated.',
        summary: 'CPU and RAM stay mostly healthy, but the database and cache are trending upward.',
        areasOfConcern: ['DB Agent: database subsystem under load'],
        suggestedImprovements: ['Review the elevated cpu value and continue monitoring the db subsystem.'],
      },
      telemetrySnapshot: [
        { name: 'web', cpu: 12, ram: 512 },
        { name: 'db', cpu: 74, ram: 2048 },
      ],
    });

    const pdfText = await blob.text();

    expect(pdfText.startsWith('%PDF-1.4')).toBe(true);
    expect(pdfText).toContain('iNTERNS Monitor Report');
    expect(pdfText).toContain('Dashboard summary');
    expect(pdfText).toContain('Telemetry snapshot');
    expect(pdfText).toContain('WEB: CPU 12%, RAM 512 MB');
    expect(pdfText).toContain('DB: CPU 74%, RAM 2048 MB');
    expect(pdfText).toContain('Generated at Jun 12, 2026');
    expect(pdfText).toContain('xref');
    expect(pdfText).toContain('%%EOF');
  });
});
