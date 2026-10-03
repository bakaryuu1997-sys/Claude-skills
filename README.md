# Claude Skills & Antigravity Marketplace Plugin 🚀

Bộ kỹ năng kỹ nghệ phần mềm chuyên nghiệp (27+ Lifecycle Skills) và tích hợp công cụ MCP (Serena AST/LSP, Playwright) dành cho **Claude Code**, **Codex**, và **Antigravity**.

Repository: [https://github.com/bakaryuu1997-sys/Claude-skills](https://github.com/bakaryuu1997-sys/Claude-skills)

---

## 🌟 Tính Năng Nổi Bật

1. **Chuẩn Hóa Toàn Diện 6 Giai Đoạn Vòng Đời Dự Án**:
   - **Giai đoạn A (Chuẩn bị)**: Khởi tạo (`/project-init`), Phân tích yêu cầu (`/requirement-analysis`), Demo prototype (`/prototype-ui`), Thiết kế API (`/api-design`), Thiết kế Database (`/db-design`), Báo giá WBS (`/estimate`), Kế hoạch kiểm thử (`/test-plan`), Lập tiến độ (`/project-timeline`).
   - **Giai đoạn B (Khởi động)**: Họp Kickoff (`/project-kickoff`), Thiết kế cơ bản khách duyệt (`/basic-design`), Thiết kế chi tiết cho dev (`/detail-design`).
   - **Giai đoạn C (Vận hành & Phát triển)**: Dev viết code (`/dev-implement`), Sinh test suite API 8 status codes (`/api-test-suite-generator`), Review code 5 sheet Excel (`/code-review`), Kiểm toán bảo mật Trail of Bits & OWASP (`/trailofbits-security-skills`), Quản lý thực thi test (`/test-execution`), Tổng kết sprint (`/sprint-review`), Phân tích thay đổi (`/change-request`).
   - **Giai đoạn D (Bàn giao)**: Bàn giao go-live & runbook (`/handover-doc`).
   - **Giai đoạn X (Cross-cutting)**: Khảo sát kiến trúc 4 tầng bằng Serena LSP (`/acquire-codebase-knowledge`), Sơ đồ kiến trúc HTML (`/project-architecture`), Dashboard tiến độ (`/project-status`), Hiến pháp kỹ thuật nội bộ (`/coding-standards`), Biên bản họp (`/meeting-minutes`).
   - **Meta**: Menu điều hướng sinh động (`/menu`), Linter kiểm định chất lượng (`/skill-doctor`).

2. **Tích Hợp Sẵn Công Cụ MCP Hiện Đại**:
   - **Serena LSP**: Điều hướng mã nguồn theo cấu trúc cây cú pháp (AST Symbols), định vị hàm/class/interface mà không tốn token ngữ cảnh.
   - **Playwright**: Kiểm thử giao diện tự động, chụp ảnh màn hình và tương tác web.

3. **Bảo Mật & An Toàn Đầu Vào (Prompt Injection Defense)**:
   - 100% các skill đều trang bị cơ chế cách ly dữ liệu đầu vào theo chuẩn `input-safety.md`.
   - Vòng lặp tự cải tiến `Self-Improvement Loop` có chốt chặn an toàn (bắt buộc con người phê duyệt).

---

## 🛠️ Hướng Dẫn Cài Đặt 1-Click (Add Marketplace & Auto-Update)

Dựa trên chuẩn Plugin & Marketplace của Claude Code / Codex, bạn có thể thiết lập trên bất kỳ máy tính nào theo 3 bước:

### Bước 1: Thêm Marketplace vào Công cụ Làm Việc
1. Mở menu quản lý Plugin trong **Claude Code**, **Codex**, hoặc **Antigravity**.
2. Chọn mục **Marketplaces**.
3. Nhấn **Add Marketplace** rồi dán đường dẫn GitHub repository:
   ```text
   https://github.com/bakaryuu1997-sys/Claude-skills
   ```
4. Chọn gói plugin **`dev-lifecycle-skills`** và bấm **Install**.

### Bước 2: Bật Chế Độ Tự Động Cập Nhật (Enable Auto Update)
1. Trong phần quản lý plugin đã cài, chuyển trạng thái của `dev-lifecycle-skills` sang **Enable Auto Update**.
2. **Cơ chế hoạt động**: Mỗi khi bạn sửa đổi skill tại máy chính và push commit lên nhánh `main`, công cụ trên máy của bạn (và các máy khác trong team) sẽ tự động kiểm tra và pull bản mới nhất về thư mục chạy ngầm của AI — **hoàn toàn không cần copy file thủ công**.

### Bước 3: Cách Clone Thủ Công (Dành cho máy làm việc offline hoặc Git clone)
```bash
git clone https://github.com/bakaryuu1997-sys/Claude-skills.git
```

---

## 🔄 Quy Trình Sửa Đổi & Auto-Commit Lên GitHub

Mỗi khi bạn tinh chỉnh hoặc thêm mới một skill, hãy chạy script tự động 1-click:
* Trên Windows: Nhấp đúp vào `scripts/auto-commit-push.bat` (hoặc chạy `scripts/auto-commit-push.ps1`).
* Script sẽ tự động:
  1. Chạy `skill-doctor.py` để đảm bảo 0 lỗi cú pháp/logic.
  2. Gom thay đổi và tạo commit theo chuẩn Conventional Commits.
  3. Push trực tiếp lên nhánh `main` của GitHub.

---

## 📜 Giấy Phép
Phát hành theo giấy phép MIT License. Bản quyền thuộc về **bakaryuu** (2026).
