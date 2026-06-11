const mockReports = {
  CI: {
    healthScore: 89,
    result: 'Mostly healthy with merge caution',
    summary: 'CI environment is stable, but a pipeline stage is slower than expected.',
    areasOfConcern: ['Slow merge validation stage', 'Minor public API latency variance'],
    suggestedImprovements: ['Review pipeline resource usage', 'Monitor API traffic bursts'],
  },
  PROD: {
    healthScore: 64,
    result: 'Degraded due to memory and API issues',
    summary: 'Production health is degraded following the latest deployment which introduced increased memory pressure; a critical memory alert is active.',
    areasOfConcern: ['Critical memory threshold breach', 'Elevated API error rates', 'Infrastructure latency degradation'],
    suggestedImprovements: ['Evict cache and restart affected services', 'Investigate backend timeout sources', 'Review network latency patterns'],
  },
};

export default mockReports;