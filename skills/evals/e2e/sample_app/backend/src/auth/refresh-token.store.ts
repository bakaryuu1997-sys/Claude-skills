import { createHash, randomBytes } from 'node:crypto';

interface Session {
  userId: string;
  expiresAt: number;
  used: boolean;
}

const sha256 = (v: string): string => createHash('sha256').update(v).digest('hex');

/** Opaque, single-use refresh tokens. Only the SHA-256 hash is stored. */
export class RefreshTokenStore {
  private readonly sessions = new Map<string, Session>();

  issue(userId: string, now: number, ttlMs: number): string {
    const token = randomBytes(32).toString('base64url');
    this.sessions.set(sha256(token), { userId, expiresAt: now + ttlMs, used: false });
    return token;
  }

  /** Consumes the token (rotation). Returns the user id, or null if unknown, expired or already used. */
  consume(token: string, now: number): string | null {
    const s = this.sessions.get(sha256(token));
    if (!s || s.used || s.expiresAt <= now) return null;
    s.used = true;
    return s.userId;
  }
}
