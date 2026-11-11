# Engineering Standards — [CẦN ĐIỀN: tên dự án]

> Mẫu do /x5-coding-standards sinh ra. Mọi `[CẦN ĐIỀN]` lấy từ `project-context.json` hoặc tài liệu thật của dự án; không có thì giữ nguyên, không bịa.
> Phiên bản: `_v1` · Ngày: [CẦN ĐIỀN] · Người phê duyệt: [CẦN ĐIỀN]

## 1. Tech stack (từ `tech_stack`)

| Thành phần | Công nghệ | Phiên bản (từ manifest) |
|---|---|---|
| Backend | [CẦN ĐIỀN] | [CẦN ĐIỀN] |
| Database | [CẦN ĐIỀN] | [CẦN ĐIỀN] |
| Auth | [CẦN ĐIỀN] | [CẦN ĐIỀN] |
| Frontend | [CẦN ĐIỀN] | [CẦN ĐIỀN] |
| CI/CD | [CẦN ĐIỀN] | [CẦN ĐIỀN] |

Chuẩn theo stack: `references/stack-<ngôn-ngữ>.md` (TypeScript / Python / khác).

## 2. Quy tắc mã nguồn

1. Không nuốt lỗi; mọi `catch` phải log hoặc ném lại.
2. Kiểu tường minh ở ranh giới API; validate đầu vào tại biên trước khi vào service.
3. Lỗi: `code` theo `ERR-<DOMAIN>-<NNN>`, lấy từ Error Map của thiết kế chi tiết; không tự tạo mã.
4. Ghi nhiều bảng hoặc ghi kèm log lịch sử → transaction.
5. Cấu hình tập trung một nơi; production thiếu biến bắt buộc → dừng khi khởi động.

## 3. Git & Pull Request

- Commit theo Conventional Commits: `<type>(<scope>): <mô tả>`; type: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `ci`, `build`, `revert`. Breaking change ghi `BREAKING CHANGE:` trong body.
- Nhánh: [CẦN ĐIỀN: quy ước đặt tên nhánh — ví dụ `feature/<ticket>`].
- PR description gồm 7 mục: Summary · Directory Tree · Spec Adherence · Test Verification · Security Checklist · Local Run Guide · Reviewer Notes (mẫu đầy đủ trong SKILL).
- Bằng chứng test: dán lệnh và output thật. Không ghi "pass" nếu chưa chạy.

## 4. Ngưỡng chất lượng

Lấy từ `settings.quality_gates` của context (không đặt số riêng ở đây):

| Chỉ số | Ngưỡng |
|---|---|
| UT pass rate | [từ context] |
| UT coverage line / branch | [từ context] |
| IT pass rate | [từ context] |
| ST pass rate | [từ context] |
| Lỗi Critical/High mở | [từ context] |

## 5. Bảo mật tối thiểu

- Kiểm IDOR (kiểm quyền sở hữu tài nguyên theo người dùng đăng nhập) trên mọi endpoint đọc/ghi tài nguyên của người dùng.
- Token/JWT: thời hạn, cơ chế refresh [CẦN ĐIỀN]; không đưa secret vào log hay response.
- Không log dữ liệu cá nhân và thông tin thanh toán.

## 6. Quy trình thay đổi quy chuẩn

- Mọi thay đổi tài liệu này cần người phê duyệt ghi ở mục đầu. AI không tự sửa quy chuẩn đã duyệt.
- Phát hiện mâu thuẫn giữa quy chuẩn và code hiện có → ghi vào `known_issues[]` của context, không tự sửa code hàng loạt.
