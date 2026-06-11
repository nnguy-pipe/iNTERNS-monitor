import { useEffect, useMemo, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import MetricCard from '../ui/MetricCard.jsx';
import { fetchSimulatorMetrics } from '../../utils/api.js';

// 2× sum of default subsystem base RAM values (web=512, app=256, db=1024, cache=512 → 2304 MB)
const SIM_MAX_RAM_MB = 4608;

function buildSeries(values) {
  return values.map((value, index) => ({ time: `T${index + 1}`, value }));
}

function MetricsPanel({ subsystems }) {
  const dataset = 15;
  const [history, setHistory] = useState({});
  const [selectedMetric, setSelectedMetric] = useState("web"); //default to web, but can be switched to db or cache or app
  // saves history (20 entries) of cpu and memory for each subsystem, updated every time new data is received from API
  useEffect(() => {
    if (!subsystems.length) return;

    subsystems.forEach(s => {
      setHistory(prev => ({
        ...prev,
        [s.name]: {
          cpu: [...(prev[s.name]?.cpu || []).slice(-(dataset-1)), s.cpu],
          memory: [...(prev[s.name]?.memory || []).slice(-(dataset-1)), s.ram]
        }
      }));
    });
  }, [subsystems]);
  const activeHistory = history[selectedMetric] || { cpu: [], memory: [] };
  const cpuData = activeHistory.cpu.map((v, i) => ({ time: i+1, value: v }));
  const memoryData = activeHistory.memory.map((v, i) => ({ time: i+1, value: v }));


  return (
     <section id="metrics" className="space-y-6 rounded-xl bg-white p-8 border border-slate-200">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-600">Live metrics</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-900">Real-time system telemetry</h2>
        </div>
        <p className="text-sm text-slate-500">Metrics update every few seconds with simulated values.<br></br> Displays the most recent {dataset} entries for each subsystem.</p>
      </div>
      {/* Tabs */}
      <div className="flex gap-3 border-b pb-2">
        {subsystems.map(s => (
          <button
            key={s.name}
            onClick={() => setSelectedMetric(s.name)}
            className={`px-4 py-2 rounded-t-md ${
              selectedMetric === s.name
                ? "bg-white border border-b-0 font-semibold"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            {s.name.toUpperCase()}
          </button>
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <div className={`rounded-lg bg-slate-50 p-6 border border-slate-200 ${activeHistory.cpu[activeHistory.cpu.length - 1] > 80 ? 'border-l-4 border-l-red-600' : ''}`}>
          <p className="text-sm uppercase tracking-[0.18em] text-slate-500">CPU Usage (%)</p>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={cpuData} margin={{ top: 8, right: 24, left: 0, bottom: 8 }}>
                <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
                <XAxis dataKey="time" interval={0} tick={{ fill: '#475569' }} tickMargin={2} />
                <YAxis tick={{ fill: '#475569' }} domain={[0, 100]} tickMargin={2} />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#0ea5e9" strokeWidth={3} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className={`rounded-lg bg-slate-50 p-6 border border-slate-200 ${activeHistory.memory[activeHistory.memory.length - 1] > 4000 ? 'border-l-4 border-l-red-600' : ''}`}>
          <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Memory Usage (MB)</p>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={memoryData} margin={{ top: 8, right: 24, left: 0, bottom: 8 }}>
                <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
                <XAxis dataKey="time" interval={0} tick={{ fill: '#475569' }} tickMargin={2} />
                <YAxis tick={{ fill: '#475569' }} domain={[0, 8000]} tickMargin={2} />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={3} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* <div className="grid gap-6 lg:grid-cols-2">
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
      </div> */}
    </section>
  );
}

export default MetricsPanel;
