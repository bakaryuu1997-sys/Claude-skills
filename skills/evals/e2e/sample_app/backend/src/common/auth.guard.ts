import { CanActivate, ExecutionContext, Injectable, SetMetadata } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { JwtService } from '@nestjs/jwt';
import type { Request } from 'express';
import { UsersRepository } from '../auth/users.repository';
import { hasRoleAtLeast, type Role, type User } from '../auth/user.types';
import { AppException, ERR } from './errors';

export const ROLE_KEY = 'minRole';
/** Minimum role required (employee < manager < hr). */
export const MinRole = (role: Role) => SetMetadata(ROLE_KEY, role);

export interface AuthedRequest extends Request {
  user: User;
}

interface TokenPayload {
  sub: string;
  tv: number;
}

@Injectable()
export class AuthGuard implements CanActivate {
  constructor(
    private readonly jwt: JwtService,
    private readonly users: UsersRepository,
    private readonly reflector: Reflector,
  ) {}

  async canActivate(ctx: ExecutionContext): Promise<boolean> {
    const req = ctx.switchToHttp().getRequest<AuthedRequest>();
    const [scheme, token] = (req.headers.authorization ?? '').split(' ');
    if (scheme !== 'Bearer' || !token) throw new AppException(ERR.AUTH_TOKEN);

    let payload: TokenPayload;
    try {
      payload = await this.jwt.verifyAsync<TokenPayload>(token);
    } catch {
      throw new AppException(ERR.AUTH_TOKEN);
    }

    const user = this.users.findById(payload.sub);
    // tokenVersion mismatch = token revoked
    if (!user || user.tokenVersion !== payload.tv) throw new AppException(ERR.AUTH_TOKEN);

    const required = this.reflector.getAllAndOverride<Role | undefined>(ROLE_KEY, [
      ctx.getHandler(),
      ctx.getClass(),
    ]);
    if (required && !hasRoleAtLeast(user.role, required)) throw new AppException(ERR.FORBIDDEN);

    req.user = user;
    return true;
  }
}
