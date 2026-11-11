# Checklist review theo loại thay đổi

Áp dụng checklist phù hợp với loại thay đổi; Security luôn áp dụng. Mỗi mục `[ ]` map về tiêu chí R01–R25 trong SKILL.md (cột "Nguồn"). Mục không áp dụng ghi `N/A + lý do` trong workbook.

## Security (mọi thay đổi) — R01–R10
```
[ ] R01 SQL/NoSQL/Command injection — query parameterized/ORM, không nối chuỗi; subprocess truyền mảng đối số
[ ] R02 Authentication — endpoint cần auth verify token TRƯỚC mọi logic; JWT: allowlist thuật toán, hết hạn, thu hồi
[ ] R03 Authorization/IDOR — mọi truy vấn kèm điều kiện sở hữu/tenant (`where id AND userId/tenantId`); userId lấy từ token, không từ body/params
[ ] R04 Input validation — validate toàn bộ input client bằng schema; DTO lồng nhau có @ValidateNested + @Type; whitelist (chống mass assignment)
[ ] R05 Dữ liệu nhạy cảm — không log password/token/thẻ/PII; không trả password_hash/salt trong response
[ ] R06 Error messages — không lộ stack trace/SQL/schema ra client; dùng envelope lỗi chuẩn của pipeline
[ ] R07 Rate limiting — endpoint auth/public/batch có giới hạn tần suất riêng
[ ] R08 File upload — MIME thực (magic bytes), giới hạn dung lượng, tên file, quét virus nếu cần
[ ] R09 Dependency — package mới có CVE? (`npm audit --omit=dev` / `pip-audit`)
[ ] R10 Secrets — không hardcode key/password trong code, Dockerfile, workflow; không commit .env
```

## Performance & Logic — R11–R14
```
[ ] R11 N+1 query; thiếu index trên WHERE/JOIN/FK; GET list có phân trang; cache dữ liệu ít đổi; tác vụ nặng ra background job; response chỉ trả trường cần; connection pool
[ ] R12 Transaction + đồng thời: update nhiều bảng trong transaction; race condition (SELECT FOR UPDATE/optimistic lock); POST retry-safe (idempotency key) — đặc biệt thanh toán
[ ] R13 Business rule khớp spec (API/Detail Design); edge case null/empty/0/âm/biên; status code đúng hành động (201 tạo, 204 xóa); message lỗi rõ
[ ] R14 Error handling — catch đúng tầng, không nuốt lỗi, không `catch {}` rỗng, không ép `any` che lỗi; step 2 fail sau step 1 commit → có rollback/compensation
```

## Database / Migration — R15
```
[ ] Migration reversible (có down) · non-breaking (cột mới nullable/DEFAULT) · breaking change có kế hoạch 2 bước (expand/contract)
[ ] FK mới có index · backfill xử lý null/default · thứ tự migration không vòng · đã thử rollback ở staging · seed lookup nếu cần
```

## API Contract (đối chiếu API Design) — R16–R17
```
[ ] R16 URL/method/request schema/response schema đúng spec; envelope thành công `{data,meta}` và lỗi `{error:{code,message,details,requestId}}`, mã `ERR-<DOMAIN>-<NNN>` theo pipeline.md; auth middleware đã gắn; breaking change → bump version
[ ] R17 Decorator/status parity — endpoint POST dạng action/simulate/search (không tạo entity) mà framework mặc định trả 201 phải trả đúng 200 như spec (NestJS `@HttpCode(200)`, Spring `@ResponseStatus`, FastAPI `status_code=`)
```

## Test — R18–R20
```
[ ] R18 Có test cho: happy path, auth failure, validation, not found, permission, biên (rỗng/max length). Code mới không có test → Medium
[ ] R19 Mọi nhánh guard/throw/optimistic lock/ràng buộc ngày có test nhánh tiêu cực (unhappy path)
[ ] R20 Dịch vụ ngoài được mock; mock ORM đủ phương thức mà code gọi (kể cả findMany/count/updateMany/$transaction); test không phụ thuộc thời gian thực/thứ tự chạy
```

## Infrastructure as Code — R21–R22
```
[ ] R21 Dockerfile: image pin version (không `latest`), non-root, HEALTHCHECK, multi-stage, .dockerignore (node_modules, .env, .git), resource limits (compose/K8s)
[ ] R22 CI/CD: secrets qua GitHub Secrets/env, CI chạy trên PR, branch protection, staging/production cùng image khác env
```

## Frontend (web / React Native) — R23
```
[ ] Loading/Error/Empty state đủ; offline không crash; cleanup useEffect/subscription; AbortController khi unmount; không gọi API trong render
[ ] Token/phiên: KHÔNG lưu access/refresh token trong localStorage/sessionStorage/AsyncStorage (web: cookie HttpOnly/BFF hoặc bộ nhớ; RN: SecureStore/Keychain)
[ ] XSS: không `dangerouslySetInnerHTML`/`innerHTML` với dữ liệu người dùng chưa sanitize; có CSP; CSRF defense khi dùng cookie phiên (SameSite + header tùy biến/CSRF token)
[ ] Có `x-idempotency-key` cho mutating request quan trọng; nút submit disabled khi đang gửi
[ ] Re-render không cần thiết (memo/useCallback), Accessibility (alt, label), i18n không hardcode chuỗi
```

## Maintainability & kiến trúc — R24
```
[ ] Phân tầng router→controller→service→repository; không logic nghiệp vụ trong controller; TypeScript strict (không `any` che lỗi, không `@ts-ignore` vô cớ); naming/độ phức tạp hợp lý; trùng lặp code; comment giải thích "vì sao"
```

## Domain-specific — R25
Nạp `references/domain-fintech-jp.md` nếu dự án thuộc domain tài chính/kế toán/ngân hàng; ngược lại ghi `N/A`.
