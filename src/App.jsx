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

const environments = ['CI', 'PROD'];

function App() {
  const pollingInterval = 2500;
  const [environment, setEnvironment] = useState('PROD');
  const [updatedAt, setUpdatedAt] = useState(new Date());

  //from API
  const [apiHealth, setApiHealth] = useState(null);
  const [apiMetrics, setApiMetrics] = useState(null);
  const [health, setHealth] = useState(null);
  const [subsystems, setSubsystems] = useState([]);
  const [loading, setLoading] = useState(true);

  // fetch/ load data function
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
      const subsystemAgents = Object.entries(metricsRes?.subsystems || {}).map(
        ([name, stats]) => ({ name, ...stats })
      );

      setSubsystems(subsystemAgents);
      setLoading(false);
  }
  useEffect(() => {
    loadData();
  }, [environment]);

  useEffect(() => {
    const timer = setInterval(() => {
      loadData();
      setUpdatedAt(new Date());
    }, pollingInterval);

    return () => clearInterval(timer);
  }, []);

  const skills = mockSkills[environment] || [];
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
