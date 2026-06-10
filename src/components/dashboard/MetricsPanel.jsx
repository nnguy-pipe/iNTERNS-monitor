import { useEffect, useMemo, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import MetricCard from '../ui/MetricCard.jsx';
import mockMetrics from '../../data/mockMetrics.js';

function buildSeries(values) {
  return values.map((value, index) => ({ time: `T${index + 1}`, value }));
}

function MetricsPanel({ environment }) {
  const [metrics, setMetrics] = useState(mockMetrics[environment]);

  useEffect(() => {
    setMetrics(mockMetrics[environment]);
  }, [environment]);

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics((current) => {
        const next = {
          cpuUsage: current.cpuUsage.map((value) => {
            const change = Math.random() * 6 - 2;
            return Math.max(0, Math.min(100, Math.round((value + change) * 10) / 10));
          }),
          memoryUsage: current.memoryUsage.map((value) => {
            const change = Math.random() * 4 - 1.5;
            return Math.max(0, Math.min(100, Math.round((value + change) * 10) / 10));
          }),
          apiLatency: current.apiLatency.map((value) => {
            const change = Math.random() * 18 - 7;
            return Math.max(0, Math.round((value + change) * 10) / 10);
          }),
          errorRate: current.errorRate.map((value) => {
            const change = Math.random() * 0.8 - 0.3;
            return Math.max(0, Math.round((value + change) * 10) / 10);
          }),
        };
        return next;
      });
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  const cpuData = useMemo(() => buildSeries(metrics.cpuUsage), [metrics.cpuUsage]);
  const memoryData = useMemo(() => buildSeries(metrics.memoryUsage), [metrics.memoryUsage]);

  return (
    <section id="metrics" className="space-y-6 rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-600">Live metrics</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-900">Real-time system telemetry</h2>
        </div>
        <p className="text-sm text-slate-500">Metrics update every few seconds with simulated values.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl bg-slate-50 p-6">
          <p className="text-sm uppercase tracking-[0.18em] text-slate-500">CPU Usage</p>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={cpuData}>
                <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
                <XAxis dataKey="time" tick={{ fill: '#475569' }} />
                <YAxis tick={{ fill: '#475569' }} domain={[0, 100]} />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#0ea5e9" strokeWidth={3} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-3xl bg-slate-50 p-6">
          <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Memory Usage</p>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={memoryData}>
                <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
                <XAxis dataKey="time" tick={{ fill: '#475569' }} />
                <YAxis tick={{ fill: '#475569' }} domain={[0, 100]} />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={3} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <MetricCard
          label="API latency"
          value={metrics.apiLatency[metrics.apiLatency.length - 1]}
          unit="ms"
          trend={`Trending ${metrics.apiLatency[metrics.apiLatency.length - 1] > 200 ? 'higher' : 'steady'}`}
        />
        <MetricCard
          label="Error rate"
          value={metrics.errorRate[metrics.errorRate.length - 1]}
          unit="%"
          trend={`Trending ${metrics.errorRate[metrics.errorRate.length - 1] > 2 ? 'up' : 'stable'}`}
        />
      </div>
    </section>
  );
}

export default MetricsPanel;
