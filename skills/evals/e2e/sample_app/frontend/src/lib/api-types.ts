// Contract types (envelope and error shape are defined once in the shared API conventions).
export interface ApiErrorDetail {
  field: string;
  issue: string;
}

export interface ApiErrorBody {
  error: { code: string; message: string; details?: ApiErrorDetail[]; requestId?: string };
}

export interface Envelope<T> {
  data: T;
  meta?: Record<string, unknown>;
}
