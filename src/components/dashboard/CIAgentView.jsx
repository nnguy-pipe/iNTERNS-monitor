import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import AgentCard from './AgentCard.jsx';

const STATUS_COLOR = {
  Healthy: '#10b981',
  Warning: '#f59e0b',
  Critical: '#ef4444',
  Unknown: '#6b7280',
};

function CIAgentView({ ciAgent }) {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (!ciAgent) return;

    const statusValue =
      ciAgent.status === 'Healthy' ? 100 : ciAgent.status === 'Warning' ? 50 : ciAgent.status === 'Critical' ? 0 : 25;

    setHistory((prev) => {
      const updated = [...prev.slice(-14), { time: prev.length + 1, status: statusValue, label: ciAgent.status }];
      return updated;
    });
  }, [ciAgent]);

  if (!ciAgent) {
    return (
      <div className="rounded-xl bg-white p-8 border border-slate-200 text-center text-slate-500">
        No CI agent data available.
      </div>
    );
  }

  return (
    <section className="space-y-6 rounded-xl bg-white p-8 border border-slate-200">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-600">CI/CD Pipeline</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-900">Pipeline Health</h2>
        </div>
        <p className="text-sm text-slate-500">Real-time CI/CD agent monitoring</p>
      </div>

      {/* CI Agent Card */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <AgentCard {...ciAgent} />
        </div>

        {/* Metrics Summary */}
        <div className="lg:col-span-2 space-y-3">
          <div className="rounded-lg bg-slate-50 p-6 border border-slate-200">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Latest Finding</p>
            <p className="mt-3 text-sm text-slate-700 leading-relaxed">{ciAgent.latestFinding || 'No findings yet'}</p>
          </div>

          <div className="grid gap-3 grid-cols-2">
            <div className="rounded-lg bg-slate-50 p-4 border border-slate-200">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Status</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{ciAgent.status || 'Unknown'}</p>
            </div>
            <div className="rounded-lg bg-slate-50 p-4 border border-slate-200">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Last Checked</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{ciAgent.lastChecked || 'N/A'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Status History Chart */}
      <div className="rounded-lg bg-slate-50 p-6 border border-slate-200">
        <p className="text-sm uppercase tracking-[0.18em] text-slate-500 mb-4">Status History</p>
        <div className="h-64">
          {history.length > 1 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history} margin={{ top: 8, right: 24, left: 0, bottom: 8 }}>
                <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
                <XAxis dataKey="time" tick={{ fill: '#475569' }} tickMargin={2} />
                <YAxis
                  tick={{ fill: '#475569' }}
                  domain={[0, 100]}
                  tickMargin={2}
                  label={{ value: 'Health', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip
                  formatter={(value, name) => {
                    if (name === 'label') return [];
                    if (value === 100) return ['Healthy', 'Status'];
                    if (value === 50) return ['Warning', 'Status'];
                    if (value === 0) return ['Critical', 'Status'];
                    return ['Unknown', 'Status'];
                  }}
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: 'none',
                    borderRadius: '0.5rem',
                    color: '#f1f5f9',
                  }}
                />
                <Line
                  type="stepAfter"
                  dataKey="status"
                  stroke="#0ea5e9"
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-500">
              Waiting for status history...
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

export default CIAgentView;
