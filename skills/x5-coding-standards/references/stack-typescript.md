# Chuẩn TypeScript / Node.js (áp dụng khi `tech_stack.backend` là Node/TS)

Dùng khi `project-context.json → tech_stack.backend` chứa TypeScript/Node/Express/NestJS/Next.js. Ví dụ tên thư viện chỉ minh họa — theo đúng stack của dự án.

## 1. Kiểu dữ liệu
- `tsconfig.json`: bật `"strict": true`.
- Cấm `any`. Dùng `unknown` rồi thu hẹp bằng type guard hoặc schema parser (Zod, Valibot, class-validator…).
- Hàm public của Controller và Service khai báo kiểu trả về tường minh.
- Body/query/params của request: parse và validate bằng schema TẠI BIÊN (route/controller) trước khi gọi service.

## 2. Database & transaction
- Thao tác ghi nhiều bảng, hoặc ghi kèm log lịch sử → bọc transaction (Prisma: `prisma.$transaction(async (tx) => { … })`; TypeORM/Knex: tương đương).
- Khóa ngoại và index được khai báo trong schema, không chỉ trong code.

## 3. Lỗi
- Lớp lỗi kế thừa `Error` có: `statusCode` (HTTP), `code` theo hợp đồng API (`ERR-<DOMAIN>-<NNN>`, pipeline.md §2), `message` an toàn cho người dùng, `details` (tùy chọn).
- Mã lỗi lấy từ **Error Map của /b3-detail-design** hoặc code đã có của dự án. Không tự tạo mã mới khi chưa có trong Error Map.
- Cấm `catch (e) {}` rỗng. Lỗi được log (không log dữ liệu nhạy cảm) hoặc ném lại.
- Error handler trung tâm trả đúng format `{ error: { code, message, details?, requestId? } }`.

## 4. Cấu hình & fail-fast
- Mọi biến môi trường đọc tại một module cấu hình (vd `src/config/index.ts`).
- Khi `NODE_ENV=production` và thiếu biến bắt buộc (theo danh sách trong context hoặc tài liệu cấu hình của dự án) → dừng tiến trình ngay. Không dùng giá trị mặc định cho secret.

## 5. Kiểm tra trước merge (gợi ý lệnh, theo package.json thật)
- `tsc --noEmit` (type check), lint (ESLint), test (Jest/Vitest), coverage theo `settings.quality_gates`.
- Dán output thật vào PR description; không ghi "pass" nếu chưa chạy.
