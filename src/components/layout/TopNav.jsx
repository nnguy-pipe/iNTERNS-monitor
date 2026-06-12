import StatusBadge from '../ui/StatusBadge.jsx';

function TopNav({ environment, environments, onEnvironmentChange, lastUpdated, status }) {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 lg:px-8">
        <div>
          <p className="text-sm font-semibold tracking-[0.22em] text-sky-600">iNTERN</p>
          <h1 className="text-2xl font-semibold text-slate-900">iMonitor Dashboard</h1>
        </div>

        <div className="flex flex-1 flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
          <nav className="flex flex-wrap items-center gap-3 text-sm text-slate-600">
            <a href="#dashboard" className="hover:text-slate-900">Dashboard</a>
            <a href="#reports" className="hover:text-slate-900">Reports</a>
          </nav>

          <div className="flex items-center gap-3 rounded-full bg-slate-100 p-2 shadow-inner">
            {environments.map((env) => (
              <button
                key={env}
                onClick={() => onEnvironmentChange(env)}
                className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                  environment === env
                    ? 'bg-sky-600 text-white shadow-sm'
                    : 'bg-transparent text-slate-700 hover:bg-slate-200'
                }`}
                aria-pressed={environment === env}
              >
                {env}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <StatusBadge status={status} />
            <p className="text-sm text-slate-500">Updated {lastUpdated.toLocaleTimeString()}</p>
          </div>
        </div>
      </div>
    </header>
  );
}

export default TopNav;
