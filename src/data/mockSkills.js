const mockSkills = {
  CI: [
    {
      name: 'CI Health Gate Review',
      description: 'Analyze merge validation performance and pipeline health.',
      category: 'CI/CD',
      relatedAlerts: ['Merge validation delay'],
    },
    {
      name: 'New Relic Metric Interpretation',
      description: 'Translate metric trends into operational actions.',
      category: 'Monitoring',
      relatedAlerts: ['Minor API latency variance'],
    },
  ],
  PROD: [
    {
      name: 'Memory Leak Detection',
      description: 'Identify memory pressure events and recommend remediation steps.',
      category: 'Reliability',
      relatedAlerts: ['Critical memory threshold breach'],
    },
    {
      name: 'High CPU Usage Investigation',
      description: 'Investigate CPU spikes and service load anomalies.',
      category: 'Performance',
      relatedAlerts: ['API error rate spike'],
    },
    {
      name: 'New Relic Metric Interpretation',
      description: 'Translate production performance trends into action items.',
      category: 'Monitoring',
      relatedAlerts: ['Infrastructure latency degradation'],
    },
  ],
};

export default mockSkills;
