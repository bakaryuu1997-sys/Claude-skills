import { CallHandler, ExecutionContext, Injectable, NestInterceptor, StreamableFile } from '@nestjs/common';
import { Observable, map } from 'rxjs';

/** Wraps successful JSON responses in { data, meta? }; streamed files (CSV) pass through untouched. */
@Injectable()
export class EnvelopeInterceptor implements NestInterceptor {
  intercept(_ctx: ExecutionContext, next: CallHandler): Observable<unknown> {
    return next.handle().pipe(
      map((body: unknown) => {
        if (body instanceof StreamableFile) return body;
        if (body && typeof body === 'object' && 'data' in body) return body;
        return { data: body };
      }),
    );
  }
}
