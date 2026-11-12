import { Inject, Injectable } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { CLOCK, type Clock } from '../common/clock';
import { AppException, ERR } from '../common/errors';
import { CONFIG, type AppConfig } from '../config';
import { LoginRateLimiter } from './login-rate-limit';
import { RefreshTokenStore } from './refresh-token.store';
import type { Role, User } from './user.types';
import { UsersRepository, verifyPassword } from './users.repository';

export interface LoginResult {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  role: Role;
}

@Injectable()
export class AuthService {
  readonly limiter: LoginRateLimiter;
  private readonly refreshTokens = new RefreshTokenStore();

  constructor(
    private readonly users: UsersRepository,
    private readonly jwt: JwtService,
    @Inject(CLOCK) private readonly clock: Clock,
    @Inject(CONFIG) private readonly config: AppConfig,
  ) {
    this.limiter = new LoginRateLimiter(config.loginRateLimit.max, config.loginRateLimit.windowMs);
  }

  private async tokensFor(user: User, now: number): Promise<LoginResult> {
    const accessToken = await this.jwt.signAsync({ sub: user.id, tv: user.tokenVersion });
    const refreshToken = this.refreshTokens.issue(user.id, now, this.config.refreshTtlSeconds * 1000);
    return { accessToken, refreshToken, expiresIn: this.config.accessTtlSeconds, role: user.role };
  }

  async login(employeeId: string, password: string, callerKey: string): Promise<LoginResult> {
    const now = this.clock().getTime();
    const user = this.users.findByEmployeeId(employeeId);

    // An account lock wins over the rate limiter so the 6th attempt reports the lock, not a generic 429.
    if (user?.lockedUntil && user.lockedUntil > now) {
      throw new AppException(ERR.AUTH_LOCKED, [
        { field: 'lockedUntil', issue: new Date(user.lockedUntil).toISOString() },
      ]);
    }

    const retryAfter = this.limiter.hit(callerKey, now);
    if (retryAfter > 0)
      throw new AppException(ERR.RATE_LIMIT, undefined, { 'Retry-After': String(retryAfter) });

    // Same error for unknown user and wrong password: do not reveal which one failed.
    if (!user || !verifyPassword(password, user.passwordHash)) {
      if (user) {
        user.failedLoginCount += 1;
        if (user.failedLoginCount >= this.config.loginLock.maxFailures) {
          user.lockedUntil = now + this.config.loginLock.lockMs;
        }
      }
      throw new AppException(ERR.AUTH_INVALID);
    }

    user.failedLoginCount = 0;
    user.lockedUntil = null;
    return this.tokensFor(user, now);
  }

  async refresh(refreshToken: string): Promise<{ accessToken: string; expiresIn: number }> {
    const now = this.clock().getTime();
    const userId = this.refreshTokens.consume(refreshToken, now);
    const user = userId ? this.users.findById(userId) : undefined;
    if (!user) throw new AppException(ERR.AUTH_TOKEN);
    const accessToken = await this.jwt.signAsync({ sub: user.id, tv: user.tokenVersion });
    return { accessToken, expiresIn: this.config.accessTtlSeconds };
  }
}
