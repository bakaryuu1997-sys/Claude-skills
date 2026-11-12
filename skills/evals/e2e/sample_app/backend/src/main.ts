import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { configureApp } from './app.setup';
import { validateAndLoadConfig } from './config';

async function bootstrap(): Promise<void> {
  const config = validateAndLoadConfig();
  const app = configureApp(await NestFactory.create(AppModule));
  await app.listen(config.port);
}

void bootstrap();
