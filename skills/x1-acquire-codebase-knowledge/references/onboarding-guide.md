# ONBOARDING GUIDE — mẫu chuẩn cho thành viên mới

> Mục tiêu: người mới đọc xong trong một buổi có thể cài môi trường, chạy được hệ thống trên máy mình, hiểu cấu trúc và biết hỏi ai. Ghi tại `docs/X1_acquire-codebase-knowledge/Onboarding_Guide.md`. Mọi tên người, kênh chat, địa chỉ môi trường LẤY TỪ `team[]`, `links.*` trong context — không bịa; thiếu thì ghi `[CẦN ĐIỀN]`.

## 1. Mục lục bắt buộc

1. **Dự án là gì** — 3–5 câu: người dùng là ai, giá trị chính, phạm vi hiện tại (lấy từ `project.description` và A2).
2. **Ai là ai** — bảng `team[]`: vai trò, phụ trách mảng nào, kênh liên hệ. Thêm dòng "hỏi về …" cho từng người.
3. **Môi trường & truy cập** — repo (`links.git_repo`), staging (`links.staging_url`), tài liệu (`links.*`). KHÔNG ghi mật khẩu/token: ghi "xin cấp qua <quy trình>".
4. **Cài đặt trên máy** — phiên bản runtime (từ `tech_stack`), lệnh cài, biến môi trường (chỉ TÊN biến và mẫu `.env.example`, không giá trị thật), cách chạy test.
5. **Chạy được trong 30 phút** — một chuỗi lệnh duy nhất đi từ clone repo đến trang đầu tiên hiển thị. Nếu cần hơn 30 phút, ghi nguyên nhân.
6. **Bản đồ mã nguồn** — cây thư mục 2 mức, mỗi thư mục một dòng mô tả trách nhiệm (lấy từ `Architecture_Survey.md` của X1).
7. **Luồng nghiệp vụ chính** — 1–2 luồng đầu-cuối, kèm đường dẫn file đầu vào và đầu ra.
8. **Quy ước làm việc** — nhánh, commit (Conventional Commits), review PR (tham chiếu `ENGINEERING_STANDARDS.md` của X5), quy tắc Definition of Done (`quality_gates` trong context).
9. **Tài liệu nên đọc theo thứ tự** — liệt kê từ `docs/` theo bước pipeline (A→D), kèm một dòng "đọc để làm gì".
10. **Việc đầu tiên nên làm** — 2–3 task nhỏ, an toàn (vd sửa text, thêm test) để làm quen quy trình.
11. **Câu hỏi thường gặp** — tối thiểu 5 mục, rút từ `known_issues[]` và các điểm dễ vấp.
12. **Lịch sử thay đổi** — ngày, phiên bản, người sửa.

## 2. Nguyên tắc viết

- Viết cho người chưa biết gì về dự án, không giả định họ đã đọc tài liệu khác.
- Mỗi lệnh phải copy-paste chạy được; ghi rõ hệ điều hành (Windows/macOS) nếu lệnh khác nhau.
- Đường dẫn tương đối trong repo, không đường dẫn tuyệt đối của máy ai.
- Ngôn ngữ theo `settings.languages.internal`; thuật ngữ kỹ thuật giữ tiếng Anh.

## 3. Kiểm tra trước khi phát hành

- [ ] Một người chưa tham gia dự án làm theo được mục 4–5 mà không hỏi lại.
- [ ] Không có token, mật khẩu, IP production, email cá nhân.
- [ ] Mọi `[CẦN ĐIỀN]` đã được điền hoặc có người nhận việc.
- [ ] Ngày cập nhật ghi ở đầu file.
