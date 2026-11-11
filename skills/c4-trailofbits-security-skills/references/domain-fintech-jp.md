# Domain: Tài chính / Kế toán / Ngân hàng — kiểm toán bổ sung

> **Nạp CHỈ KHI** hệ thống xử lý hóa đơn, chứng từ điện tử, thanh toán, công nợ, hoặc yêu cầu pháp lý (電子帳簿保存法, インボイス制度). Ngưỡng/thời hạn lấy từ SOW/Detail Design; thiếu → `[CẦN XÁC NHẬN VỚI KHÁCH]`.

1. **Action-Level Authority:** endpoint tác động tài chính/trạng thái pháp lý (`/contracts/:id/apply|terminate`, phê duyệt, ký) không chỉ dựa vào role tĩnh — kiểm guard thẩm quyền theo hạn mức phê duyệt và luật chuyển trạng thái, chống leo thang đặc quyền ngang/dọc.
2. **Hash chứng từ:** SHA-256/384/512 (cấm MD5, SHA-1), tính trong memory/stream trước upload, hex 64 ký tự (SHA-256) lưu DB; có test round-trip tải về hash lại khớp.
3. **Tham số tài chính trên URL:** số tiền chính xác, số tài khoản ngân hàng, hạn mức tín dụng, mã số thuế không đi qua query GET (lưu vết access log/proxy/CDN/lịch sử trình duyệt) — dùng POST body hoặc token/scope. Bộ lọc khoảng (range) không chứa định danh nhạy cảm thì chấp nhận được; ghi lý do khi chấp nhận.
4. **Batch tài chính** (`/…/batch-calculate`, `/reconciliation/execute`): Throttle riêng, chặt hơn endpoint đọc (giới hạn cụ thể theo NFR dự án), test request vượt ngưỡng nhận 429.
5. **Presigned URL chứng từ:** TTL ngắn, `attachment`, quyền IAM tối thiểu (chỉ prefix của tenant).
