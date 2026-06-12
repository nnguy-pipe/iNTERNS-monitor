import { useEffect, useMemo, useState } from 'react';
import TopNav from './components/layout/TopNav.jsx';
import PageShell from './components/layout/PageShell.jsx';
import HealthSummary from './components/dashboard/HealthSummary.jsx';
import AgentGrid from './components/dashboard/AgentGrid.jsx';
import MetricsPanel from './components/dashboard/MetricsPanel.jsx';
import AlertsFeed from './components/dashboard/AlertsFeed.jsx';
import AlertDetailsDrawer from './components/dashboard/AlertDetailsDrawer.jsx';
import ReportPreview from './components/dashboard/ReportPreview.jsx';
import RecommendedNextSteps from './components/dashboard/RecommendedNextSteps.jsx';
import mockSkills from './data/mockSkills.js';
import { deriveHealthSnapshot } from './utils/health.js';
import { API_BASE, fetchAgentChecks, fetchLatestReport, ingestSimulatorMetrics } from './utils/api.js';
import {
  buildReportPdfBlob,
  buildTelemetrySnapshot,
  formatExportTimestamp,
  formatReadableTimestamp,
  openReportSection,
} from './utils/reportExport.js';

const environments = ['CI', 'PROD'];

// Mapping from backend agent identifiers to frontend display metadata
const AGENT_META = {
  infrastructure: { name: 'Infrastructure Agent', scope: 'Cloud infrastructure and network health' },
  memory: { name: 'Memory Agent', scope: 'Heap and container memory pressure' },
  cpu: { name: 'CPU Agent', scope: 'CPU load and core utilization' },
  ci: { name: 'CI/CD Agent', scope: 'Pipeline and merge health' },
  api: { name: 'API Agent', scope: 'Public endpoint latency and availability' },
};

const STATUS_LABEL = { healthy: 'Healthy', warning: 'Warning', critical: 'Critical', unknown: 'Unknown' };
const STATUS_CONFIDENCE = { healthy: 97, warning: 72, critical: 38, unknown: 50 };
const SCORE_SYSTEM_NAME = 'iMonitor';
const REPORT_RESULT = {
  healthy: 'All monitored subsystems are within safe operating ranges.',
  warning: 'One or more subsystem metrics are elevated.',
  critical: 'One or more subsystems need immediate attention.',
  unknown: 'Latest persisted report is unavailable.',
};

function mapReportStatus(status) {
  if (status === 'healthy') return 'Healthy';
  if (status === 'warning') return 'Degraded';
  if (status === 'critical') return 'Critical';
  return 'Degraded';
}

function formatLastChecked(isoTimestamp) {
  try {
    const diffSec = Math.round((Date.now() - new Date(isoTimestamp).getTime()) / 1000);
    if (diffSec < 5) return 'just now';
    if (diffSec < 60) return `${diffSec} sec ago`;
    return `${Math.floor(diffSec / 60)} min ago`;
  } catch {
    return 'recently';
  }
}

function mapBackendAgents(backendAgents) {
  return backendAgents.map((a) => {
    const meta = AGENT_META[a.agent] || { name: a.agent, scope: '' };
    return {
      name: meta.name,
      scope: meta.scope,
      status: STATUS_LABEL[a.status] || 'Unknown',
      latestFinding: a.latest_finding || 'No data',
      lastChecked: formatLastChecked(a.last_checked),
      confidenceScore: STATUS_CONFIDENCE[a.status] ?? 50,
    };
  });
}

function buildFallbackReport(healthSnapshot) {
  return {
    healthScore: healthSnapshot.healthScore,
    result: healthSnapshot.result,
    summary: healthSnapshot.summary,
    areasOfConcern: healthSnapshot.areasOfConcern,
    suggestedImprovements: healthSnapshot.suggestedImprovements,
  };
}

function buildDisplayReport(backendReport, fallbackReport) {
  if (!backendReport) return fallbackReport;

  const status = backendReport.status || 'unknown';
  const primaryIssue =
    typeof backendReport.primary_issue === 'string' && backendReport.primary_issue.trim()
      ? backendReport.primary_issue.trim()
      : 'No primary issue recorded';
  const suggestions = Array.isArray(backendReport.suggestions) && backendReport.suggestions.length
    ? backendReport.suggestions.filter((item) => typeof item === 'string' && item.trim())
    : ['Continue monitoring the persisted report.'];

  return {
    healthScore: Math.round(Number(backendReport.health_score ?? fallbackReport.healthScore)),
    result: REPORT_RESULT[status] || REPORT_RESULT.unknown,
    summary:
      status === 'healthy'
        ? 'The latest persisted report indicates the environment is healthy.'
        : `The latest persisted report highlights ${primaryIssue}.`,
    areasOfConcern: [primaryIssue],
    suggestedImprovements: suggestions.length ? suggestions : ['Continue monitoring the persisted report.'],
  };
}

function App() {
  const pollingInterval = 2500;
  const [environment, setEnvironment] = useState('PROD');
  const [updatedAt, setUpdatedAt] = useState(new Date());
  const [liveAgents, setLiveAgents] = useState(null); // null = not yet loaded

  const [health, setHealth] = useState(null);
  const [subsystems, setSubsystems] = useState([]);
  const [backendReports, setBackendReports] = useState({ CI: null, PROD: null });
  const [loading, setLoading] = useState(true);
  const [reportExportBusy, setReportExportBusy] = useState({
    pdf: false,
    json: false,
    xml: false,
  });
  const [exportFeedback, setExportFeedback] = useState({ type: 'idle', message: '' });
  const [selectedAlert, setSelectedAlert] = useState(null);
  const healthSnapshot = useMemo(() => deriveHealthSnapshot(subsystems), [subsystems]);
  const activeAlerts = healthSnapshot.alerts;
  const fallbackReport = useMemo(() => buildFallbackReport(healthSnapshot), [healthSnapshot]);
  const displayReport = useMemo(
    () => buildDisplayReport(backendReports[environment], fallbackReport),
    [backendReports, environment, fallbackReport]
  );
  const healthStatus = healthSnapshot.status;
  const healthScore = displayReport.healthScore;
  const summary = displayReport.summary;
  const skills = mockSkills[environment] || [];

  function triggerDownload(blob, filename) {
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  function setExportBusy(format, isBusy) {
    setReportExportBusy((current) => ({ ...current, [format]: isBusy }));
  }

  function setExportMessage(type, message) {
    setExportFeedback({ type, message });
  }

  function openReport() {
    if (!openReportSection(document)) {
      setExportMessage('error', 'Report section is not available right now.');
    }
  }

  const reportSnapshot = useMemo(
    () => ({
      environment,
      healthScore: displayReport.healthScore,
      result: displayReport.result,
      summary: displayReport.summary,
      areasOfConcern: displayReport.areasOfConcern,
      suggestedImprovements: displayReport.suggestedImprovements,
      telemetrySnapshot: buildTelemetrySnapshot(subsystems),
    }),
    [displayReport, environment, subsystems]
  );

  async function downloadPdfReport() {
    if (reportExportBusy.pdf) return;
    const exportMoment = new Date();
    const timestamp = formatExportTimestamp(exportMoment);
    setExportBusy('pdf', true);
    try {
      const blob = buildReportPdfBlob({
        environment,
        generatedAt: exportMoment,
        report: reportSnapshot,
        telemetrySnapshot: reportSnapshot.telemetrySnapshot,
      });
      triggerDownload(blob, `report-${environment.toLowerCase()}-${timestamp}.pdf`);
      setExportMessage('success', `PDF download started (${formatReadableTimestamp(exportMoment)}).`);
    } finally {
      setExportBusy('pdf', false);
    }
  }

  async function downloadSimulatorJson() {
    if (reportExportBusy.json) return;
    const timestamp = formatExportTimestamp();
    setExportBusy('json', true);
    try {
      const response = await fetch(`${API_BASE}/api/simulator/export/json`, { method: 'GET' });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const payload = await response.json();
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
      triggerDownload(blob, `simulator-${environment.toLowerCase()}-${timestamp}.json`);
      setExportMessage('success', `JSON download started (${timestamp}).`);
    } catch (error) {
      setExportMessage('error', `JSON download failed: ${error.message}`);
    } finally {
      setExportBusy('json', false);
    }
  }

  async function downloadSimulatorXml() {
    if (reportExportBusy.xml) return;
    const timestamp = formatExportTimestamp();
    setExportBusy('xml', true);
    try {
      const response = await fetch(`${API_BASE}/api/simulator/export/xml`, { method: 'GET' });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const payload = await response.json();
      if (!payload.xml) {
        throw new Error('Response did not include XML content');
      }
      const blob = new Blob([payload.xml], { type: 'application/xml' });
      triggerDownload(blob, `simulator-${environment.toLowerCase()}-${timestamp}.xml`);
      setExportMessage('success', `XML download started (${timestamp}).`);
    } catch (error) {
      setExportMessage('error', `XML download failed: ${error.message}`);
    } finally {
      setExportBusy('xml', false);
    }
  }

  // fetch/ load data function
  async function loadData() {
      setLoading(true);

      try {
        const [healthRes, metricsRes] = await Promise.all([
          fetch('http://localhost:8000/api/simulator/health').then((r) => r.json()),
          fetch('http://localhost:8000/api/simulator/metrics').then((r) => r.json()),
        ]);

        setHealth(healthRes);

        // Convert subsystems object -> array
        const subsystemAgents = Object.entries(metricsRes?.subsystems || {}).map(
          ([name, stats]) => ({ name, ...stats }),
        );
        setSubsystems(subsystemAgents);

        try {
          await ingestSimulatorMetrics(SCORE_SYSTEM_NAME, environment);
        } catch {
          // Keep going even if simulator ingestion is unavailable; an existing report may still be readable.
        }

        try {
          const latestReport = await fetchLatestReport(SCORE_SYSTEM_NAME, environment);
          setBackendReports((prev) => ({ ...prev, [environment]: latestReport }));
        } catch {
          // Keep the existing report if the database-backed lookup is unavailable.
        }
      } finally {
        setLoading(false);
      }
  }
  useEffect(() => {
    loadData();

    const timer = setInterval(() => {
      loadData();
      setUpdatedAt(new Date());
    }, pollingInterval);

    return () => clearInterval(timer);
  }, [environment]);

  // Poll backend agent checks; fall back silently to mock data when unavailable
  useEffect(() => {
    let active = true;

    async function pollAgents() {
      try {
        const data = await fetchAgentChecks();
        if (!active || !data.agents) return;
        setLiveAgents(mapBackendAgents(data.agents));
      } catch {
        // backend unavailable — keep using mock data
        if (active) setLiveAgents(null);
      }
    }

    const id = setInterval(pollAgents, 10000);
    pollAgents();

    return () => { active = false; clearInterval(id); };
  }, []);

  useEffect(() => {
    if (!selectedAlert) return;
    const stillActive = activeAlerts.find((alert) => alert.id === selectedAlert.id);
    if (!stillActive) {
      setSelectedAlert(null);
    }
  }, [activeAlerts, selectedAlert]);

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <TopNav
        environment={environment}
        environments={environments}
        onEnvironmentChange={setEnvironment}
        lastUpdated={updatedAt}
        status={healthStatus}
      />
      <PageShell>
        <div className="space-y-10">
          <HealthSummary
            status={healthStatus}
            score={healthScore}
            activeAlerts={activeAlerts.length}
            environment={environment}
            summary={summary}
            scoreSource={backendReports[environment] ? 'backend' : 'fallback'}
            onOpenReport={openReport}
          />

          <section id="agents" className="space-y-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-600">Agent status</p>
                <h2 className="mt-2 text-2xl font-semibold text-slate-900">Monitoring agents</h2>
              </div>
              <p className="text-sm text-slate-500">Current environment: {environment}</p>
            </div>
            <AgentGrid agents={subsystems} />
          </section>

          <AlertsFeed alerts={activeAlerts} onSelectAlert={setSelectedAlert} />

          <section className="grid gap-6 lg:grid-cols-12 items-start">
            <div className="lg:col-span-8">
              <ReportPreview
                report={displayReport}
                onDownloadPdf={downloadPdfReport}
                onDownloadJson={downloadSimulatorJson}
                onDownloadXml={downloadSimulatorXml}
                exportStatus={{
                  busy: reportExportBusy,
                  type: exportFeedback.type,
                  message: exportFeedback.message,
                }}
              />
            </div>
            <div className="lg:col-span-4">
              <RecommendedNextSteps skills={skills} />
            </div>
          </section>

          <MetricsPanel subsystems={subsystems} />

          <AlertDetailsDrawer
            alert={selectedAlert}
            isOpen={Boolean(selectedAlert)}
            onClose={() => setSelectedAlert(null)}
          />
        </div>
      </PageShell>
    </div>
  );
}

export default App;
