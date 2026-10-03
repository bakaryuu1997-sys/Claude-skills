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

Tạo bộ slide thuyết trình chất lượng cao, hiện đại và chuẩn mực phục vụ đa dạng mục đích trong vòng đời dự án: **Pitching giải pháp, Họp Kickoff, Trình bày Kiến trúc kỹ thuật, Sprint Review / Demo tính năng cho khách, và Báo cáo tiến độ cho Ban Lãnh đạo**.

Xuất ra 2 định dạng song hành:
1. File **PowerPoint (`.pptx`) 16:9** chuẩn mực doanh nghiệp, dễ dàng trình chiếu và biên tập trên Microsoft Office / Google Slides.
2. File **HTML Presentation (`.html`) tự vận hành (Self-contained)** chạy trực tiếp trên bất kỳ trình duyệt web nào (hỗ trợ phím mũi tên `←` `→`, phím cách, Fullscreen `F`, responsive trên mọi màn hình).

Nguyên tắc thiết kế chuyên nghiệp:
- **Card-based & Modular:** Nội dung tổ chức thành các khối thẻ trực quan (Cards/Tiles), phân cấp thị giác rõ ràng (Visual Hierarchy). Tuyệt đối tránh các trang slide chỉ toàn chữ bullet points đơn điệu.
- **Dữ liệu & Số liệu lớn (Big Numbers / Key Metrics):** Làm nổi bật các số liệu then chốt (Ví dụ: `99.9% Uptime`, `12 Sprints`, `45 Endpoints`, `0 Critical Bugs`) với cỡ chữ lớn và màu nhấn tương phản.
- **Bảng màu doanh nghiệp đồng nhất (Corporate Color Palette):** Sử dụng các bảng màu chuyên nghiệp (Primary: Navy `#1F3864`, Secondary: Tech Blue `#0288D1`, Accent: Emerald `#10B981`, Surface: Light Slate `#F8FAFC`).
- **Không bao giờ dùng nội dung giữ chỗ (No TBD / Placeholder):** Mọi slide phải chứa số liệu, bối cảnh và lập luận thực tế từ dữ liệu dự án.

---

## Bước -1 — Đọc Project Context (nếu có)

> **Giao thức chuẩn — chi tiết: `a1-project-init/references/context-protocol.md`** (KHÔNG chép lại vào skill):
> đọc bằng `load_context.py` + `cget()`; ghi bằng `update_context.py`; gate bằng `check_gate.py`.
> `NO_CONTEXT` → chạy chế độ hỏi/suy luận thủ công.

**Nếu có context** → tự động trích xuất:
- `project.name`, `client`, `tech_stack`, `team`, `estimates`, `milestones`.
- Bảng màu nhận diện thương hiệu nếu có khai báo trong `settings`.

---

## Bước 0 — Thu thập thông tin đầu vào

Xác định **Chủ đề & Mục tiêu thuyết trình**:
1. **Pitching / Đề xuất giải pháp (Pre-sales):** Đọc từ /a2-requirement-analysis, /a4-api-design, /a6-estimate, /b0-proposal-sow.
2. **Khởi động dự án (Project Kickoff):** Đọc từ /b1-project-kickoff (Charter, RACI, Milestones, Sprints).
3. **Kiến trúc hệ thống (Technical Architecture):** Đọc từ /x1-acquire-codebase-knowledge, /x2-project-architecture.
4. **Tổng kết Sprint & Demo tính năng:** Đọc từ /c6-sprint-review, /c1-dev-implement, kết quả test /c5-test-execution.
5. **Báo cáo tiến độ / Ban Lãnh đạo:** Đọc từ /x3-project-status, /a9-project-timeline.

Nếu người dùng đưa nội dung tự do → Phân tích cấu trúc thành dàn bài 10–15 slide chuẩn.

---

## Tiêu chí Cấu trúc Slide Chuẩn Mực

Một bộ slide chuyên nghiệp thông thường gồm **12–16 slides** theo luồng tư duy mạch lạc:

1. **Slide 1 — Tiêu đề (Title Slide):** Tên dự án, chủ đề buổi họp, khách hàng, ngày trình bày, người trình bày.
2. **Slide 2 — Tóm tắt điều hành (Executive Summary):** 3 thông điệp cốt lõi người nghe cần nắm trong 30 giây.
3. **Slide 3 — Bối cảnh & Thách thức (Problem Statement / Business Context):** Khách hàng đang gặp vấn đề gì, cơ hội là gì.
4. **Slide 4 — Mục tiêu & Tiêu chí thành công (Objectives & KPIs):** Định lượng bằng con số đo đếm được.
5. **Slide 5 — Giải pháp đề xuất (Proposed Solution Overview):** Bức tranh toàn cảnh 3 trụ cột giải pháp.
6. **Slide 6 — Kiến trúc kỹ thuật / Công nghệ (Technical Stack & Architecture):** Sơ đồ khối tầng công nghệ (FE, BE, DB, Cloud).
7. **Slide 7–9 — Tính năng & Demo cốt lõi (Core Features / Sprint Highlights):** Các khối module chính, luồng người dùng nổi bật.
8. **Slide 10 — Đảm bảo chất lượng & An toàn (QA & Security):** Tỷ lệ test coverage, kết quả audit bảo mật, cam kết SLA.
9. **Slide 11 — Lộ trình & Các mốc quan trọng (Roadmap & Milestones):** Dòng thời gian trực quan theo Sprint/Tháng.
10. **Slide 12 — Đội ngũ & Phối hợp (Team & Governance):** Vai trò hai bên, kênh liên lạc và đầu mối hỗ trợ.
11. **Slide 13 — Rủi ro & Giải pháp phòng ngừa (Risks & Mitigation):** Bảng rủi ro kèm hành động đối phó cụ thể.
12. **Slide 14 — Bước kế tiếp (Next Steps / Call to Action):** Các đầu việc cần chốt ngay sau buổi họp.
13. **Slide 15 — Hỏi đáp & Cảm ơn (Q&A & Thank You):** Thông tin liên hệ và mở thảo luận.

---

## Tiêu chí Kỹ Thuật Khi Tạo File PPTX & HTML

- **Tạo file PPTX:**
  - Kích thước chuẩn **16:9** (W: 13.333 inches, H: 7.5 inches).
  - Tối thiểu 3 mẫu layout slide: Hero title, 2/3-column card grid, KPI metrics highlights.
  - Mỗi thẻ nội dung (Card) có viền bo tròn nhẹ, màu nền tương phản nhẹ so với nền slide chính.
- **Tạo file HTML Interactive Slide:**
  - 1 file HTML duy nhất (Self-contained, không phụ thuộc internet ngoài CDN Tailwind/CSS cơ bản).
  - Hỗ trợ chuyển trang mượt mà bằng bàn phím (`ArrowRight`, `ArrowLeft`, `Space`), nút điều hướng nổi ở góc dưới.
  - Hiển thị số trang hiện tại (`3 / 14`) và thanh tiến trình (Progress bar) ở mép trên cùng.

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
