const PDF_PAGE_WIDTH = 612;
const PDF_PAGE_HEIGHT = 792;
const PDF_MARGIN = 36;
const CARD_GAP = 16;

function escapePdfText(value) {
  return String(value).replace(/\\/g, '\\\\').replace(/\(/g, '\\(').replace(/\)/g, '\\)');
}

function wrapText(value, maxChars) {
  const words = String(value).split(/\s+/).filter(Boolean);
  if (words.length === 0) return [''];

  const lines = [];
  let current = words[0];

  for (const word of words.slice(1)) {
    if ((current + ' ' + word).length <= maxChars) {
      current += ` ${word}`;
    } else {
      lines.push(current);
      current = word;
    }
  }

  lines.push(current);
  return lines;
}

export function formatExportTimestamp(date = new Date()) {
  const pad = (value) => String(value).padStart(2, '0');
  return `${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(date.getDate())}-${pad(date.getHours())}${pad(
    date.getMinutes(),
  )}${pad(date.getSeconds())}`;
}

export function formatReadableTimestamp(date = new Date()) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
  }).format(date);
}

export function buildTelemetrySnapshot(subsystems = []) {
  return subsystems.map((subsystem) => ({
    name: subsystem?.name || 'Subsystem',
    cpu: Number(subsystem?.cpu ?? 0),
    ram: Number(subsystem?.ram ?? 0),
  }));
}

export function openReportSection(doc = document) {
  const reportSection = doc?.getElementById?.('reports');
  if (!reportSection) return false;

  reportSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  reportSection.focus({ preventScroll: true });
  return true;
}

function createTextBlock(lines, x, y, fontSize, color = '0 0 0') {
  return lines
    .map(
      (line, index) =>
        `BT /F1 ${fontSize} Tf ${color} rg 1 0 0 1 ${x} ${y - index * (fontSize + 2)} Tm (${escapePdfText(line)}) Tj ET`,
    )
    .join('\n');
}

function drawCard({ x, y, width, height, title, lines, accent = '0.05 0.55 0.85', fill = '0.97 0.98 1' }) {
  const bodyY = y + height - 24;
  const bodyLines = Array.isArray(lines) ? lines : [String(lines)];
  return [
    `${fill} rg ${x} ${y} ${width} ${height} re f`,
    `0.82 0.86 0.92 RG 0.8 w ${x} ${y} ${width} ${height} re S`,
    `${accent} rg ${x} ${y + height - 10} ${width} 4 re f`,
    createTextBlock([title], x + 14, bodyY, 13, '0.09 0.13 0.2'),
    createTextBlock(bodyLines, x + 14, bodyY - 18, 10, '0.22 0.27 0.33'),
  ]
    .filter(Boolean)
    .join('\n');
}

export function buildReportPdfBlob({ environment, generatedAt = new Date(), report, telemetrySnapshot = [] , healthStatus = 'Unknown'}) {
  const readableTimestamp = formatReadableTimestamp(generatedAt);
  const healthLines = [
    `Health score: ${report.healthScore}/100`,
    `Status: ${healthStatus}`,
  ];
  const fullReport = `Result: ${report.result}` + report.summary
  const summaryLines = wrapText(fullReport, 110);
  const telemetryLines = telemetrySnapshot.length
    ? telemetrySnapshot.flatMap((row) => [`${row.name.toUpperCase()}: CPU ${Math.round(row.cpu)}%, RAM ${Math.round(row.ram)} MB`])
    : ['No telemetry snapshot was available at export time.'];
  const concernLines = report.areasOfConcern.length
    ? report.areasOfConcern.flatMap((item) => wrapText(`- ${item}`, 50))
    : ['• None'];
  const improvementLines = report.suggestedImprovements.length
    ? report.suggestedImprovements.flatMap((item) => wrapText(`- ${item}`, 50))
    : ['• None'];

  const content = [
    '0.12 0.22 0.39 rg 36 724 540 50 re f',
    createTextBlock(['iNTERNS Monitor Report'], 52, 744, 18, '1 1 1'),
    createTextBlock([`${environment} - Generated at ${readableTimestamp}`], 52, 728, 10, '0.9 0.95 1'),
    drawCard({
      x: 36,
      y: 632,
      width: 168,
      height: 70,
      title: 'Health snapshot',
      lines: healthLines,
    }),
    drawCard({
      x: 222,
      y: 632,
      width: 168,
      height: 70,
      title: 'Export metadata',
      lines: [`Environment: ${environment}`],
      accent: '0.16 0.63 0.36',
      fill: '0.96 0.99 0.97',
    }),
    drawCard({
      x: 408,
      y: 632,
      width: 168,
      height: 70,
      title: 'Report status',
      lines: wrapText(`Snapshot captured from the latest successful database read.`, 30),
      accent: '0.45 0.35 0.9',
      fill: '0.97 0.96 1',
    }),
    drawCard({
      x: 36,
      y: 500,
      width: 540,
      height: 112,
      title: 'Dashboard summary',
      lines: summaryLines,
      fill: '0.99 0.99 0.99',
      accent: '0.05 0.55 0.85',
    }),
    drawCard({
      x: 36,
      y: 348,
      width: 540,
      height: 132,
      title: `Telemetry snapshot (${readableTimestamp})`,
      lines: telemetryLines,
      fill: '0.96 0.98 1',
      accent: '0.14 0.45 0.9',
    }),
    drawCard({
      x: 36,
      y: 150,
      width: 260,
      height: 180,
      title: 'Areas of concern',
      lines: concernLines,
      fill: '1 0.99 0.96',
      accent: '0.85 0.49 0.03',
    }),
    drawCard({
      x: 316,
      y: 150,
      width: 260,
      height: 180,
      title: 'Suggested improvements',
      lines: improvementLines,
      fill: '0.97 0.99 0.96',
      accent: '0.16 0.63 0.36',
    }),
  ].join('\n');

  const objects = [];
  const offsets = [0];
  let pdf = '%PDF-1.4\n';

  objects.push('<< /Type /Catalog /Pages 2 0 R >>');
  objects.push('<< /Type /Pages /Kids [3 0 R] /Count 1 >>');
  objects.push(
    `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${PDF_PAGE_WIDTH} ${PDF_PAGE_HEIGHT}] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>`,
  );
  objects.push('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>');
  objects.push(`<< /Length ${content.length} >>\nstream\n${content}\nendstream`);

  objects.forEach((object, index) => {
    offsets.push(pdf.length);
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
  });

  const xrefOffset = pdf.length;
  pdf += `xref\n0 ${objects.length + 1}\n`;
  pdf += '0000000000 65535 f \n';
  for (let i = 1; i < offsets.length; i += 1) {
    pdf += `${String(offsets[i]).padStart(10, '0')} 00000 n \n`;
  }
  pdf += `trailer << /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`;

  return new Blob([pdf], { type: 'application/pdf' });
}
