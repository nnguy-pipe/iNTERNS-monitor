import StatusBadge from '../ui/StatusBadge.jsx';

function AgentCard({name, cpu, ram, active_users, external_load, event_spike }) {
  return (
    <article className="h-full rounded-lg border border-slate-200 bg-white p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{name}</h3>
          <p className="mt-1 text-xs text-slate-500">CPU: {cpu}%</p>
          <p className="mt-1 text-xs text-slate-500">RAM: {ram} mb</p>
          <p className="mt-1 text-xs text-slate-500">Active Users: {active_users}</p>
          <p className="mt-1 text-xs text-slate-500">External Load: {external_load}</p>
          <p className="mt-1 text-xs text-slate-500">Event Spike: {event_spike}</p>
        </div>
        <StatusBadge status={status} />
      </div>
    </article>
  );
}

export default AgentCard;
