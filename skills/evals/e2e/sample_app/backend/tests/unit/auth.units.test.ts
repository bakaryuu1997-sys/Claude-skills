import { LoginRateLimiter } from '../../src/auth/login-rate-limit';
import { RefreshTokenStore } from '../../src/auth/refresh-token.store';
import { hasRoleAtLeast } from '../../src/auth/user.types';
import { hashPassword, verifyPassword } from '../../src/auth/users.repository';

describe('LoginRateLimiter', () => {
  it('allows up to max hits, then returns seconds to wait', () => {
    const l = new LoginRateLimiter(2, 10_000);
    expect(l.hit('ip', 0)).toBe(0);
    expect(l.hit('ip', 1_000)).toBe(0);
    expect(l.hit('ip', 2_000)).toBe(8);
  });

  it('opens a new window after windowMs', () => {
    const l = new LoginRateLimiter(1, 10_000);
    l.hit('ip', 0);
    expect(l.hit('ip', 5_000)).toBeGreaterThan(0);
    expect(l.hit('ip', 10_000)).toBe(0);
  });

  it('keys are independent and reset() clears state', () => {
    const l = new LoginRateLimiter(1, 10_000);
    l.hit('a', 0);
    expect(l.hit('b', 0)).toBe(0);
    l.reset();
    expect(l.hit('a', 1)).toBe(0);
  });
});

describe('RefreshTokenStore', () => {
  it('issues a token that can be consumed exactly once', () => {
    const s = new RefreshTokenStore();
    const t = s.issue('u1', 0, 1000);
    expect(s.consume(t, 10)).toBe('u1');
    expect(s.consume(t, 20)).toBeNull();
  });

  it('rejects expired and unknown tokens', () => {
    const s = new RefreshTokenStore();
    const t = s.issue('u1', 0, 1000);
    expect(s.consume(t, 1000)).toBeNull();
    expect(s.consume('nope', 0)).toBeNull();
  });
});

describe('passwords and roles', () => {
  it('verifies the right password and rejects the wrong one; hashes are salted', () => {
    const h = hashPassword('correct-horse-12');
    expect(verifyPassword('correct-horse-12', h)).toBe(true);
    expect(verifyPassword('correct-horse-13', h)).toBe(false);
    expect(hashPassword('correct-horse-12')).not.toBe(h);
    expect(verifyPassword('x', 'malformed')).toBe(false);
  });

  it('role hierarchy: hr >= manager >= employee', () => {
    expect(hasRoleAtLeast('hr', 'manager')).toBe(true);
    expect(hasRoleAtLeast('manager', 'hr')).toBe(false);
    expect(hasRoleAtLeast('employee', 'manager')).toBe(false);
    expect(hasRoleAtLeast('employee', 'employee')).toBe(true);
  });
});
