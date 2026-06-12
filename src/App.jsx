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
import { API_BASE, fetchAgentChecks } from './utils/api.js';
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

function App() {
  const pollingInterval = 2500;
  const [environment, setEnvironment] = useState('PROD');
  const [updatedAt, setUpdatedAt] = useState(new Date());
  const [liveAgents, setLiveAgents] = useState(null); // null = not yet loaded

  //from API
  const [apiHealth, setApiHealth] = useState(null);
  const [apiMetrics, setApiMetrics] = useState(null);
  const [health, setHealth] = useState(null);
  const [loadError, setLoadError] = useState(null);
  const [subsystems, setSubsystems] = useState([]);
  const [backendReports, setBackendReports] = useState({ CI: null, PROD: null });
  const [scoreSources, setScoreSources] = useState({ CI: 'fallback', PROD: 'fallback' });
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
  const report = {
    healthScore: healthSnapshot.healthScore,
    result: healthSnapshot.result,
    summary: healthSnapshot.summary,
    areasOfConcern: healthSnapshot.areasOfConcern,
    suggestedImprovements: healthSnapshot.suggestedImprovements,
  };
  const healthStatus = healthSnapshot.status;
  const healthScore = healthSnapshot.healthScore;
  const summary = healthSnapshot.summary;
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
      healthScore: healthSnapshot.healthScore,
      result: healthSnapshot.result,
      summary: healthSnapshot.summary,
      areasOfConcern: healthSnapshot.areasOfConcern,
      suggestedImprovements: healthSnapshot.suggestedImprovements,
      telemetrySnapshot: buildTelemetrySnapshot(subsystems),
    }),
    [environment, healthSnapshot, subsystems]
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
      setLoadError(null);

      try {
        const [healthResponse, metricsResponse] = await Promise.all([
          fetch('http://localhost:8000/api/simulator/health'),
          fetch('http://localhost:8000/api/simulator/metrics'),
        ]);

        if (!healthResponse.ok || !metricsResponse.ok) {
          throw new Error(`Telemetry fetch failed (health=${healthResponse.status}, metrics=${metricsResponse.status})`);
        }

        const [healthRes, metricsRes] = await Promise.all([
          healthResponse.json(),
          metricsResponse.json(),
        ]);

        setHealth(healthRes);
        setApiHealth(healthRes);
        setApiMetrics(metricsRes);

        // Convert subsystems object -> array.
        const subsystemAgents = Object.entries(metricsRes?.subsystems || {}).map(
          ([name, stats]) => ({ name, ...stats }),
        );

        setSubsystems(subsystemAgents);
      } catch (error) {
        setLoadError(error instanceof Error ? error.message : 'Failed to load telemetry');
        setApiHealth(null);
        setApiMetrics(null);
        setHealth(null);
        setSubsystems([]);
      } finally {
        setLoading(false);
      }
  }

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    let active = true;

    const safeLoadData = async () => {
      if (!active) return;
      await loadData();
      if (!active) return;
      setUpdatedAt(new Date());
    };

    safeLoadData();

    const timer = setInterval(() => {
      safeLoadData();
    }, pollingInterval);

    return () => {
      active = false;
      clearInterval(timer);
    };
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
      />
      <PageShell>
        <div className="space-y-10">
          <HealthSummary
            status={healthStatus}
            score={healthScore}
            activeAlerts={activeAlerts.length}
            environment={environment}
            summary={summary}
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
                report={report}
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
