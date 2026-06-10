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

const environments = ['CI', 'PROD'];

function App() {
  const [environment, setEnvironment] = useState('PROD');
  const [updatedAt, setUpdatedAt] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setUpdatedAt(new Date());
    }, 10000);

    return () => clearInterval(timer);
  }, []);

  const activeAlerts = mockAlerts[environment] || [];
  const currentAgents = mockAgents[environment] || [];
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
          <div className="rounded-3xl border border-sky-200 bg-sky-50/90 p-6 text-slate-900 shadow-sm">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-700">Demo guide</p>
                <h2 className="mt-2 text-xl font-semibold text-slate-900">Show the critical alert path</h2>
              </div>
              <div className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-slate-900 ring-1 ring-slate-200">
                Current environment: {environment}
              </div>
            </div>
            <p className="mt-4 max-w-3xl text-slate-700 leading-7">
              Use the CI / PROD toggle to switch between a mostly healthy merge validation story and a clearly degraded production state with a critical memory alert. The health score and active alerts are intentionally prominent for demo impact.
            </p>
          </div>

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
