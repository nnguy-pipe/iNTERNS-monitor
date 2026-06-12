import { describe, expect, it } from 'vitest';
import { calculateHealthScore } from '../src/utils/health.js';

describe('health scoring', () => {
  it('drops quickly when a current subsystem is unhealthy', () => {
    const healthySubsystems = [
      { name: 'web', cpu: 12, ram: 512, active_users: 40 },
      { name: 'app', cpu: 18, ram: 768, active_users: 55 },
      { name: 'db', cpu: 20, ram: 1024, active_users: 30 },
    ];
    const degradedSubsystems = [
      ...healthySubsystems.slice(0, 2),
      { name: 'db', cpu: 96, ram: 7200, active_users: 760 },
    ];

    expect(calculateHealthScore(healthySubsystems)).toBe(100);
    expect(calculateHealthScore(degradedSubsystems)).toBeLessThan(60);
  });
});
