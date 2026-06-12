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
import {
  API_BASE,
  fetchAgentChecks,
  fetchSimulatorMetrics,
  fetchUserReport,
  ingestSimulatorSnapshot,
} from './utils/api.js';
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
  users: { name: 'User Agent', scope: 'Active-user load and concurrency health' },
  ci: { name: 'CI/CD Agent', scope: 'Pipeline and merge health' },
  api: { name: 'API Agent', scope: 'Public endpoint latency and availability' },
};

const STATUS_LABEL = { healthy: 'Healthy', warning: 'Warning', critical: 'Critical', unknown: 'Unknown' };
const DASHBOARD_SYSTEM_NAME = import.meta.env.VITE_SYSTEM_NAME || 'infra-demo';
const ENV_TO_BACKEND = { CI: 'ci', PROD: 'production' };
const STATUS_RANK = { Healthy: 0, Degraded: 1, Critical: 2 };

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
      type: 'agent',
    };
  });
}

function normalizeHealthScore(value) {
  const score = Number(value);
  if (Number.isNaN(score)) return 50;
  return Math.max(0, Math.min(100, score <= 1 ? score * 100 : score));
}

function deriveSubsystemStatus(metrics) {
  const cpu = Number(metrics?.cpu || 0);
  const ram = Number(metrics?.ram || 0);
  const users = Number(metrics?.active_users || 0);
  const eventSpike = Number(metrics?.event_spike || 0);
  if (cpu >= 85 || ram >= 3500 || users >= 80 || eventSpike >= 4) return 'Critical';
  if (cpu >= 60 || ram >= 2200 || users >= 40 || eventSpike > 0) return 'Warning';
  return 'Healthy';
}

function mapSimulatorAgents(metrics) {
  const subsystems = metrics?.subsystems || {};
  const checkedAt = Number(metrics?.timestamp)
    ? formatLastChecked(new Date(Number(metrics.timestamp) * 1000).toISOString())
    : 'just now';
  const preset = metrics?.preset || 'default';

  return Object.entries(subsystems).map(([name, values]) => ({
    name,
    scope: `${name.toUpperCase()} subsystem daemon telemetry`,
    status: deriveSubsystemStatus(values),
    latestFinding: `Daemon: preset ${preset}, cpu ${Number(values?.cpu || 0).toFixed(1)}%, ram ${Math.round(
      Number(values?.ram || 0),
    )} MB, active users ${Number(values?.active_users || 0)}`,
    lastChecked: checkedAt,
    cpu: values?.cpu,
    ram: values?.ram,
    active_users: values?.active_users,
    external_load: values?.external_load,
    event_spike: values?.event_spike,
    type: 'subsystem',
  }));
}

function mapBackendReport(backendReport, environment) {
  const score = Number(backendReport?.health_score ?? 0.5);
  const status = (backendReport?.status || 'unknown').toLowerCase();
  const primaryIssue = backendReport?.primary_issue || '';
  const suggestionsRaw = (backendReport?.suggestions || [])
    .map((s) => (typeof s === 'string' ? s : s?.action))
    .filter(Boolean);
  const suggestions = environment === 'PROD'
    ? suggestionsRaw.filter((s) => !/\bci\b/i.test(s))
    : suggestionsRaw;

  const anomalyConcerns = (backendReport?.anomalies || [])
    .map((a) => a?.reason)
    .filter(Boolean)
    .filter((s) => (environment === 'PROD' ? !/\bci\b/i.test(s) : true))
    .slice(0, 3);

  const areasOfConcern = [primaryIssue, ...anomalyConcerns]
    .filter(Boolean)
    .filter((s) => (environment === 'PROD' ? !/\bci\b/i.test(s) : true));

  const reasoningItems = (backendReport?.reasoning?.reasoning_chain || [])
    .map((s) => String(s))
    .filter((s) => (environment === 'PROD' ? !/\bci\b/i.test(s) : true));

  const correlatedEvents = (backendReport?.correlated_events || [])
    .map((s) => String(s));

  const anomalyItems = (backendReport?.anomalies || [])
    .map((a) => ({
      severity: (a?.severity || 'medium').toString(),
      reason: (a?.reason || 'Anomaly detected').toString(),
      rule: a?.rule || a?.type || 'pattern',
    }))
    .filter((a) => (environment === 'PROD' ? !/\bci\b/i.test(a.reason) : true));

  let result = (backendReport?.status || 'unknown').toString().toUpperCase();
  let summary = primaryIssue || 'No primary issue identified in the latest backend report.';

  if (environment === 'CI') {
    if (status === 'healthy') {
      result = 'CI SUCCESS';
      summary = 'CI checks succeeded. No blocking failures detected in the latest assessment.';
    } else if (status === 'warning' || status === 'critical') {
      result = 'CI FAILED';
      summary = primaryIssue
        ? `CI failed due to: ${primaryIssue}`
        : 'CI is degraded with failing checks. Review logs and traces for the failing stage.';
    } else {
      result = 'CI UNKNOWN';
      summary = 'CI status is unknown because there are not enough recent CI events.';
    }
  } else if (environment === 'PROD') {
    if (status === 'healthy') {
      result = 'PROD STABLE';
      summary = 'Production is stable. No active production-impacting issues were detected.';
    } else if (status === 'warning' || status === 'critical') {
      result = 'PROD DEGRADED';
      summary = primaryIssue
        ? `Production issue: ${primaryIssue}`
        : 'Production is degraded. Investigate infrastructure, API latency, and error telemetry.';
    } else {
      result = 'PROD UNKNOWN';
      summary = 'Production status is unknown due to limited recent production telemetry.';
    }
  }

  return {
    healthScore: Math.round(normalizeHealthScore(score)),
    result,
    summary,
    areasOfConcern: areasOfConcern.length ? areasOfConcern : ['No high-priority concerns detected.'],
    suggestedImprovements: suggestions.length ? suggestions : ['Continue monitoring and review incoming telemetry.'],
    attachedReport: backendReport?.report_markdown || '',
    backendStatus: backendReport?.status || 'unknown',
    reasoningItems,
    correlatedEvents,
    anomalyItems,
    source: 'backend',
    createdAt: backendReport?.created_at || null,
  };
}

function mapReportToAlerts(report, environment) {
  if (!report) return [];

  const alerts = [];
  const status = String(report.backendStatus || '').toLowerCase();

  if (report.summary && report.summary !== 'No primary issue identified in the latest backend report.') {
    alerts.push({
      severity: status === 'critical' ? 'Critical' : status === 'warning' ? 'High' : 'Low',
      title: environment === 'CI' ? 'CI health finding' : 'Production health finding',
      environment,
      sourceAgent: 'Reasoning Engine',
      affectedResource: environment === 'CI' ? 'CI pipeline' : 'Production services',
      timestamp: report.createdAt ? formatLastChecked(report.createdAt) : 'recently',
      summary: report.summary,
      reasoning: (report.reasoningItems || []).join(' ') || report.summary,
      suggestedActions: (report.suggestedImprovements || []).join(', '),
      relatedSkill: environment === 'CI' ? 'CI Health Gate Review' : 'Production Incident Review',
      confidence: status === 'critical' ? 92 : status === 'warning' ? 84 : 76,
      status: 'Open',
    });
  }

  (report.anomalyItems || []).slice(0, 3).forEach((item, index) => {
    alerts.push({
      severity: String(item.severity).toLowerCase() === 'high' ? 'High' : 'Medium',
      title: `Anomaly detected: ${item.rule}`,
      environment,
      sourceAgent: 'Anomaly Engine',
      affectedResource: environment === 'CI' ? 'CI telemetry' : 'Production telemetry',
      timestamp: report.createdAt ? formatLastChecked(report.createdAt) : 'recently',
      summary: item.reason,
      reasoning: item.reason,
      suggestedActions: (report.suggestedImprovements || []).join(', '),
      relatedSkill: 'Anomaly Investigation',
      confidence: 80 - index * 5,
      status: 'Open',
    });
  });

  return alerts;
}

function deriveBackendReportFallback(agentChecks, metrics, environment) {
  const checks = Array.isArray(agentChecks) ? agentChecks : [];
  const scoreByStatus = { healthy: 95, warning: 72, critical: 35, unknown: 55 };

  const backendScoreFromAgents = checks.length
    ? Math.round(
      checks.reduce((sum, item) => {
        const statusKey = String(item?.status || 'unknown').toLowerCase();
        return sum + (scoreByStatus[statusKey] ?? 55);
      }, 0) / checks.length,
    )
    : null;

  const backendScoreFromMetrics = metrics?.subsystems
    ? Math.round(
      Object.values(metrics.subsystems).reduce((sum, row) => sum + Number(row?.cpu || 0), 0) /
        Math.max(1, Object.keys(metrics.subsystems).length),
    )
    : 60;

  const healthScore = backendScoreFromAgents ?? backendScoreFromMetrics;

  const criticalFinding = checks.find((item) => String(item?.status || '').toLowerCase() === 'critical');
  const warningFinding = checks.find((item) => String(item?.status || '').toLowerCase() === 'warning');
  const topFinding = criticalFinding || warningFinding;

  const summary = topFinding?.latest_finding
    ? String(topFinding.latest_finding)
    : environment === 'CI'
      ? 'Backend telemetry is active and CI health checks are being evaluated.'
      : 'Backend telemetry is active and production health checks are being evaluated.';

  return {
    healthScore,
    result: environment === 'CI' ? 'CI BACKEND STATUS' : 'PROD BACKEND STATUS',
    summary,
    areasOfConcern: topFinding?.latest_finding ? [String(topFinding.latest_finding)] : ['No high-priority concerns detected.'],
    suggestedImprovements: ['Review live backend agent findings and continue monitoring telemetry trends.'],
    attachedReport: '',
    backendStatus: criticalFinding ? 'critical' : warningFinding ? 'warning' : 'healthy',
    reasoningItems: topFinding?.latest_finding ? [String(topFinding.latest_finding)] : [],
    correlatedEvents: [],
    anomalyItems: [],
    source: 'backend',
    createdAt: new Date().toISOString(),
  };
}

function deriveTelemetryStatus(metrics) {
  const subsystems = metrics?.subsystems || {};
  const rows = Object.values(subsystems);
  if (!rows.length) return null;

  const avgCpu = rows.reduce((sum, row) => sum + Number(row?.cpu || 0), 0) / rows.length;
  const maxCpu = Math.max(...rows.map((row) => Number(row?.cpu || 0)));
  const maxRam = Math.max(...rows.map((row) => Number(row?.ram || 0)));
  const preset = String(metrics?.preset || '').toLowerCase();

  if (maxCpu >= 90 || avgCpu >= 80 || maxRam >= 1800) return 'Critical';
  if (preset.startsWith('high_') || avgCpu >= 55 || maxRam >= 1400) return 'Degraded';
  return 'Healthy';
}

function maxStatus(a, b) {
  const rankA = STATUS_RANK[a] ?? 0;
  const rankB = STATUS_RANK[b] ?? 0;
  return rankA >= rankB ? a : b;
}

function App() {
  const pollingInterval = 5000;
  const [environment, setEnvironment] = useState('PROD');
  const [updatedAt, setUpdatedAt] = useState(new Date());
  const [agentChecks, setAgentChecks] = useState([]);
  const [apiMetrics, setApiMetrics] = useState(null);
  const [subsystems, setSubsystems] = useState([]);
  const [liveReport, setLiveReport] = useState(null);
  const [liveTelemetryStatus, setLiveTelemetryStatus] = useState(null);
  const [liveAlerts, setLiveAlerts] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [reportExportBusy, setReportExportBusy] = useState({
    report: false,
    pdf: false,
    json: false,
    xml: false,
  });
  const [exportFeedback, setExportFeedback] = useState({ type: 'idle', message: '' });
  const healthSnapshot = useMemo(() => deriveHealthSnapshot(subsystems), [subsystems]);
  const healthStatus = healthSnapshot.status || 'Unknown';
  const skills = mockSkills[environment] || [];
  const report = useMemo(
    () => liveReport || deriveBackendReportFallback(agentChecks, apiMetrics, environment),
    [liveReport, agentChecks, apiMetrics, environment],
  );
  const activeAlerts = useMemo(
    () => (liveAlerts.length ? liveAlerts : mapReportToAlerts(report, environment)),
    [liveAlerts, report, environment],
  );

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

  const healthScore = report?.healthScore ?? 60;
  const summary = report?.summary ?? 'Live backend report unavailable. Ingest events to generate assessment.';

  const reportSnapshot = useMemo(
    () => ({
      environment,
      healthScore,
      result: report?.result || `${environment} PENDING`,
      summary,
      areasOfConcern: report?.areasOfConcern || [],
      suggestedImprovements: report?.suggestedImprovements || [],
      telemetrySnapshot: buildTelemetrySnapshot(subsystems),
    }),
    [environment, healthScore, report, subsystems, summary],
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

  async function downloadMarkdownReport() {
    if (reportExportBusy.report) return;
    setExportBusy('report', true);
    try {
      const backendEnvironment = ENV_TO_BACKEND[environment] || 'production';
      const latest = await fetchUserReport(DASHBOARD_SYSTEM_NAME, backendEnvironment);
      const markdown = latest?.report_markdown || report?.attachedReport || '';
      if (!markdown) {
        throw new Error('No report content available');
      }

      const dateTag = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-');
      const fileName = `${DASHBOARD_SYSTEM_NAME}-${backendEnvironment}-report-${dateTag}.md`;
      const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
      triggerDownload(blob, fileName);
      setExportMessage('success', `Report download started (${formatReadableTimestamp(new Date())}).`);
    } catch (error) {
      setExportMessage('error', `Report download failed: ${error.message}`);
    } finally {
      setExportBusy('report', false);
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

  // Poll backend agent checks from DB for health findings.
  useEffect(() => {
    let active = true;

    async function pollAgents() {
      try {
        const data = await fetchAgentChecks();
        if (!active || !data.agents) return;
        setAgentChecks(data.agents);
      } catch {
        if (active) setAgentChecks([]);
      }
    }

    const id = setInterval(pollAgents, 60000);
    pollAgents();

    return () => { active = false; clearInterval(id); };
  }, []);

  // Poll simulator daemon for live card metrics and top-line telemetry status.
  useEffect(() => {
    let active = true;

    async function pollMetrics() {
      try {
        const metrics = await fetchSimulatorMetrics();
        if (!active) return;
        setApiMetrics(metrics);
        setSubsystems(
          Object.entries(metrics?.subsystems || {}).map(([name, stats]) => ({
            name,
            ...stats,
          })),
        );
        setLiveTelemetryStatus(deriveTelemetryStatus(metrics));
        setUpdatedAt(new Date());
      } catch {
        if (active) setLiveTelemetryStatus(null);
      }
    }

    pollMetrics();
    const id = setInterval(pollMetrics, pollingInterval);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function loadReport() {
      const backendEnvironment = ENV_TO_BACKEND[environment] || 'production';
      try {
        await ingestSimulatorSnapshot(DASHBOARD_SYSTEM_NAME, backendEnvironment);
      } catch {
        // Keep going; existing DB reports may still be available.
      }

      try {
        const report = await fetchUserReport(DASHBOARD_SYSTEM_NAME, backendEnvironment);
        if (!active) return;
        const mapped = mapBackendReport(report, environment);
        setLiveReport(mapped);
        setLiveAlerts(mapReportToAlerts(mapped, environment));
      } catch {
        if (active) {
          setLiveReport(null);
          setLiveAlerts([]);
        }
      }
    }

    loadReport();
    const id = setInterval(loadReport, 60000);

    return () => {
      active = false;
      clearInterval(id);
    };
  }, [environment]);

  const currentAgents = useMemo(() => {
    const backendAgents = mapBackendAgents(agentChecks);
    const daemonAgents = apiMetrics?.subsystems ? mapSimulatorAgents(apiMetrics) : [];
    return [...backendAgents, ...daemonAgents];
  }, [agentChecks, apiMetrics]);

  // useEffect(() => {
  //   // Auto-open the critical alert in PROD to guide the demo story
  //   if (environment === 'PROD') {
  //     const critical = (activeAlerts || []).find((a) => a.severity === 'Critical');
  //     if (critical) setSelectedAlert(critical);
  //   } else {
  //     setSelectedAlert(null);
  //   }
  // }, [environment, activeAlerts]);

  const overallHealthStatus = liveTelemetryStatus
    ? maxStatus(healthStatus, liveTelemetryStatus)
    : healthStatus;

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <TopNav
        environment={environment}
        environments={environments}
        onEnvironmentChange={setEnvironment}
        lastUpdated={updatedAt}
        overallStatus={overallHealthStatus}
      />
      <PageShell>
        <div className="space-y-10">
          <HealthSummary
            score={healthScore}
            activeAlerts={activeAlerts.length}
            environment={environment}
            summary={summary}
            scoreSource={report?.source || 'fallback'}
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
            <AgentGrid agents={currentAgents} />
          </section>

          <AlertsFeed alerts={activeAlerts} onSelectAlert={setSelectedAlert} />

          <section className="grid gap-6 lg:grid-cols-12 items-start">
            <div className="lg:col-span-8">
              <ReportPreview report={report || {
                healthScore,
                result: `${environment} PENDING`,
                summary,
                areasOfConcern: [],
                suggestedImprovements: [],
                reasoningItems: [],
                correlatedEvents: [],
                anomalyItems: [],
                attachedReport: '',
              }}
              onDownloadReport={downloadMarkdownReport}
              onDownloadPdf={downloadPdfReport}
              onDownloadJson={downloadSimulatorJson}
              onDownloadXml={downloadSimulatorXml}
              exportStatus={{ busy: reportExportBusy }}
              statusText={exportFeedback.message}
              statusTone={
                exportFeedback.type === 'error'
                  ? 'text-rose-600'
                  : exportFeedback.type === 'success'
                    ? 'text-emerald-600'
                    : 'text-slate-500'
              }
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
