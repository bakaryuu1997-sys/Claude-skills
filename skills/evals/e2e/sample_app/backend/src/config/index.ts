export interface AppConfig {
  nodeEnv: string;
  port: number;
  jwtSecret: string;
  accessTtlSeconds: number;
  refreshTtlSeconds: number;
  loginRateLimit: { max: number; windowMs: number };
  loginLock: { maxFailures: number; lockMs: number };
  delegationMaxDays: number;
}

export const CONFIG = Symbol('CONFIG');

type Env = Record<string, string | undefined>;

const SENSITIVE = ['JWT_SECRET'] as const;

/**
 * Loads configuration from the given env (injected for tests).
 * In production a missing sensitive variable aborts startup (fail-fast, no fallback).
 */
export function validateAndLoadConfig(customEnv?: Env): AppConfig {
  const env: Env = customEnv ?? process.env;
  const nodeEnv = env.NODE_ENV ?? 'development';

  if (nodeEnv === 'production') {
    const missing = SENSITIVE.filter((k) => !env[k]);
    if (missing.length > 0) {
      throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }
  }

  return {
    nodeEnv,
    port: Number(env.PORT ?? 3000),
    jwtSecret: env.JWT_SECRET ?? 'dev-only-secret-not-for-production',
    accessTtlSeconds: 15 * 60,
    refreshTtlSeconds: 7 * 24 * 60 * 60,
    loginRateLimit: { max: 5, windowMs: 10 * 60 * 1000 },
    loginLock: { maxFailures: 5, lockMs: 10 * 60 * 1000 },
    delegationMaxDays: 30,
  };
}
