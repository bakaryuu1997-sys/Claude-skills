# Quy tắc review chuyên sâu theo tech stack

Chọn mục theo `tech_stack` trong context (hoặc file đang review). c1 cũng dùng file này khi viết code. Gặp stack chưa có mục → áp checklist chung + tài liệu chính thức của framework, ghi chú trong report.

## NestJS (TypeScript)
- `ValidationPipe` global với `whitelist: true`, `forbidNonWhitelisted: true`, `transform: true`; DTO lồng nhau: `@ValidateNested({ each: true })` + `@Type(() => SubDto)` (thiếu → bỏ qua validation con).
- Guards cho AuthN/AuthZ (không kiểm tay trong controller); lấy `userId/tenantId` từ `req.user`, không từ body.
- POST dạng action/simulate trả 200: `@HttpCode(HttpStatus.OK)`. Lỗi qua `ExceptionFilter` toàn cục trả envelope lỗi chuẩn; không `throw new Error()` thô ra client.
- Service không dùng `@Req()`; Repository/Prisma tách khỏi controller. Prisma: tránh `$queryRawUnsafe`; `include` có kiểm soát (N+1); transaction `$transaction` cho đa bảng; `findMany` có `take`.
- Throttler (`@nestjs/throttler`) cho auth/batch; `ConfigModule` validate env (fail-fast); `helmet()` + CORS whitelist.
- Test: `Test.createTestingModule` nạp đủ pipe/filter/guard như `main.ts`.

## Express / Node.js
- Middleware thứ tự: helmet → CORS (whitelist, không `*` + credentials) → body parser có `limit` → rate limit → auth → routes → error handler cuối.
- Mọi async handler phải bắt lỗi (dùng wrapper hoặc Express 5); không nuốt lỗi. Validation bằng Zod/Joi ở boundary; không truyền `req.body` thẳng vào ORM.
- Không `child_process.exec` với input người dùng; dùng `execFile`/`spawn` mảng đối số. Graceful shutdown (SIGTERM đóng server + DB pool).
- Config: không `process.env.X` rải rác — một module config validate khi khởi động.

## Next.js / React (web)
- Server vs Client Component đúng chỗ: không import module server-only/secret vào Client Component; biến `NEXT_PUBLIC_*` không chứa secret.
- Route Handler/Server Action: kiểm auth + ownership phía server, validate input bằng Zod; Server Action không tin tham số client.
- Phiên: cookie `HttpOnly; Secure; SameSite`; không lưu token ở localStorage; CSP; không `dangerouslySetInnerHTML` với dữ liệu chưa sanitize.
- Data fetching: TanStack Query/`fetch` cache đúng (`revalidate`/`no-store` cho dữ liệu cá nhân); không fetch trong render; có Loading/Error/Empty; `error.tsx`/ErrorBoundary.
- Hiệu năng: dynamic import cho phần nặng, `next/image`, tránh re-render (memo), key ổn định cho list; a11y (label, focus, contrast).
- Form: React Hook Form + Zod, lỗi inline, disable khi submit, `x-idempotency-key` cho thao tác tạo/đổi quan trọng.

## FastAPI / Python
- `Depends()` cho auth/db session (không tạo session trong endpoint); Pydantic model cho request/response, không `dict` raw.
- `async def` phải dùng driver async (`asyncpg`, SQLAlchemy async); `BackgroundTasks` cho email/notification.
- Alembic cho mọi thay đổi DB; `HTTPException` với status đúng — không trả `{"error":…}` kèm 200.

## React Native
- `FlatList` thay `ScrollView` cho danh sách dài; `useCallback` + `React.memo` khi cần.
- Lưu token bằng `SecureStore` (Expo)/`Keychain`, không `AsyncStorage`; Error boundary; `AbortController` hủy fetch khi unmount.

## PostgreSQL
- `EXPLAIN ANALYZE` verify index với query mới; `SELECT … FOR UPDATE` khi cần khóa hàng; `RETURNING` để khỏi SELECT lại.
- Migration an toàn: `CREATE INDEX CONCURRENTLY` (ngoài transaction), `lock_timeout`/`statement_timeout`, cột mới nullable/DEFAULT rồi backfill theo lô.

## Java / Spring (nếu dự án dùng)
- Bean Validation (`@Valid`) ở controller; `@ResponseStatus`/`ResponseEntity` đúng mã; `@Transactional` ở service, không ở controller; Spring Security method-level cho ownership; không `@Autowired` field (dùng constructor injection).
