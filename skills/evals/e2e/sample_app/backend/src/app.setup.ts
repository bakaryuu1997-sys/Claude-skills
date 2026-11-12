import { INestApplication, ValidationError, ValidationPipe } from '@nestjs/common';
import { AppException, ERR, type ErrorDetail } from './common/errors';
import { GlobalHttpExceptionFilter } from './common/http-exception.filter';
import { EnvelopeInterceptor } from './common/response.interceptor';

function flatten(errors: ValidationError[]): ErrorDetail[] {
  return errors.flatMap((e) =>
    Object.values(e.constraints ?? {}).map((issue) => ({ field: e.property, issue })),
  );
}

/** Shared by main.ts and the test bootstrap so tests run with the same prefix/pipes/filters/interceptors. */
export function configureApp<T extends INestApplication>(app: T): T {
  app.setGlobalPrefix('api/v1', { exclude: ['health'] });
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      exceptionFactory: (errors) => new AppException(ERR.VALIDATION, flatten(errors)),
    }),
  );
  app.useGlobalFilters(new GlobalHttpExceptionFilter());
  app.useGlobalInterceptors(new EnvelopeInterceptor());
  return app;
}
