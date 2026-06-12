import { useEffect, useState } from 'react';
import TopNav from './components/layout/TopNav.jsx';
import PageShell from './components/layout/PageShell.jsx';
import HealthSummary from './components/dashboard/HealthSummary.jsx';
import AgentGrid from './components/dashboard/AgentGrid.jsx';
import MetricsPanel from './components/dashboard/MetricsPanel.jsx';
import AlertsFeed from './components/dashboard/AlertsFeed.jsx';
import AlertDetailsDrawer from './components/dashboard/AlertDetailsDrawer.jsx';
import ReportPreview from './components/dashboard/ReportPreview.jsx';
import RecommendedNextSteps from './components/dashboard/RecommendedNextSteps.jsx';
import mockAgents from './data/mockAgents.js';
import mockAlerts from './data/mockAlerts.js';
import mockReports from './data/mockReports.js';
import mockSkills from './data/mockSkills.js';
import { fetchAgentChecks } from './utils/api.js';

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
  const [environment, setEnvironment] = useState('PROD');
  const [updatedAt, setUpdatedAt] = useState(new Date());
  const [liveAgents, setLiveAgents] = useState(null); // null = not yet loaded
   //from API
  const [apiHealth, setApiHealth] = useState(null);
  const [apiMetrics, setApiMetrics] = useState(null);
  const [health, setHealth] = useState(null);
  const [subsystems, setSubsystems] = useState([]);
  const [loading, setLoading] = useState(true);

  // fetch
  useEffect(() => {
    async function loadData() {
      setLoading(true);

      const [healthRes, metricsRes] = await Promise.all([
        // update to not be hardcoded, but for demo purposes this is fine
        fetch("http://localhost:8000/api/simulator/health").then(r => r.json()),
        fetch("http://localhost:8000/api/simulator/metrics").then(r => r.json())
      ]);

      setHealth(healthRes);
      setApiMetrics(metricsRes);
      // Convert subsystems object → array
      const subsystemAgents = Object.entries(metricsRes.subsystems).map(
        ([name, stats]) => ({ name, ...stats })
      );

      setSubsystems(subsystemAgents);
      setLoading(false);
    }

    loadData();
  }, [environment]);

  useEffect(() => {
    const timer = setInterval(() => {
      setUpdatedAt(new Date());
    }, 10000);

    return () => clearInterval(timer);
  }, []);

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

    const id = setInterval(pollAgents, 60000);
    pollAgents();

    return () => { active = false; clearInterval(id); };
  }, []);

  const activeAlerts = mockAlerts[environment] || [];
  const currentAgents = liveAgents || mockAgents[environment] || [];
  const report = mockReports[environment];
  const skills = mockSkills[environment] || [];
  const [selectedAlert, setSelectedAlert] = useState(null);

  useEffect(() => {
    // Auto-open the critical alert in PROD to guide the demo story
    if (environment === 'PROD') {
      const critical = (mockAlerts.PROD || []).find((a) => a.severity === 'Critical');
      if (critical) setSelectedAlert(critical);
    } else {
      setSelectedAlert(null);
    }
  }, [environment]);

  // Derive health status from agents/alerts for demo storytelling
  const hasCriticalAlert = activeAlerts.some((a) => a.severity === 'Critical');
  const hasHighAlert = activeAlerts.some((a) => a.severity === 'High');
  const hasCriticalAgent = currentAgents.some((ag) => ag.status === 'Critical');

  let healthStatus = 'Healthy';
  if (hasCriticalAlert || hasCriticalAgent) healthStatus = 'Critical';
  else if (hasHighAlert || currentAgents.some((ag) => ag.status === 'Degraded' || ag.status === 'Warning'))
    healthStatus = 'Degraded';

  const healthScore = report?.healthScore ?? (environment === 'PROD' ? 64 : 89);
  const summary = report?.summary ?? '';

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
              <ReportPreview report={report} />
            </div>
            <div className="lg:col-span-4">
              <RecommendedNextSteps skills={skills} />
            </div>
          </section>

          <MetricsPanel environment={environment} />

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
