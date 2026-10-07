---
name: x7-presentation-deck
version: "3.8.0"
description: >-
  Tạo slide thuyết trình chuyên nghiệp (PowerPoint pptx 16:9 + HTML interactive slide Marp):
  thiết kế dạng thẻ (Card-based), bảng màu doanh nghiệp, biểu đồ số liệu trực quan, không
  placeholder TBD. Dùng cho pitch, demo, kickoff, sprint review, kiến trúc. Trigger:
  "slide thuyết trình", "tạo slide", "presentation", "powerpoint", "pptx", "pitch deck",
  "slide báo cáo", "thuyết trình dự án". Bước X7.
---

# Presentation Deck — Tạo Slide Thuyết Trình Chuyên Nghiệp

## Mục tiêu

Tạo bộ slide thuyết trình kỹ thuật và quản trị chuẩn phong cách thiết kế con người cao cấp (Human-Centric Executive Design): **Pitching giải pháp, Họp Kickoff, Trình bày Kiến trúc, Sprint Review / Demo sản phẩm, và Báo cáo Ban Lãnh đạo**.

Triệt tiêu hoàn toàn "vết tích AI" (*AI Slop, Bệnh đóng hộp, Viền dạ quang chói lóa, Thẻ ngoặc vuông máy móc*), bộ kỹ năng xuất ra song hành 2 định dạng:
1. **PowerPoint (`.pptx`) 16:9 Widescreen**: Layout thoáng đãng, chữ đứng tự do (Frameless) với phân cấp typography `Segoe UI`, ảnh chụp màn hình tự nhiên và tỷ lệ cân đối hoàn hảo.
2. **HTML Presentation (`.html`) Tự Vận Hành**: Trình chiếu web chuẩn 16:9 với Tailwind CSS tối giản, phím tắt (`←`, `→`, `Space`), Fullscreen (`F`) và nhúng ảnh Base64 tự chứa 100%.

---

## Bước -1 — Đọc Project Context (nếu có)

> **Giao thức chuẩn — chi tiết: `a1-project-init/references/pipeline.md`** (KHÔNG chép lại vào skill):
> đọc bằng `load_context.py` + `cget()`; ghi bằng `update_context.py`; gate bằng `check_gate.py`.
> `NO_CONTEXT` → chạy chế độ hỏi/suy luận thủ công.

Trích xuất: `project.name`, `client`, `tech_stack`, `team`, `estimates`, `milestones`, `activity_log`, và các hiện vật thực tế (`docs/C2_test-execution/screenshots/`, sơ đồ kiến trúc SVG/HTML).

---

## 4 Quy Tắc Thiết Kế Tự Nhiên (Human-Centric Design Principles)

### 1. Bỏ Bệnh "Đóng Hộp" — Chữ Đứng Tự Do (Frameless Layout)
- **CẤM TUYỆT ĐỐI**: Nhốt mọi đoạn text vào từng chiếc hộp hình chữ nhật có viền màu dạ quang (Neon box outline).
- **BẮT BUỘC**: Để chữ và các khối ý tưởng đứng tự do (Frameless) trên nền tối. Sử dụng **khoảng trắng (Negative Space)** rộng rãi và **độ phân cấp kích cỡ font** (Tiêu đề 17–18pt Bold, nội dung 12–13pt Muted) để phân định nội dung như designer chuyên nghiệp.

### 2. Xóa Bỏ Hoàn Toàn Tiền Tố Ngoặc Vuông (`[TAG]` Prohibition)
- **CẤM**: Các thẻ kỹ thuật dạng dump JSON như ❌ `[UI/UX]`, ❌ `[SEARCH]`, ❌ `[AUTO-SAVE]`, ❌ `[DOCKER]`.
- **BẮT BUỘC**: Thay bằng các câu khẳng định ngắn gọn, tự nhiên và mang tính giá trị (Ví dụ: ✅ *Biên Tập 2 Cột Song Song*, ✅ *Tìm Kiếm Toàn Văn Dưới 10ms*, ✅ *Tự Động Lưu Nháp An Toàn*).

### 3. Trình Bày Ảnh Chụp Màn Hình Tự Nhiên (Clean Screenshot Presentation)
- **CẤM**: Bọc ảnh trong khung hình nền màu dày cộp với đường viền dạ quang bao quanh.
- **BẮT BUỘC**: Đặt ảnh chụp màn hình đứng độc lập, sắc nét, viền siêu mảnh tối giản hòa vào nền hoặc hiệu ứng bóng mờ nhẹ để người xem tập trung 100% vào giao diện thật của sản phẩm.

### 4. Giảm Tải Bullet Points — Tập Trung Trải Nghiệm & Đo Lường
- **CẤM**: Danh sách gạch đầu dòng dài dòng kể lể tính năng kỹ thuật mà mắt người xem vốn dĩ đã tự nhìn thấy trên hình ảnh.
- **BẮT BUỘC**: Mỗi điểm nhấn gồm **1 tiêu đề lớn đậm + 1 câu súc tích** mô tả trải nghiệm người dùng thực tế và con số đo lường định lượng (Ví dụ: *<50ms*, *100% pass*, *1 cú click*).

---

## Cấu Trúc Khung Bộ Slide 10 Trang Tự Nhiên

- **Slide 1 — Cover Slide (60/40 Asymmetric Hero)**: Cột trái giới thiệu dự án & định vị giá trị; Cột phải bảng chỉ số trọng tâm phẳng tối giản.
- **Slide 2 — Tầm Nhìn & 3 Trụ Cột**: 3 Khối nội dung thoáng đãng với số thứ tự lớn (01, 02, 03) không viền hộp.
- **Slide 3 — Hiệu Năng & Độ Tin Cậy**: 4 Số liệu lớn tự do (100%, <50ms, 0 Defect, 95%) kèm giải thích trải nghiệm.
- **Slide 4 — Kiến Trúc Hệ Thống**: Dòng chảy kiến trúc 4 tầng phân lập bằng đường gióng tinh tế.
- **Slide 5–6 — Showcase Tính Năng & Giao Diện**: Ảnh chụp màn hình đứng tự nhiên bên trái; 3 điểm nhấn trải nghiệm không viền hộp bên phải.
- **Slide 7 — Tiến Độ Sprints**: Dòng thời gian ngang 3 chặng Scrum rõ ràng, thoáng đãng.
- **Slide 8 — Tiêu Chuẩn Bảo Mật**: 3 Trụ cột an toàn thông tin giải thích bằng văn phong doanh nghiệp.
- **Slide 9 — Triển Khai & Vận Hành**: Quy trình DevOps 1-lệnh, healthcheck và sao lưu tự động.
- **Slide 10 — Kế Hoạch Bàn Giao & Q&A**: Checklist UAT 5 mục thực tế và thảo luận mở.

---

## ⚡ Kiến Trúc Slide HTML Hiện Đại (Slidev & Bento Interactive Architecture)

File HTML xuất ra (`docs/presentations/[TênDựÁn]_Slide_Deck.html`) được xây dựng theo chuẩn tương tác của các công cụ hàng đầu (**Slidev**, **Gamma**, **AiPPT**):

### 1. Thẩm Mỹ Kỹ Thuật Số (Modern Tech Aesthetic)
- **Bảng màu nền sâu (Deep Canvas)**: Nền tối doanh nghiệp (`bg-slate-950` / `#020617`), kết hợp viền mờ tối giản (`border-slate-800/80` / `#1e293b`).
- **Điểm nhấn màu thương hiệu (Accent Glow)**: Màu Sky Blue (`#38bdf8`), Emerald (`#34d399`), Indigo (`#818cf8`) phân định vai trò; cấm viền dạ quang neon chói gắt.
- **Phân cấp phông chữ (Typography Hierarchy)**: Tiêu đề đanh thép, số đo kích thước lớn (Display metrics), văn bản giải thích phụ `text-slate-400`.

### 2. Các Khối Hiển Thị Thành Phần (Component-Based Slide Blocks)
- **Bento KPI Grid**: Hiển thị số liệu định lượng lớn (ví dụ: `100% PASS`, `<50ms`, `0 Defect`) kèm badge đo lường, không dùng bảng biểu khô khan.
- **Code Block Tương Tác (Slidev Style)**: Khối code hiển thị font Monospace (`font-mono`), đánh dấu ngôn ngữ, nút copy mã nguồn nhanh, và hiệu ứng làm nổi bật dòng code trọng tâm.
- **Luồng Kiến Trúc (Architecture Flow)**: Sơ đồ SVG hoặc flex/grid card phân tầng trực quan (Client → Gateway → Microservices → Database).

### 3. Trải Nghiệm Thuyết Trình Trực Tiếp (Live Presentation Controls)
- **Điều hướng bàn phím đầy đủ**: `←` / `→` hoặc `Space` (Chuyển trang), `Home` / `End` (Trang đầu / Trang cuối).
- **Chế độ trình chiếu toàn màn hình (Fullscreen Mode)**: Nhấn phím `F` để mở/đóng fullscreen không viền trình duyệt.
- **Thanh tiến độ & Bộ đếm (Progress & Counter)**: Thanh tiến độ siêu mượt ở cạnh trên và bộ đếm `X / Total` ở góc trên.
- **Chế độ xem lưới tổng quan (Overview Grid Mode)**: Nhấn phím `O` hoặc `G` để xem thumbnail toàn bộ slide và click nhảy nhanh đến slide bất kỳ.
- **Độc lập 100% (Zero-Dependency & Offline-Ready)**: File HTML tự chạy offline khi nhấp đúp, không yêu cầu npm hay web server.

---

## 🔗 Workflow Integration

**Nguồn sự thật pipeline: `<skills_dir>/a1-project-init/references/pipeline.md`** — KHÔNG vẽ lại pipeline trong response; nếu nơi khác mô tả thứ tự lệch, pipeline.md thắng.

- **Bước hiện tại:** X7 — Presentation Deck (Tạo slide thuyết trình chuyên nghiệp)
- **Input từ:** Bất kỳ tài liệu nào trong pipeline cần trình chiếu (A2, A6, B0, B1, C6, X2...)
- **Output cho:** Khách hàng, ban lãnh đạo, toàn thể team dự án
- **Bước kế tiếp:** Trình chiếu trực tiếp trong buổi họp hoặc đính kèm báo cáo

**Kết thúc response:** theo quy ước chung trong `pipeline.md` (≤ 6 dòng ✅→▶; skill tạo/sửa file append `activity_log[]` bằng `update_context.py`).

---

## Self-Improvement Loop

Trước khi kết thúc tác vụ, hãy tự đánh giá lại quá trình thực hiện theo 3 câu hỏi:
1. Có bước nào thất bại, gặp lỗi hoặc phải dùng cách xử lý tạm (workaround) không?
2. Người dùng có phải đính chính, chỉnh sửa hoặc từ chối kết quả nào đáng chú ý không?
3. Có phát hiện thêm ngữ cảnh hay quy tắc mới nào giúp các lần chạy sau làm tốt hơn không?
