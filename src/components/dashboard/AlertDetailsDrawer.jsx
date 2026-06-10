import { useEffect } from 'react';

function AlertDetailsDrawer({ alert, isOpen, onClose }) {
  useEffect(() => {
    function onKeyDown(event) {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    }

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !alert) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-slate-900/40 px-4 py-6 sm:items-center sm:p-0"
      role="dialog"
      aria-modal="true"
      aria-labelledby="alert-details-title"
      onClick={onClose}
    >
      <div
        className="w-full max-w-3xl rounded-[2rem] bg-white p-6 shadow-2xl ring-1 ring-slate-200 sm:p-8"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-600">Alert details</p>
            <h2 className="mt-2 text-3xl font-semibold text-slate-900">{alert.title}</h2>
            <p className="mt-2 text-sm text-slate-600">{alert.summary}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500"
            aria-label="Close alert detail drawer"
          >
            Close
          </button>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <div className="space-y-4 rounded-3xl bg-slate-50 p-6">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Severity</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{alert.severity}</p>
            </div>
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Resource</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{alert.affectedResource}</p>
            </div>
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Status</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{alert.status}</p>
            </div>
          </div>

          <div className="space-y-4 rounded-3xl bg-slate-50 p-6">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Source agent</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{alert.sourceAgent}</p>
            </div>
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Confidence</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{alert.confidence}%</p>
            </div>
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Environment</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{alert.environment}</p>
            </div>
          </div>
        </div>

        <div className="mt-8 space-y-6">
          <div className="rounded-3xl bg-slate-50 p-6">
            <h3 className="text-lg font-semibold text-slate-900">Agent reasoning</h3>
            <p className="mt-3 text-slate-600">{alert.reasoning}</p>
          </div>
          <div className="rounded-3xl bg-slate-50 p-6">
            <h3 className="text-lg font-semibold text-slate-900">Suggested actions</h3>
            <p className="mt-3 text-slate-600">{alert.suggestedActions}</p>
          </div>
          <div className="rounded-3xl bg-slate-50 p-6">
            <h3 className="text-lg font-semibold text-slate-900">Related skill</h3>
            <p className="mt-3 text-slate-600">{alert.relatedSkill}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AlertDetailsDrawer;
