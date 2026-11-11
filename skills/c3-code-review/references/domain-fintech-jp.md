# Domain: Tài chính / Kế toán / Ngân hàng — tiêu chí R25 (mở rộng)

> **Nạp CHỈ KHI** PR đụng module hóa đơn, chứng từ, thanh toán, đối soát, tính thuế, điện văn ngân hàng. Ngưỡng cụ thể (TTL, thời hạn lưu) lấy từ SOW/Detail Design; thiếu thì ghi `[CẦN XÁC NHẬN VỚI KHÁCH]`.

R25 gồm các kiểm tra con (đánh dấu từng mục khi áp dụng):
1. **Pure engine (Zero-IO):** file `*.engine.*` không I/O, không `await`, không gọi DB/API, mốc thời gian tiêm qua tham số (`asOfDate`) → tất định, không time-drift.
2. **Bất biến sau chốt sổ:** thực thể ở trạng thái đã phát hành/đã thanh toán có guard chặn sửa trường tài chính (subtotal, tax_amount, dòng chi tiết) + có test tiêu cực assert 400/409.
3. **Presigned URL chứng từ:** `expiresIn` ngắn theo yêu cầu (mặc định tham khảo ≤ 900 giây), `ResponseContentDisposition: attachment`, có test assert TTL. (Lưu ý: `attachment` không thay thế `Cache-Control: no-store` cho dữ liệu nhạy cảm — kiểm thêm header cache.)
4. **Điện văn cố định (Zengin 120-byte, EDI, SWIFT/MT940):** dùng helper đệm byte, bảng offset khớp đặc tả ngân hàng (ghi rõ 0/1-based), round-trip test, kiểm checksum/trailer.
5. **Hash & lưu trữ pháp lý:** SHA-256+ (cấm MD5/SHA-1) tính trong memory trước upload, test round-trip; Object Lock/thời hạn lưu theo luật/khách.
6. **Batch/orchestrator:** mock harness đủ phương thức tập hợp; endpoint batch có rate limit riêng.
7. **Tham số tài chính trên URL:** không truyền số tiền chính xác/số tài khoản/mã số thuế qua query GET (lưu vết log/proxy/CDN) — dùng POST body hoặc token.
