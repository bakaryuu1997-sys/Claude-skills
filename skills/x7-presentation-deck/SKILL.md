---
name: x7-presentation-deck
version: "3.6.0"
description: >-
  Tạo slide thuyết trình chuyên nghiệp (PowerPoint pptx 16:9 + HTML interactive slide Marp):
  thiết kế dạng thẻ (Card-based), bảng màu doanh nghiệp, biểu đồ số liệu trực quan, không
  placeholder TBD. Dùng cho pitch, demo, kickoff, sprint review, kiến trúc. Trigger:
  "slide thuyết trình", "tạo slide", "presentation", "powerpoint", "pptx", "pitch deck",
  "slide báo cáo", "thuyết trình dự án". Bước X7.
---

# Presentation Deck — Tạo Slide Thuyết Trình Chuyên Nghiệp

## Mục tiêu

Tạo bộ slide thuyết trình chất lượng cao, chuẩn mực doanh nghiệp và tương tác hiện đại phục vụ các nhu cầu thuyết trình kỹ thuật và quản trị: **Pitching giải pháp, Họp Kickoff, Trình bày Kiến trúc hệ thống, Sprint Review / Demo sản phẩm, và Báo cáo Ban Lãnh đạo**.

Kế thừa các tinh hoa từ cộng đồng mã nguồn mở hàng đầu (*Deck-as-Code*, *Action Titles*, *Density Cap*, *Anti-Slop Design System*), bộ kỹ năng này xuất ra song hành 2 định dạng:
1. **PowerPoint (`.pptx`) 16:9 chuẩn Widescreen**: Định dạng biên tập đầy đủ, sử dụng các shape, card, typography phân cấp và layout chuyên nghiệp qua `python-pptx`.
2. **HTML Presentation (`.html`) Tự Vận Hành (Self-contained)**: Trình chiếu trực tiếp trên mọi trình duyệt web với Tailwind CSS, hiệu ứng Dark Glassmorphism, điều hướng bàn phím (`←`, `→`, `Space`), thanh tiến trình và responsive toàn diện.

---

## Bước -1 — Đọc Project Context (nếu có)

> **Giao thức chuẩn — chi tiết: `a1-project-init/references/pipeline.md`** (KHÔNG chép lại vào skill):
> đọc bằng `load_context.py` + `cget()`; ghi bằng `update_context.py`; gate bằng `check_gate.py`.
> `NO_CONTEXT` → chạy chế độ hỏi/suy luận thủ công.

Trích xuất thông tin dự án: `project.name`, `client`, `tech_stack`, `team`, `estimates`, `milestones`, `activity_log`, và kiểm tra thư mục hiện vật thực tế (`docs/C2_test-execution/screenshots/`, sơ đồ kiến trúc, v.v.).

---

## 3 Quy Tắc "Vàng" Khi Thiết Kế Slide

### 1. Quy tắc Action Title (Bắt buộc 100%)
- **CẤM TUYỆT ĐỐI**: Đặt tiêu đề bằng danh từ chung chung, rời rạc (Ví dụ: ❌ *"Kiến trúc hệ thống"*, ❌ *"Kết quả kiểm thử"*, ❌ *"Tiến độ Sprint"*).
- **BẮT BUỘC**: Mọi tiêu đề slide phải là **Action Title** — câu khẳng định ngắn gọn chứa kết luận hoặc thông điệp cốt lõi (*Key Takeaway*) mà người nghe cần ghi nhớ ngay trong 3 giây đầu tiên.
  - *Ví dụ chuẩn*: ✅ *"Kiến Trúc 4 Tầng Tối Ưu: Phân Lập Gateway, Business Logic & Database ACID"*
  - *Ví dụ chuẩn*: ✅ *"108/108 Test Specs Vượt Qua Tuyệt Đối — Sẵn Sàng 95% Cho Mốc Go-Live"*
  - *Ví dụ chuẩn*: ✅ *"WebSocket Đồng Bộ Đa Thiết Bị Đạt Độ Trễ Dưới 50ms"*

### 2. Khống chế Mật Độ Chữ (Density Cap)
- **Giới hạn độ dài**: Tối đa **40–50 từ** trên một slide nội dung.
- **CẤM TUYỆT ĐỐI**: Các đoạn văn xuôi dài dòng (No walls of text).
- **BẮT BUỘC**: Trình bày theo dạng **Khối thẻ (Card Grid)**, **Chỉ số đo lường lớn (Big KPI Numbers)**, và các gạch đầu dòng súc tích (tối đa **6–8 từ/ý**).

### 3. Quy trình 2 Bước (Outline & Layout Selection → Render Code & QA)
- **Bước 1 (Outline & Takeaways)**: Lên dàn bài outline chi tiết. Với từng slide, xác định rõ:
  - Thông điệp takeaway (Action Title).
  - Loại bố cục phù hợp: Hero Title, 3-Card Grid, Split-Pane (ảnh chụp + phân tích), KPI Matrix, Timeline Sprint.
  - Các số liệu đo lường hoặc hiện vật giao diện đính kèm.
- **Bước 2 (Deck-as-Code Render)**: Tạo script sinh tự động (`scratch/generate_deck.py`), thực thi xuất ra cả 2 file `.pptx` và `.html`, kiểm tra tràn chữ và lưu giữ script để tái lập trình.

---

## Tiêu Chuẩn Thị Giác Chống "AI Slop" (Anti-Slop Design System)

1. **100% Theme Uniformity (Đồng Nhất Nền Tuyệt Đối)**:
   - Toàn bộ bộ slide phải duy trì **duy nhất một phong cách nền đồng nhất** từ trang đầu đến trang cuối.
   - *Executive Dark Slate Theme*: Nền tối sang trọng `#0B132B` / `#0F172A`, thẻ card `#1C2541` viền `#334155`.
   - *Enterprise Clean Light Theme*: Nền sáng thanh lịch `#F8FAFC`, thẻ card `#FFFFFF` viền `#E2E8F0`.
   - **CẤM TUYỆT ĐỐI**: Pha trộn slide nền đen xen kẽ slide nền trắng gây chói mắt và mất đồng bộ nhận diện.

2. **Hoa văn & Họa tiết trang trí (Visual Accents & Motifs)**:
   - **Top Accent Stripe**: Dải màu gradient thương hiệu ở mép trên cùng của mỗi slide (Widescreen bar: `#0288D1` → `#10B981` hoặc `#6366F1` → `#EC4899`).
   - **Status Pill Badges**: Thẻ trạng thái bo tròn dạng viên thuốc ở đầu slide (ví dụ: `[SPRINT 2 ACTIVE]`, `[CORE COMPLETE]`, `[PASS 100%]`).
   - **Elevated Card Containers**: Mỗi khối nội dung được đặt trong khung thẻ bo góc tinh tế, có viền mảnh tương phản nhẹ để tạo chiều sâu thị giác (Visual Depth).
   - **Footer Breadcrumbs**: Chân trang đồng bộ trên 100% slide chứa: Tên dự án | Tên chuyên đề | `Trang X / N` | Ngày báo cáo.

3. **Nhúng Hiện Vật & Ảnh Chụp Thực Tế (Real Artifacts & Screenshots)**:
   - Khi dự án có ảnh chụp giao diện thật (trong `docs/C2_test-execution/screenshots/` hoặc `docs/A2_prototype-ui/`), BẮT BUỘC nhúng ảnh thật vào các slide tính năng / demo.
   - Sử dụng bố cục **Split-Pane (50/50 hoặc 60/40)**: một bên là khung ảnh chụp màn hình viền sáng, một bên là 3 thẻ card tóm tắt giá trị kỹ thuật.

---

## Cấu Trúc Khung Bộ Slide 10–12 Trang Mẫu

- **Slide 1 — Cover Slide**: Action Title dự án, Pill Badge phiên bản/trạng thái, ngày tháng và người trình bày.
- **Slide 2 — Executive Summary & Vision**: 3 Trụ cột giá trị cốt lõi (Tốc độ, Tiện ích, Chủ quyền dữ liệu).
- **Slide 3 — Key Metrics & Performance KPIs**: 4 Khối số liệu lớn nổi bật (Uptime, Pass Rate, Latency, Defect count).
- **Slide 4 — Layered Technical Architecture**: 4 Tầng kiến trúc (Presentation, Gateway/Real-time, Business Logic, Persistence DB).
- **Slide 5–6 — Feature & UI Showcase**: Bố cục Split-Pane nhúng ảnh chụp giao diện thực tế kèm phân tích UX/kỹ thuật.
- **Slide 7 — Sprint Delivery & Roadmap**: Lộ trình 3 Sprints (Đã hoàn thành vs Đang triển khai vs Sắp tới).
- **Slide 8 — Security & Compliance**: Phòng thủ 3 lớp (Auth Master Key, Rate Limiter, Cloudflare Zero Trust).
- **Slide 9 — DevOps & Deployment Runbook**: Docker Compose, Health Check probes, quy trình tự động sao lưu.
- **Slide 10 — Next Steps & Call to Action**: Kế hoạch nghiệm thu UAT, mốc Go-Live và mở thảo luận Q&A.

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
