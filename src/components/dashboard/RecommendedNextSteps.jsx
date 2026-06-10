function RecommendedNextSteps({ skills }) {
  // Generate action descriptions from skill names and descriptions
  const getActionDescription = (skill) => {
    const skillNameLower = skill.name.toLowerCase();
    
    if (skillNameLower.includes('memory leak')) {
      return 'Review memory usage patterns and cache configuration';
    }
    if (skillNameLower.includes('cpu')) {
      return 'Investigate CPU spikes and check service load';
    }
    if (skillNameLower.includes('ci health') || skillNameLower.includes('merge')) {
      return 'Review merge validation performance and pipeline stages';
    }
    if (skillNameLower.includes('new relic') || skillNameLower.includes('metric')) {
      return 'Check metric trends and validate performance baselines';
    }
    if (skillNameLower.includes('latency') || skillNameLower.includes('infrastructure')) {
      return 'Check network fabric and recent infrastructure changes';
    }
    return skill.description;
  };

  return (
    <section id="next-steps" className="rounded-xl bg-white p-8 border border-slate-200 h-full">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-600">Next steps</p>
        <h2 className="mt-1 text-xl font-semibold text-slate-900">Recommended actions</h2>
      </div>

      <div className="mt-6 space-y-3">
        {skills && skills.length > 0 ? (
          skills.map((skill, index) => (
            <div
              key={skill.name}
              className="flex gap-3 rounded-lg border border-slate-200 p-3 hover:bg-slate-50 transition"
            >
              <div className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-sky-100 text-xs font-semibold text-sky-700">
                {index + 1}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-900">{getActionDescription(skill)}</p>
                <p className="mt-1 text-xs text-slate-500">{skill.name}</p>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-6">
            <p className="text-sm text-slate-500">No recommended actions at this time.</p>
          </div>
        )}
      </div>
    </section>
  );
}

export default RecommendedNextSteps;
