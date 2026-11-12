/** Fixed-window in-memory limiter keyed by caller (IP). Reset between tests with reset(). */
export class LoginRateLimiter {
  private readonly hits = new Map<string, { count: number; windowStart: number }>();

  constructor(
    private readonly max: number,
    private readonly windowMs: number,
  ) {}

  /** Returns 0 when allowed, otherwise the seconds until the window resets. */
  hit(key: string, now: number): number {
    const entry = this.hits.get(key);
    if (!entry || now - entry.windowStart >= this.windowMs) {
      this.hits.set(key, { count: 1, windowStart: now });
      return 0;
    }
    entry.count += 1;
    if (entry.count > this.max) return Math.ceil((entry.windowStart + this.windowMs - now) / 1000);
    return 0;
  }

  reset(): void {
    this.hits.clear();
  }
}
