# 🏛️ TIER-1 BENCHMARK CATALOG & UX ANATOMY
> Thư viện đối chiếu chuẩn mực thiết kế và trải nghiệm từ các siêu ứng dụng hàng đầu thế giới.

---

## 1. Domain: Fintech, Invoicing, Billing & B2B Payments
**Siêu ứng dụng đối chiếu:** Stripe, Mercury, Brex, Ramp

### Các chuẩn mực bắt buộc (Industry Standards):
1. **Idempotency Key (Chống trừ tiền hai lần):**
   - Mọi mutation tạo hóa đơn, charge thẻ, gửi yêu cầu thanh toán đều phải có `Idempotency-Key` ở Header.
   - Nếu mạng chập chờn user bấm 2 lần -> Backend trả về kết quả cũ, tuyệt đối không tạo bản ghi mới.
2. **Visual Proof & PDF Hash Integrity:**
   - Hóa đơn không chỉ là HTML mà phải xuất PDF có gắn dấu băm SHA-256 chống chối bỏ.
   - Hiển thị QR Code thanh toán tức thì theo chuẩn ngân hàng (PayPay, Zengin, VietQR, SEPA).
3. **Smart Dunning & Auto-Retry Loop:**
   - Khi thanh toán thất bại: Không khóa tài khoản ngay. Gửi email nhắc nhở kèm link thanh toán 1-click không cần đăng nhập lại.
   - Tự động retry theo thuật toán Exponential Backoff (+1 ngày, +3 ngày, +7 ngày).
4. **Real-time Reconciliation (Đối soát tự động):**
   - Đọc sao kê ngân hàng (Zengin/CSV/MT940) và tự động khớp (fuzzy matching) theo mã số hợp đồng và số tiền.

---

## 2. Domain: SaaS, Workflow, Project & Data Management
**Siêu ứng dụng đối chiếu:** Linear, Notion, Figma, Superhuman

### Các chuẩn mực bắt buộc:
1. **Zero-Latency Navigation & Command Palette (`Cmd+K` / `Ctrl+K`):**
   - Mọi hành động (tìm kiếm, đổi trạng thái, gán người, xuất file) đều có thể gõ bằng bàn phím trong < 0.2s.
2. **Optimistic UI Updates:**
   - Khi bấm chuyển trạng thái Task từ "In Progress" sang "Done" -> Giao diện đổi ngay lập tức, ngầm gửi API phía sau. Nếu lỗi -> Bắn toast "Undo" và rollback lại trạng thái cũ.
3. **Multi-dimensional Filtering & Saved Views:**
   - Không chỉ có ô Search text đơn thuần. Phải lọc kết hợp: `Status is X` AND `Date after Y` AND `Amount > Z`.
   - Cho phép lưu lại bộ lọc thành "Tab tùy chỉnh" (Saved Views).
4. **Contextual Action Toolbar (Bulk Actions):**
   - Chọn nhiều dòng (Checkbox) -> Nổi thanh toolbar nổi ở đáy màn hình: Xóa hàng loạt, Đổi trạng thái hàng loạt, Xuất CSV hàng loạt.

---

## 3. Domain: EdTech, Learning Platforms & Community
**Siêu ứng dụng đối chiếu:** Duolingo, Brilliant, Coursera, Codecademy

### Các chuẩn mực bắt buộc:
1. **The Retention Loop (Streak & Micro-Celebrations):**
   - Chuỗi ngày học liên tục (Streak counter), biểu tượng ngọn lửa, thông báo nhắc nhở nhẹ nhàng vào giờ học cố định.
   - Hoàn thành bài học: Hiệu ứng pháo hoa nhẹ, cộng điểm XP, cảm giác tiến bộ rõ rệt (Sense of Progress).
2. **Active Recall & Bite-sized Units:**
   - Chia nhỏ kiến thức thành từng thẻ 3–5 phút. Không bắt đọc văn bản dài 20 trang.
   - Xen kẽ câu đố (Quiz), kéo thả, điền từ khuyết, chạy code thử nghiệm trực tiếp trên trình duyệt.
3. **Spaced Repetition (Lặp lại ngắt quãng):**
   - Tự động gợi ý ôn tập lại những câu hỏi hoặc bài học mà người dùng đã từng làm sai cách đây 3 ngày.

---

## 4. Domain: E-Commerce, Booking & Marketplace
**Siêu ứng dụng đối chiếu:** Shopify, Airbnb, Amazon, Uber

### Các chuẩn mực bắt buộc:
1. **Frictionless Onboarding & Progressive Profiling:**
   - Không bắt điền 15 ô thông tin khi mới tạo tài khoản. Chỉ hỏi Email/Mật khẩu hoặc Social Login. Các thông tin khác hỏi dần khi thực hiện giao dịch đầu tiên.
2. **Visual Evidence & Real-time Status:**
   - Hiển thị bản đồ hành trình đơn hàng dạng Timeline trực quan (Đã đặt -> Đang duyệt -> Đang giao -> Hoàn thành).
3. **Smart Empty States:**
   - Khi chưa có dữ liệu (giỏ hàng trống, chưa có đơn hàng): Tuyệt đối không để màn hình trắng trơn. Phải có hình minh họa thân thiện, văn bản gợi mở và nút kêu gọi hành động (CTA) như: *"Khám phá các sản phẩm nổi bật ngay"*.
