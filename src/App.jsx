import { useEffect, useState } from 'react';
import TopNav from './components/layout/TopNav.jsx';
import PageShell from './components/layout/PageShell.jsx';
import HealthSummary from './components/dashboard/HealthSummary.jsx';
import AgentGrid from './components/dashboard/AgentGrid.jsx';
import MetricsPanel from './components/dashboard/MetricsPanel.jsx';
import AlertsFeed from './components/dashboard/AlertsFeed.jsx';
import AlertDetailsDrawer from './components/dashboard/AlertDetailsDrawer.jsx';
import ReportPreview from './components/dashboard/ReportPreview.jsx';
import SkillsRegistry from './components/skills/SkillsRegistry.jsx';
import mockAgents from './data/mockAgents.js';
import mockAlerts from './data/mockAlerts.js';
import mockReports from './data/mockReports.js';
import mockSkills from './data/mockSkills.js';

const environments = ['CI', 'PROD'];

function App() {
  const [environment, setEnvironment] = useState('CI');
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

  const healthStatus = environment === 'PROD' ? 'Degraded' : 'Healthy';
  const healthScore = environment === 'PROD' ? 64 : 89;
  const summary =
    environment === 'PROD'
      ? 'Production environment is degraded with a critical memory event and elevated API error rate.'
      : 'CI environment is mostly healthy with a merge validation warning and stable service performance.';

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

          <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
            <ReportPreview report={report} />
            <SkillsRegistry skills={skills} />
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
