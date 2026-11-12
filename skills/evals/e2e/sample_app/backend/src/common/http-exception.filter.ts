import { ArgumentsHost, Catch, ExceptionFilter, HttpException, Logger } from '@nestjs/common';
import type { Request, Response } from 'express';
import { AppException, ERR } from './errors';

@Catch()
export class GlobalHttpExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger('HttpException');

  catch(exception: unknown, host: ArgumentsHost): void {
    const http = host.switchToHttp();
    const res = http.getResponse<Response>();
    const req = http.getRequest<Request>();
    const requestId = String(req.headers['x-request-id'] ?? '');

    let status: number = ERR.SYSTEM.status;
    let code: string = ERR.SYSTEM.code;
    let message: string = ERR.SYSTEM.message;
    let details: unknown;

    if (exception instanceof AppException) {
      status = exception.def.status;
      code = exception.def.code;
      message = exception.def.message;
      details = exception.details;
      for (const [k, v] of Object.entries(exception.extraHeaders ?? {})) res.setHeader(k, v);
    } else if (exception instanceof HttpException) {
      status = exception.getStatus();
      if (status === 404) {
        code = ERR.NOT_FOUND.code;
        message = ERR.NOT_FOUND.message;
      } else if (status === 400 || status === 413) {
        // malformed JSON body etc.
        code = ERR.VALIDATION.code;
        message = ERR.VALIDATION.message;
      } else {
        code = `ERR-SYS-${status}`;
        message = exception.message;
      }
    } else {
      // Unknown error: log internally, never leak details to the client.
      this.logger.error(exception instanceof Error ? exception.stack : String(exception));
    }

    res.status(status).json({ error: { code, message, ...(details ? { details } : {}), requestId } });
  }
}
