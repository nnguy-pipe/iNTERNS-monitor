const mockMetrics = {
  CI: {
    cpuUsage: [18, 24, 22, 26, 21, 19, 23],
    memoryUsage: [42, 45, 44, 46, 43, 44, 45],
    apiLatency: [120, 118, 125, 122, 119, 121, 123],
    errorRate: [0.4, 0.5, 0.3, 0.4, 0.5, 0.4, 0.3],
  },
  PROD: {
    cpuUsage: [51, 58, 62, 66, 71, 65, 69],
    memoryUsage: [72, 78, 82, 88, 92, 95, 98],
    apiLatency: [240, 260, 275, 290, 305, 320, 335],
    errorRate: [1.8, 2.3, 2.6, 3.1, 3.6, 4.0, 4.5],
  },
};

export default mockMetrics;
