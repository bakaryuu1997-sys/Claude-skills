---
name: product-teardown
version: "1.0.0"
description: >-
  Cố vấn Sản phẩm & Phản biện Tính năng Độc lập (Standalone Product Critic & Feature Innovation):
  quét trực tiếp mã nguồn thực tế (API, UI pages, CSDL) hoặc ý tưởng, đối chiếu khắt khe với siêu
  ứng dụng hàng đầu thế giới (Stripe, Linear, Notion, Duolingo, Shopify), phát hiện tử huyệt UX,
  tính năng làm dở và đề xuất danh mục tính năng bứt phá 3 tầng (Quick Wins, Strategic, Killer Moats).
  Dùng độc lập cho MỌI repo ở MỌI thời điểm, không phụ thuộc quy trình dev.
---

# Product Teardown — Cố vấn Sản phẩm & Phản biện Tính năng Độc lập

Kỹ năng phản biện sản phẩm chuyên sâu (Brutal Product Critic & Innovation Engine). Hoạt động độc lập trên **bất kỳ repo hoặc ý tưởng nào**, không phụ thuộc vào quy trình phát triển, không yêu cầu khởi tạo dự án trước.

---

## 🎯 Khi nào sử dụng (Trigger Words)

Kích hoạt khi người dùng nói bằng tiếng Việt tự nhiên:
- *"đánh giá sản phẩm này", "soi tính năng app này", "product teardown", "phản biện sản phẩm"*
- *"code này còn thiếu tính năng gì so với các app nổi tiếng cùng ngành?"*
- *"đọc code hiện tại rồi gợi ý tính năng mới giúp mình"*
- *"so sánh app này với Stripe / Linear / Notion / Duolingo"*
- *"tính năng này có ổn không, có đối thủ nào làm tốt hơn không?"*

---

## 🧭 Hai Chế độ Hoạt động (Dual Engine)

### Chế độ 1: Quét Codebase Thực tế (`CODEBASE-AWARE TEARDOWN`)
Dùng khi thư mục làm việc đã có mã nguồn (hoặc đang code dở dang):
1. **Chạy script quét mã nguồn** (chỉ đọc, không ghi file; kết quả là HEURISTIC):
   ```bash
   python <skills_dir>/product-teardown/scripts/codebase_feature_scanner.py "<path_to_repo>" [--json]
   ```
   Script nhận diện stack (Node/Next/Express/Nest, Python/FastAPI/Django, Java/Spring, PHP/Laravel, Go), route trang Next.js (bỏ route group `(xxx)`), endpoint theo khai báo route (Express, FastAPI, Spring, Laravel), và tín hiệu UX theo từ khóa. **Mỗi tín hiệu phải đối chiếu lại với code trước khi đưa vào báo cáo**, đặc biệt "có dấu hiệu" chỉ là từ khóa.
2. **Bóc tách hiện trạng:**
   - Đọc danh sách API routes, controllers, frontend pages, CSDL schema (Prisma, PostgreSQL entities).
   - Phát hiện các "tính năng nửa vời" (Half-baked features): thiếu Empty State, thiếu Bulk Action, thiếu Undo toast, thiếu bộ lọc đa chiều, thiếu phím tắt.
3. **Đề xuất tính năng dựa trên CSDL sẵn có:**
   - Không gợi ý viển vông. Gợi ý gắn liền với Tech Stack và Schema hiện tại để dev có thể code được ngay mà không cần đập đi xây lại.

### Chế độ 2: Phản biện Ý tưởng Mới (`GREENFIELD / IDEA TEARDOWN`)
Dùng khi dự án mới chỉ là ý tưởng sơ khai hoặc tài liệu mô tả:
1. Xác định chính xác Domain sản phẩm (Fintech, SaaS, EdTech, E-Commerce...).
2. Bóc tách rào cản phòng thủ kinh doanh (Business Moat) và chu kỳ giữ chân người dùng (Retention Loop).
3. Triệu hồi các chuẩn mực từ **Tier-1 Apps** tương ứng để tạo bảng so sánh tính năng đối thủ.

---

## 🔍 5 Lăng kính Phản biện Khắt khe (Brutal Critique Lens)

1. **Time-to-Value (TTV):** Người dùng mất bao nhiêu giây/click để nhận được giá trị đầu tiên? Chỗ nào làm họ nản lòng bỏ cuộc (Drop-off)?
2. **Cognitive Load & Friction:** Giao diện có bắt người dùng phải suy nghĩ quá nhiều, điền form thừa thãi, hay thiếu cơ chế tự động điền không?
3. **Retention & Hook Model:** Có chu kỳ thói quen (*Trigger $\rightarrow$ Action $\rightarrow$ Variable Reward $\rightarrow$ Investment*) hay chỉ là một công cụ dùng một lần rồi quên?
4. **Business Moat & Defensibility:** Có rào cản cạnh tranh nào (hiệu ứng mạng lưới, data flywheel, locking-in API) không, hay đối thủ chỉ cần 2 tuần là sao chép được?
5. **Edge-case Realism:** Khi mạng chậm, khi người dùng bấm nhầm, khi dữ liệu trống rỗng (Empty State), sản phẩm có ứng phó duyên dáng hay bị sập gãy trải nghiệm?

---

## 🏛️ Đối chiếu Siêu ứng dụng theo Domain (Tier-1 Benchmarking)

Xem chi tiết bộ chuẩn mực tại: [`references/benchmark-tier1-catalogs.md`](./references/benchmark-tier1-catalogs.md).

* **Fintech / Thanh toán / Hóa đơn:** Soi chuẩn **Stripe, Mercury, Brex** (Idempotency Key chống charge 2 lần, PDF ký số SHA-256, Smart Dunning tự động retry, đối soát tự động).
* **SaaS / Quản trị / Workflow:** Soi chuẩn **Linear, Notion, Superhuman** (Phím tắt `Cmd+K`, Optimistic UI không độ trễ, Bulk action toolbar, bộ lọc tổ hợp đa chiều).
* **EdTech / Nền tảng học tập:** Soi chuẩn **Duolingo, Brilliant** (Streak retention loop, micro-celebrations, active recall bite-sized, spaced repetition).
* **E-Commerce / Marketplace:** Soi chuẩn **Shopify, Airbnb** (Onboarding không ma sát, bản đồ đơn hàng timeline trực quan, Smart empty state gợi mở).

---

## 📊 Cấu trúc Báo cáo Đầu ra (Deliverable)

Khi hoàn tất, xuất báo cáo trực tiếp trong chat, hoặc ghi file `<workspace_folder>/docs/product-teardown/Product_Teardown_Report.md` nếu người dùng yêu cầu, theo bố cục chuẩn 4 phần (không dùng đường dẫn tuyệt đối):

1. **Executive Summary:** Điểm số trưởng thành sản phẩm (Thang 10), 3 tử huyệt lớn nhất và 3 cơ hội vàng bứt phá.
2. **Current Codebase Inventory vs Tier-1 Gap:** Bảng đối chiếu hiện trạng tính năng thực tế với siêu ứng dụng đầu ngành.
3. **Danh mục Đề xuất Tính năng Mới (3 Tầng Hành động):**
   * **Tầng 1 — Quick Wins (1–2 MD):** Tinh chỉnh UX ăn điểm ngay (thêm Command Palette, Smart Empty State, Toast Undo).
   * **Tầng 2 — Strategic Upgrades (3–5 MD):** Tính năng chuẩn ngành tăng giá trị sản phẩm (WebSocket realtime, xuất báo cáo CSV/PDF, phân quyền RBAC).
   * **Tầng 3 — Killer Moats:** Tính năng đột phá tạo rào cản cạnh tranh áp đảo (AI automation, gamification loop, tự động hóa quy trình phức tạp).
4. **Lộ trình Thực thi & Khuyến nghị Kỹ thuật (Implementation Notes):** Hướng dẫn dev cách triển khai nhanh dựa trên schema CSDL hiện có.

---

## Self-Improvement Loop

Sau mỗi lần thực hiện teardown, hãy tự đánh giá lại theo 3 câu hỏi:
1. Các đề xuất tính năng có thực sự bám sát khả năng của codebase hay còn bị viển vông?
2. So sánh với siêu ứng dụng có đúng trọng tâm domain của khách hàng không?
3. Có phát hiện thêm mô thức thiết kế (UX pattern) mới nào từ các app hiện đại để bổ sung vào `benchmark-tier1-catalogs.md` không?
