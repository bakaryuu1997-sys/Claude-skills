---
name: d3-user-guide-manual
version: "3.9.0"
description: >-
  Biên soạn tài liệu Hướng dẫn sử dụng (User Manual) và Admin Guide chuyên nghiệp: hướng dẫn
  thao tác từng bước kèm ký hiệu vị trí UI & phím tắt, quy trình nghiệp vụ, cây quyết định
  xử lý sự cố tự phục vụ liên kết Runbook, và FAQ. Trigger: "hướng dẫn sử dụng", "user manual",
  "user guide", "tài liệu hdsd", "sổ tay người dùng", "admin guide". Bước D3 — sau nghiệm thu UAT.
---

# User Guide & Manual — Sổ Tay Hướng Dẫn Người Dùng Cuối & Quản Trị Viên

> ⚠️ **Mọi tên riêng trong ví dụ của skill này (FPT, F-Pay, canteen…) chỉ là VÍ DỤ MINH HỌA** — khi làm dự án thực phải thay bằng dữ liệu của dự án đó.

## Mục tiêu

Cung cấp bộ tài liệu hướng dẫn sử dụng phần mềm hoàn chỉnh, trực quan và dễ hiểu cho cả **Người dùng cuối (End-User)** và **Quản trị viên hệ thống (Administrator)**. Giúp người dùng làm quen với hệ thống nhanh chóng (Onboarding), giảm thiểu tối đa yêu cầu hỗ trợ kỹ thuật (Support tickets) và đảm bảo vận hành trơn tru sau khi go-live.

Nguyên tắc biên soạn:
- **Ngôn ngữ người dùng (User-centric):** Sử dụng ngôn từ nghiệp vụ thân thiện, dễ hiểu, tránh thuật ngữ lập trình chuyên sâu khi viết cho người dùng cuối.
- **Minh họa từng bước (Step-by-step with UI Cues):** Mô tả rõ ràng từng thao tác (Ví dụ: "Bước 1: Nhấp vào nút [Tạo đơn hàng] ở góc trên bên phải → Bước 2: Điền các trường bắt buộc...").
- **FAQ thực tế:** Tổng hợp các tình huống hay gặp lỗi và cách tự khắc phục ngay trong tài liệu.
- **Đồng nhất ngôn ngữ 100% (Zero Language Leak):** Nếu viết sổ tay người dùng cho khách Nhật (`client_facing = ja`), toàn bộ tài liệu (User Manual, Admin Guide) phải 100% bằng tiếng Nhật chuẩn, tuyệt đối không lẫn tiếng Việt từ bản nháp.
- **Cấm rò rỉ thương hiệu bên thứ ba & mã bước:** Tuyệt đối không để tên bên thầu cũ (`Rikkei`, `Rikkeisoft`, `FPT`...) hay mã bước nội bộ (`A1`, `D3`...) xuất hiện trong tài liệu bàn giao người dùng.

---

## Bước -1 — Đọc Project Context (nếu có)

> **Giao thức chuẩn — chi tiết: `a1-project-init/references/context-protocol.md`** (KHÔNG chép lại vào skill):
> đọc bằng `load_context.py` + `cget()`; ghi bằng `update_context.py`; gate bằng `check_gate.py`.
> `NO_CONTEXT` → chạy chế độ hỏi/suy luận thủ công.

**Nếu có context** → tự động trích xuất:
- `project.name`, `client`, `links.production_url` (đường dẫn truy cập hệ thống).
- `team.support_contacts` (thông tin liên hệ hỗ trợ).
- `roles` (các nhóm quyền người dùng trong hệ thống).

---

## Bước 0 — Thu thập thông tin đầu vào

Đọc kết quả từ các bước trước:
1. `*_Basic_Design.docx` & Workbook (từ /b2-basic-design) → Danh sách màn hình, bố cục UI, các nút bấm và thông điệp lỗi (message list).
2. `*_Prototype_v[N].html` (từ /a3-prototype-ui) → Giao diện thực tế và luồng thao tác.
3. `*_Requirement_Specification.xlsx` (từ /a2-requirement-analysis) → Danh sách các vai trò (Roles) và ma trận phân quyền.

---

## Tiêu chí Chất lượng & Chống Sơ sài (Anti-Superficiality Checklist)

Bộ tài liệu hướng dẫn bắt buộc gồm **3 tài liệu chuẩn**:

| STT | File Deliverable | Định dạng | Tiêu chuẩn chất lượng tối thiểu |
|---|---|---|---|
| 1 | `[TênDựÁn]_User_Manual_EndUser.docx` | Word Document | Hướng dẫn cho người dùng cuối: Đăng nhập/Đổi mật khẩu, Hướng dẫn từng phân hệ chức năng theo luồng nghiệp vụ. **Bắt buộc tích hợp Ký hiệu Bố cục Nút bấm Trực quan (UI Cue Badges: `[画面右上: 新規登録]`, v.v.) và Bảng Ánh xạ Phím tắt Thao tác Nhanh (Keyboard Shortcuts Mapping: Enter, Esc, Ctrl+K)**, Các lỗi thao tác thường gặp và cách xử lý |
| 2 | `[TênDựÁn]_Admin_Guide.docx` | Word Document | Hướng dẫn cho Quản trị viên: Quản lý tài khoản & phân quyền (RBAC), Cấu hình tham số hệ thống, Xem nhật ký hoạt động (Audit Logs). **Bắt buộc xây dựng Cây Quyết định Xử lý Lỗi Tự phục hồi (Self-Service Incident Decision Tree) liên kết chéo với mã sự cố Runbook (`INC-01` đến `INC-06`)** để xử lý nhanh sự cố người dùng |
| 3 | `[TênDựÁn]_Quick_Start_Guide.md` | Markdown | Hướng dẫn tóm tắt 1 trang (Cheat sheet): URL đăng nhập, tài khoản mặc định thử nghiệm, 5 bước thao tác cơ bản nhất để bắt đầu |

---

## 🔗 Workflow Integration

**Nguồn sự thật pipeline: `<skills_dir>/a1-project-init/references/pipeline.md`** — KHÔNG vẽ lại pipeline trong response; nếu nơi khác mô tả thứ tự lệch, pipeline.md thắng.

- **Bước hiện tại:** D3 — User Guide & Manual (Hoàn tất bàn giao tài liệu cho người dùng)
- **Input từ:** /b2-basic-design (thiết kế màn hình) · /a3-prototype-ui (luồng tương tác) · /d2-uat-acceptance (kết quả nghiệm thu)
- **Output cho:** Người dùng cuối và quản trị viên vận hành hệ thống độc lập
- **Bước kế tiếp:** Hoàn tất toàn bộ chu trình dự án (Hoàn thành pipeline phát triển)

**Kết thúc response:** theo quy ước chung trong `pipeline.md` (≤ 6 dòng ✅→▶; skill tạo/sửa file append `activity_log[]` bằng `update_context.py`).

---

## Self-Improvement Loop

Trước khi kết thúc tác vụ, hãy tự đánh giá lại quá trình thực hiện theo 3 câu hỏi:
1. Có bước nào thất bại, gặp lỗi hoặc phải dùng cách xử lý tạm (workaround) không?
2. Người dùng có phải đính chính, chỉnh sửa hoặc từ chối kết quả nào đáng chú ý không?
3. Có phát hiện thêm ngữ cảnh hay quy tắc mới nào giúp các lần chạy sau làm tốt hơn không?
