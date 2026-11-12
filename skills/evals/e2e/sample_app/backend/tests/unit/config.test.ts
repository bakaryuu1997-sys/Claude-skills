import { validateAndLoadConfig } from '../../src/config';

describe('validateAndLoadConfig', () => {
  it('aborts in production when JWT_SECRET is missing (fail-fast)', () => {
    expect(() => validateAndLoadConfig({ NODE_ENV: 'production' })).toThrow(/JWT_SECRET/);
  });

  it('accepts production with a secret and reads PORT', () => {
    const cfg = validateAndLoadConfig({ NODE_ENV: 'production', JWT_SECRET: 'x'.repeat(32), PORT: '8080' });
    expect(cfg.port).toBe(8080);
    expect(cfg.jwtSecret).toHaveLength(32);
  });

  it('uses a clearly non-production default outside production', () => {
    const cfg = validateAndLoadConfig({ NODE_ENV: 'test' });
    expect(cfg.jwtSecret).toContain('not-for-production');
    expect(cfg.port).toBe(3000);
    expect(cfg.accessTtlSeconds).toBe(900);
    expect(cfg.loginLock).toEqual({ maxFailures: 5, lockMs: 600_000 });
  });
});
