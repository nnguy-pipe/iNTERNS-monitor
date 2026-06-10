import { useEffect, useRef } from 'react';
import SeverityPill from '../ui/SeverityPill.jsx';

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

  if (!isOpen || !alert) return null;

  const stepsFromText = (text) => {
    if (!text) return [];
    // Split into reasonable steps by sentences or commas for short lists
    const parts = text
      .split(/(?:\.\s+)|(?:;\s+)|(?:, and )|(?:,\s+)/)
      .map((p) => p.trim())
      .filter(Boolean);
    return parts;
  };

  const suggestedSteps = stepsFromText(alert.suggestedActions);

  const whyThisMatters = alert.why || `${alert.affectedResource} is approaching operational limits; if left unaddressed this can cause process restarts, increased latency, or elevated error rates.`;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-slate-900/40 px-4 py-6 sm:items-center sm:p-0"
      role="dialog"
      aria-modal="true"
      aria-labelledby="alert-details-title"
      onClick={onClose}
    >
      <div
        className="w-full max-w-4xl rounded-lg bg-white p-6 border border-slate-200 sm:p-8"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="mt-1">
              <SeverityPill level={alert.severity} />
            </div>
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-600">Alert</p>
              <h2 id="alert-details-title" className="mt-1 text-2xl font-semibold text-slate-900">{alert.title}</h2>
              <p className="mt-2 text-sm text-slate-600">{alert.summary}</p>
              <p className="mt-2 text-xs text-slate-400">{alert.timestamp} • {alert.environment}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={onClose}
              className="inline-flex items-center justify-center rounded-full bg-slate-100 p-2 text-slate-700 hover:bg-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500"
              aria-label="Close alert detail drawer"
            >
              <span className="sr-only">Close</span>
              ×
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-3">
          <div className="col-span-2 space-y-4">
            <section className="rounded-lg bg-slate-50 p-5 border border-slate-200">
              <h3 className="text-sm font-semibold text-slate-700">Issue summary</h3>
              <p className="mt-3 text-slate-600 leading-7">{alert.summary}</p>
            </section>

            <section className="rounded-lg bg-slate-50 p-5 border border-slate-200">
              <h3 className="text-sm font-semibold text-slate-700">Agent diagnosis</h3>
              <p className="mt-3 text-slate-600 leading-7">{alert.reasoning}</p>
            </section>

            <section className="rounded-lg bg-slate-50 p-5 border border-slate-200">
              <h3 className="text-sm font-semibold text-slate-700">Why this matters</h3>
              <p className="mt-3 text-slate-600 leading-7">{whyThisMatters}</p>
            </section>

            <section className="rounded-lg bg-slate-50 p-5 border border-slate-200">
              <h3 className="text-sm font-semibold text-slate-700">Suggested actions</h3>
              <ol className="mt-3 list-decimal list-inside space-y-2 text-slate-600">
                {suggestedSteps.length > 0 ? (
                  suggestedSteps.map((s, i) => (
                    <li key={i} className="pl-1">{s}</li>
                  ))
                ) : (
                  <li className="pl-1">Inspect the agent logs and run the prioritized remediation steps.</li>
                )}
              </ol>
            </section>
          </div>

          <aside className="space-y-4">
            <div className="rounded-lg bg-slate-50 p-4 border border-slate-200">
              <h4 className="text-xs font-semibold text-slate-700">Related skill</h4>
              <div className="mt-3 rounded-md bg-white p-3 border border-slate-200">
                <p className="text-sm font-semibold text-slate-900">{alert.relatedSkill}</p>
                <p className="mt-1 text-xs text-slate-500">Runbook and diagnostic tools for this skill.</p>
                <div className="mt-3 flex gap-2">
                  <button
                    type="button"
                    onClick={() => window.open('#', '_blank')}
                    className="rounded-md bg-white border border-slate-200 px-3 py-1 text-sm font-semibold text-slate-700"
                  >
                    Open skill
                  </button>
                </div>
              </div>
            </div>

            <div className="rounded-lg bg-slate-50 p-4 border border-slate-200">
              <h4 className="text-xs font-semibold text-slate-700">Confidence</h4>
              <div className="mt-3">
                <div className="h-2 w-full rounded-full bg-slate-200">
                  <div
                    className="h-2 rounded-full bg-sky-600"
                    style={{ width: `${alert.confidence}%` }}
                  />
                </div>
                <p className="mt-2 text-xs text-slate-500">{alert.confidence}% confidence</p>
              </div>
            </div>

            <div className="rounded-lg bg-slate-50 p-4 border border-slate-200">
              <h4 className="text-xs font-semibold text-slate-700">Affected resource</h4>
              <p className="mt-2 text-sm font-medium text-slate-900">{alert.affectedResource}</p>
              <p className="mt-1 text-xs text-slate-500">Source agent: <span className="font-medium text-slate-700">{alert.sourceAgent}</span></p>
              <p className="mt-2 text-xs text-slate-400">Status: <span className="font-semibold text-slate-700">{alert.status}</span></p>
            </div>

            <div className="rounded-lg bg-white p-4 border border-slate-200">
              <button
                ref={(el) => {
                  if (el && isOpen) el.focus();
                }}
                type="button"
                onClick={() => {
                  console.log('Acknowledged alert', alert.title);
                  onClose();
                }}
                className="w-full rounded-md bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-sky-500"
              >
                Acknowledge
              </button>
              <button
                type="button"
                onClick={() => window.open('#', '_blank')}
                className="mt-3 w-full rounded-md bg-white border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                View runbook
              </button>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

export default AlertDetailsDrawer;
