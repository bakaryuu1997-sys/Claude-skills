# Khung nội dung 3 tài liệu hướng dẫn (D3)

> Khung CHUNG. Tên màn hình, nút, thông báo, vai trò, mã sự cố… phải lấy từ tài liệu thiết kế cơ bản, prototype, Requirement Specification và `Runbook` thật.
> Không tìm thấy → `[CẦN ĐIỀN]`. Ngôn ngữ/font theo `settings.languages.client_facing` (`i18n-policy.md`).
> Tài liệu gửi người dùng KHÔNG chứa mã bước nội bộ (A1…D3), tên nhà thầu cũ hay thông tin dự án khác.

## 0. Phần chung của mọi tài liệu
- Bìa: tên hệ thống, đối tượng đọc (End User / Administrator), phiên bản hệ thống (`release.version`), ngày.
- **Lịch sử thay đổi tài liệu**: bảng `Phiên bản | Ngày | Người sửa | Nội dung thay đổi | Phiên bản hệ thống áp dụng`. Mỗi lần chạy lại skill thêm một dòng và sinh file `_v2`, `_v3`…
- Mục lục tự động, thuật ngữ (glossary: thuật ngữ nghiệp vụ dùng trong màn hình, định nghĩa 1 câu), cách dùng tài liệu (quy ước ký hiệu UI Cue, cảnh báo, mẹo).
- Hỗ trợ: kênh/giờ phủ lấy từ `Warranty_Scope` (D2) hoặc `team[]` `side=vendor` — chỉ ghi kênh thật.

## 1. Quy ước UI Cue (theo ngôn ngữ tài liệu)
Dạng `[<vị trí>: <nhãn nút/trường>]`, nhãn lấy y nguyên từ giao diện (`Screen_Items`):
- `ja`: `[画面右上: 新規登録]`
- `vi`: `[Góc trên bên phải: Đăng ký]`
- `en`: `[Top right: Register]`
Vị trí chuẩn: Góc trên trái/phải, Thanh bên trái, Giữa màn hình, Cuối form, Thanh điều hướng. Mỗi bước thao tác một dòng, đánh số, có ảnh (xem `screenshot-and-masking.md`).

## 2. `User_Manual_EndUser`
1. Bắt đầu: truy cập (URL từ `links.production_url`), trình duyệt/thiết bị hỗ trợ (từ NFR/thiết kế), đăng nhập, đổi/quên mật khẩu, đăng xuất.
2. Hướng dẫn theo luồng nghiệp vụ: mỗi luồng lấy từ Business Flow của thiết kế cơ bản — mục tiêu, vai trò được dùng, điều kiện trước, các bước (UI Cue + ảnh), kết quả mong đợi, lưu ý.
3. Bảng phím tắt: CHỈ liệt kê phím tắt thật sự có trong thiết kế/giao diện (nguồn: Screen_Items, tài liệu thiết kế). Không có → bỏ mục và ghi "Hệ thống không có phím tắt riêng".
4. Thông báo và lỗi thường gặp: bảng `Mã thông báo (MSG-xxx) | Nội dung hiển thị | Nguyên nhân | Cách xử lý` lấy từ `Message_List`. Mã lỗi hệ thống `ERR-<DOMAIN>-<NNN>` chỉ ghi khi người dùng nhìn thấy trên màn hình.
5. **FAQ (bắt buộc)**: tối thiểu mỗi luồng chính 2 câu hỏi, lấy từ: thông báo lỗi hay gặp, giới hạn đã biết (Punch List/Known Issues của D2 đã được khách chấp nhận), câu hỏi trong QA Tracker, quyền hạn. Mỗi câu: câu hỏi theo ngôn ngữ người dùng · trả lời ngắn · liên kết tới mục hướng dẫn. Cấm bịa câu hỏi "cho đủ số".
6. Giới hạn đã biết và cách tránh (từ Punch List/Known Issues, viết bằng ngôn ngữ người dùng, không lộ chi tiết kỹ thuật/bảo mật).
7. Liên hệ hỗ trợ và cách báo lỗi hiệu quả (cần cung cấp gì: thời gian, màn hình, ảnh, `requestId` nếu hệ thống hiển thị).

## 3. `Admin_Guide`
1. Vai trò và phân quyền (RBAC): bảng vai trò × quyền, lấy từ mục User Role/Permission của Requirement Specification và thiết kế; quy trình cấp/thu hồi quyền; nguyên tắc quyền tối thiểu.
2. Quản lý tài khoản: tạo, khoá, đặt lại mật khẩu, offboarding; chính sách mật khẩu/MFA nếu có trong thiết kế.
3. Cấu hình hệ thống: tham số quản trị được (từ thiết kế), ai được đổi, ảnh hưởng, cách khôi phục giá trị cũ.
4. Nhật ký hoạt động (Audit Log): xem ở đâu, lọc thế nào, thời gian lưu giữ (từ `Handover` mục 6/10), dữ liệu cá nhân trong log được xử lý ra sao.
5. **Cây quyết định xử lý sự cố tự phục hồi**: đọc các mã `INC-<NN>` THỰC TẾ từ `*_Runbook*.md` của D1 (không giả định `INC-01…06`). Mỗi nhánh: triệu chứng người dùng báo → câu hỏi phân loại (có/không) → `INC-xx` liên quan (liên kết tới heading trong Runbook) → việc admin tự làm được → khi nào chuyển cho vận hành/đội dự án. Vẽ bằng Mermaid `flowchart TD` với nhãn theo ngôn ngữ tài liệu. Sự cố không có trong Runbook ⇒ không bịa mã; đề xuất bổ sung Runbook ở D1.
6. Sao lưu/khôi phục, giám sát, kênh escalation: tóm tắt và dẫn chiếu `Handover`/`Runbook` (không chép lại).
7. FAQ quản trị (bắt buộc, cùng quy tắc nguồn như End User).
8. Lịch sử thay đổi và giới hạn đã biết.

## 4. `Quick_Start_Guide.md` (1 trang)
- URL truy cập (`links.production_url`).
- **KHÔNG ghi tài khoản/mật khẩu mặc định hay tài khoản thử nghiệm.** Ghi cách nhận tài khoản: người cấp (vai trò/kênh liên hệ), quy trình xin cấp, đổi mật khẩu lần đầu. Nếu cần tài khoản demo cho đào tạo: ghi "nhận từ <đầu mối> qua kênh bảo mật", không ghi giá trị.
- 5 bước thao tác cơ bản nhất (UI Cue).
- 3 lỗi hay gặp nhất + cách xử lý; kênh hỗ trợ.
