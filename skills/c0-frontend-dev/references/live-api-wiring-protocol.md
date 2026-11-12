# Quy Chuẩn Tích Hợp API Sống & Chống Mock Giả Lập (Live API Wiring & Anti-Mock Protocol)

Hướng dẫn cấu hình API Client, xác thực, phân giải lỗi và chế độ làm việc khi Backend chưa sẵn sàng.
Hợp đồng API (envelope thành công/lỗi, mã `ERR-<DOMAIN>-<NNN>`) **chỉ định nghĩa ở `pipeline.md` mục "Quy ước dùng chung" §2** — file này không định nghĩa lại, chỉ cách FE tiêu thụ.

---

## 1. Hai chế độ API (`NEXT_PUBLIC_API_MODE`)

| Chế độ | Khi nào | Nguồn dữ liệu | Được phép vào build production? |
|---|---|---|---|
| `live` (mặc định) | Backend đã chạy (dev/staging/prod) | API thật tại `API_BASE_URL` | Có — là chế độ duy nhất của production |
| `contract-mock` | **Contract-first**: Backend (C1) chưa xong, FE cần chạy song song | Mock server sinh từ `*_api_spec.json` / OpenAPI của A4 (Prism hoặc MSW), đặt ở `<frontend>/mocks/` | **KHÔNG.** Chỉ dev/test cục bộ + CI của FE |

Quy tắc contract-first (không dùng sandbox in-memory giả lập Backend):
1. Typed Client + Zod schema sinh từ A4 (`api_spec.json`) — đổi spec thì sinh lại, không sửa tay.
2. Mock chỉ đặt ở `frontend/mocks/` (handlers MSW / `prism mock openapi.yaml`) và `tests/`. **Cấm** để mock trong `src/` hoặc import từ `src/` sang `mocks/` (script `verify_fe_scaffold.py` bắt lỗi này).
3. Production build phải thất bại nếu `NEXT_PUBLIC_API_MODE=contract-mock` (kiểm trong `next.config` hoặc bước CI: `test "$NEXT_PUBLIC_API_MODE" != "contract-mock"`).
4. Mock phải trả đúng envelope/mã lỗi của pipeline §2 và các case lỗi trong cột Errors của A4 (401/403/404/409/422/429/5xx) — không chỉ happy path.
5. Khi Backend sẵn sàng: chuyển sang `live`, chạy chế độ INTEGRATE, ghi kết quả đối soát vào `FE_IMPLEMENTATION_REPORT.md` (Live API Adherence Matrix). Màn hình nào chưa đối soát với API thật phải ghi rõ "chưa live" — không tuyên bố Zero-Mock đạt.

---

## 2. Typed API Client (`src/lib/api-client.ts`) — mẫu

Dùng `fetch` (hoặc Axios) qua **một** module. Điểm cốt lõi: không đụng token trong JS, gắn idempotency key, chuẩn hóa lỗi giữ nguyên `code/details/requestId`, refresh single-flight.

```typescript
// src/lib/api-client.ts
import type { ApiErrorBody } from './api-types'; // { error: { code, message, details?, requestId? } }

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? '/api'; // '/api' = BFF route handlers (cùng origin)

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,            // ERR-<DOMAIN>-<NNN> từ backend
    message: string,
    public readonly details?: ApiErrorBody['error']['details'],
    public readonly requestId?: string,
  ) {
    super(message);
  }
}

const MUTATING = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);
let refreshInFlight: Promise<boolean> | null = null; // single-flight: N request 401 song song => 1 lần refresh

async function refreshSession(): Promise<boolean> {
  refreshInFlight ??= fetch(`${API_BASE_URL}/auth/refresh`, { method: 'POST', credentials: 'include' })
    .then((r) => r.ok)
    .catch(() => false)
    .finally(() => { refreshInFlight = null; });
  return refreshInFlight;
}

export async function apiFetch<T>(path: string, init: RequestInit & { tenantId?: string } = {}, retried = false): Promise<T> {
  const method = (init.method ?? 'GET').toUpperCase();
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  if (init.tenantId) headers.set('x-tenant-id', init.tenantId);               // tenant lấy từ session/route, không từ localStorage
  if (MUTATING.has(method) && !headers.has('x-idempotency-key')) {
    headers.set('x-idempotency-key', `idemp-${Date.now()}-${crypto.randomUUID()}`); // tạo MỖI thao tác người dùng, giữ nguyên khi retry
  }

  const res = await fetch(`${API_BASE_URL}${path}`, { ...init, method, headers, credentials: 'include' }); // cookie HttpOnly tự gắn

  if (res.status === 401 && !retried && !path.startsWith('/auth/')) {
    if (await refreshSession()) return apiFetch<T>(path, init, true);
    if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
      window.location.assign('/login?expired=1');
    }
  }
  if (!res.ok) {
    const body = (await res.json().catch(() => null)) as ApiErrorBody | null;
    throw new ApiError(res.status, body?.error?.code ?? 'ERR-NET-000', body?.error?.message ?? res.statusText,
      body?.error?.details, body?.error?.requestId);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T; // { data, meta } — hook tự lấy .data / .meta
}
```

Ghi chú:
- `x-idempotency-key`: sinh **một lần cho mỗi thao tác của người dùng** (giữ trong state của form/mutation) và gửi lại đúng key đó khi retry; không sinh key mới trong từng lần retry của cùng thao tác.
- Lỗi form: map `error.details[].field` → `setError(field)` của React Hook Form; hiển thị `message` + `requestId` (để người dùng báo hỗ trợ).
- `ApiError.code` dùng để rẽ nhánh UI (vd `ERR-AUTH-002` → redirect login), không so khớp theo `message`.

---

## 3. Lưu trữ token — QUY TẮC BẮT BUỘC (chống XSS đánh cắp phiên)

- **CẤM** lưu access/refresh token trong `localStorage` / `sessionStorage` / biến global đọc được bởi script bên thứ ba.
- Mẫu chuẩn (BFF): Next.js Route Handler (`app/api/auth/*`) nhận đăng nhập, gọi Backend, rồi đặt **cookie `HttpOnly; Secure; SameSite=Lax` (hoặc `Strict`)** chứa session/refresh token. Trình duyệt chỉ gọi BFF cùng origin; BFF gắn `Authorization: Bearer` khi proxy sang Backend. JS phía client không bao giờ thấy token.
- Nếu Backend cấp token qua JSON và không có BFF: access token giữ **trong bộ nhớ** (biến module), refresh token **chỉ** qua cookie HttpOnly do Backend `Set-Cookie`. Trang tải lại → gọi `/auth/refresh` để lấy lại access token.
- Cookie phiên bắt buộc CSRF defense: `SameSite` + header tùy biến (`x-idempotency-key`/`x-requested-with`) trên mutating request, hoặc CSRF token; Backend kiểm `Origin`.
- Bắt buộc CSP (không `unsafe-inline` script nếu khả thi), không `dangerouslySetInnerHTML` với dữ liệu người dùng chưa sanitize.
- `tenant_id`/role hiển thị lấy từ `/auth/me` (server là nguồn sự thật); UI Guard chỉ là UX, quyền thật do Backend kiểm.
- **BFF che mất IP người dùng:** Backend chỉ thấy IP của BFF. Rate limit theo IP ở Backend (vd login 5 lần/10 phút) khi đó bị **dùng chung cho mọi người dùng** → vài lần đăng nhập hợp lệ là cả tổ chức bị 429. Đã gặp thực tế khi tích hợp. Cách xử lý: BFF chuyển `X-Forwarded-For` và Backend bật `trust proxy` đúng với hạ tầng (chỉ tin proxy của mình), hoặc khóa giới hạn theo `employeeId + IP`; phải kiểm trong INTEGRATE bằng ≥ 6 lần đăng nhập từ các tài khoản khác nhau.
- c3 (checklist Frontend) và c4 (Vector 2) kiểm các điểm này.

---

## 4. Data fetching với TanStack Query

```typescript
// features/contracts/api/useContractsQuery.ts
import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api-client';
import type { ContractDto, ContractFilterParams } from '../types/contract.dto';

type ListResponse = { data: ContractDto[]; meta: { total: number; page: number; pageSize: number } };

export function useContractsQuery(params: ContractFilterParams) {
  const qs = new URLSearchParams(params as Record<string, string>).toString();
  return useQuery({
    queryKey: ['contracts', params],
    queryFn: () => apiFetch<ListResponse>(`/contracts?${qs}`),
    staleTime: 30_000,
  });
}
```

```typescript
// features/contracts/api/useCreateContractMutation.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRef } from 'react';
import { apiFetch } from '@/lib/api-client';
import type { CreateContractDto, ContractDto } from '../types/contract.dto';

export function useCreateContractMutation() {
  const queryClient = useQueryClient();
  const idemKey = useRef<string>(`idemp-${Date.now()}-${crypto.randomUUID()}`); // 1 key / 1 lần mở form
  return useMutation({
    mutationFn: (payload: CreateContractDto) =>
      apiFetch<{ data: ContractDto }>('/contracts', {
        method: 'POST', body: JSON.stringify(payload), headers: { 'x-idempotency-key': idemKey.current },
      }),
    onSuccess: () => {
      idemKey.current = `idemp-${Date.now()}-${crypto.randomUUID()}`; // thao tác kế tiếp = key mới
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
    },
  });
}
```

Các ví dụ dùng tên thực thể `contracts` chỉ để minh họa — thay bằng thực thể trong A4/B2 của dự án.

---

## 5. Quy tắc Anti-Mock (kiểm bằng `scripts/verify_fe_scaffold.py`)

1. Không có file/biến mock trong `src/` (tên `mock*`, `fake*`, `dummy*`, `*fixture*`, `const mockX = [...]`). Mock hợp lệ chỉ ở `frontend/mocks/` và `tests/`.
2. Loading: skeleton shimmer, không spinner che toàn màn hình.
3. Empty: màn hình trống có CTA. Error: thông điệp từ `ApiError` + `requestId` + nút `refetch()`.
4. Production build không được chứa đường dẫn `mocks/` và không chạy ở `contract-mock`.
