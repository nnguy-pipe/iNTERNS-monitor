import { useEffect, useMemo, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import MetricCard from '../ui/MetricCard.jsx';
import mockMetrics from '../../data/mockMetrics.js';
import { fetchSimulatorMetrics } from '../../utils/api.js';

// 2× sum of default subsystem base RAM values (web=512, app=256, db=1024, cache=512 → 2304 MB)
const SIM_MAX_RAM_MB = 4608;

function buildSeries(values) {
  return values.map((value, index) => ({ time: `T${index + 1}`, value }));
}

function MetricsPanel({ environment }) {
  const [metrics, setMetrics] = useState(mockMetrics[environment] || mockMetrics.CI);
  const [dataSource, setDataSource] = useState('mock'); // 'live' | 'mock'

  useEffect(() => {
    setMetrics(mockMetrics[environment] || mockMetrics.CI);
    setDataSource('mock');
  }, [environment]);

  useEffect(() => {
    let active = true;

    async function poll() {
      try {
        const data = await fetchSimulatorMetrics();
        if (!active) return;

        const subsystems = data.subsystems || {};
        const cpuValues = Object.values(subsystems).map((s) => s.cpu);
        const ramValues = Object.values(subsystems).map((s) => s.ram);

        if (cpuValues.length === 0) return;

        const avgCpu = Math.round((cpuValues.reduce((a, b) => a + b, 0) / cpuValues.length) * 10) / 10;
        const totalRam = ramValues.reduce((a, b) => a + b, 0);
        const ramPct = Math.round(Math.min(100, (totalRam / SIM_MAX_RAM_MB) * 100) * 10) / 10;

        setMetrics((prev) => ({
          ...prev,
          cpuUsage: [...prev.cpuUsage.slice(1), avgCpu],
          memoryUsage: [...prev.memoryUsage.slice(1), ramPct],
        }));
        setDataSource('live');
      } catch {
        if (!active) return;
        setDataSource('mock');
        // Animate mock data for CPU and memory when daemon is unavailable
        setMetrics((prev) => ({
          cpuUsage: prev.cpuUsage.map((v) => {
            const change = Math.random() * 6 - 2;
            return Math.max(0, Math.min(100, Math.round((v + change) * 10) / 10));
          }),
          memoryUsage: prev.memoryUsage.map((v) => {
            const change = Math.random() * 4 - 1.5;
            return Math.max(0, Math.min(100, Math.round((v + change) * 10) / 10));
          }),
          apiLatency: prev.apiLatency.map((v) => {
            const change = Math.random() * 18 - 7;
            return Math.max(0, Math.round((v + change) * 10) / 10);
          }),
          errorRate: prev.errorRate.map((v) => {
            const change = Math.random() * 0.8 - 0.3;
            return Math.max(0, Math.round((v + change) * 10) / 10);
          }),
        }));
      }
    }

    // Also keep the mock animation running for apiLatency and errorRate when live
    const mockInterval = setInterval(() => {
      if (!active) return;
      setMetrics((prev) => ({
        ...prev,
        apiLatency: prev.apiLatency.map((v) => {
          const change = Math.random() * 18 - 7;
          return Math.max(0, Math.round((v + change) * 10) / 10);
        }),
        errorRate: prev.errorRate.map((v) => {
          const change = Math.random() * 0.8 - 0.3;
          return Math.max(0, Math.round((v + change) * 10) / 10);
        }),
      }));
    }, 4000);

    const liveInterval = setInterval(poll, 3000);
    poll();

    return () => {
      active = false;
      clearInterval(liveInterval);
      clearInterval(mockInterval);
    };
  }, []);

  const cpuData = useMemo(() => buildSeries(metrics.cpuUsage), [metrics.cpuUsage]);
  const memoryData = useMemo(() => buildSeries(metrics.memoryUsage), [metrics.memoryUsage]);

  return (
     <section id="metrics" className="space-y-6 rounded-xl bg-white p-8 border border-slate-200">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-600">Live metrics</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-900">Real-time system telemetry</h2>
        </div>
        <p className="text-sm text-slate-500">
          {dataSource === 'live'
            ? 'CPU & memory sourced from infrastructure simulator daemon.'
            : 'Metrics update every few seconds with simulated values.'}
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className={`rounded-lg bg-slate-50 p-6 border border-slate-200 ${metrics.cpuUsage[metrics.cpuUsage.length - 1] > 80 ? 'border-l-4 border-l-amber-600' : ''}`}>
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

        <div className={`rounded-lg bg-slate-50 p-6 border border-slate-200 ${metrics.memoryUsage[metrics.memoryUsage.length - 1] > 90 ? 'border-l-4 border-l-red-600' : ''}`}>
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
        {
          (() => {
            const lastLatency = metrics.apiLatency[metrics.apiLatency.length - 1];
            const latencyAccent = lastLatency > 300 ? 'critical' : lastLatency > 250 ? 'warning' : 'normal';
            return (
              <MetricCard
                label="API latency"
                value={lastLatency}
                unit="ms"
                trend={`Trending ${lastLatency > 200 ? 'higher' : 'steady'}`}
                accent={latencyAccent}
              />
            );
          })()
        }
        {
          (() => {
            const lastError = metrics.errorRate[metrics.errorRate.length - 1];
            const errorAccent = lastError > 3 ? 'critical' : lastError > 2 ? 'warning' : 'normal';
            return (
              <MetricCard
                label="Error rate"
                value={lastError}
                unit="%"
                trend={`Trending ${lastError > 2 ? 'up' : 'stable'}`}
                accent={errorAccent}
              />
            );
          })()
        }
      </div>
    </section>
  );
}

export default MetricsPanel;
