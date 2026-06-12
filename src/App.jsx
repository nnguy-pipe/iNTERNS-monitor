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
import { fetchAgentChecks, fetchLatestReport, ingestSimulatorMetrics } from './utils/api.js';

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
  const [subsystems, setSubsystems] = useState([]);
  const [backendReports, setBackendReports] = useState({ CI: null, PROD: null });
  const [scoreSources, setScoreSources] = useState({ CI: 'fallback', PROD: 'fallback' });
  const [loading, setLoading] = useState(true);

  // fetch/ load data function
  async function loadData() {
      setLoading(true);

      try {
        const [healthRes, metricsRes] = await Promise.all([
          fetch('http://localhost:8000/api/simulator/health').then((r) => r.json()),
          fetch('http://localhost:8000/api/simulator/metrics').then((r) => r.json()),
        ]);

        setHealth(healthRes);
        setApiMetrics(metricsRes);

        // Convert subsystems object -> array
        const subsystemAgents = Object.entries(metricsRes?.subsystems || {}).map(
          ([name, stats]) => ({ name, ...stats }),
        );
        setSubsystems(subsystemAgents);

        try {
          await ingestSimulatorMetrics(SCORE_SYSTEM_NAME, environment);
          const latestReport = await fetchLatestReport(SCORE_SYSTEM_NAME, environment);
          setBackendReports((prev) => ({ ...prev, [environment]: latestReport }));
          setScoreSources((prev) => ({ ...prev, [environment]: 'backend' }));
        } catch {
          if (!backendReports[environment]) {
            setScoreSources((prev) => ({ ...prev, [environment]: 'fallback' }));
          }
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

  const [selectedAlert, setSelectedAlert] = useState(null);
  const healthSnapshot = useMemo(() => deriveHealthSnapshot(subsystems), [subsystems]);
  const skills = mockSkills[environment] || [];
  const backendReport = backendReports[environment];
  const scoreSource = scoreSources[environment];
  const activeAlerts = healthSnapshot.alerts;
  const fallbackReport = {
    healthScore: healthSnapshot.healthScore,
    result: healthSnapshot.result,
    summary: healthSnapshot.summary,
    areasOfConcern: healthSnapshot.areasOfConcern,
    suggestedImprovements: healthSnapshot.suggestedImprovements,
  };

  const backendHealthScore = backendReport
    ? Math.round((Number(backendReport.health_score) || 0) * 100)
    : null;

  const report = backendReport
    ? {
        healthScore: backendHealthScore,
        result: `Latest backend report for ${environment}.`,
        summary: backendReport.primary_issue || 'No primary issue reported by backend.',
        areasOfConcern: backendReport.primary_issue ? [backendReport.primary_issue] : ['No active concerns'],
        suggestedImprovements:
          Array.isArray(backendReport.suggestions) && backendReport.suggestions.length
            ? backendReport.suggestions
            : ['Continue monitoring backend telemetry ingestion.'],
      }
    : fallbackReport;

  const healthStatus = backendReport ? mapReportStatus(backendReport.status) : healthSnapshot.status;
  const healthScore = backendReport ? backendHealthScore : healthSnapshot.healthScore;
  const summary = backendReport
    ? backendReport.primary_issue || 'Backend report available and up to date.'
    : healthSnapshot.summary;


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
            scoreSource={scoreSource}
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
              <ReportPreview report={report} />
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
