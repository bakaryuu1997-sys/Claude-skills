# ADR — Architecture Decision Record (mẫu chuẩn)

> Mỗi quyết định kiến trúc quan trọng (chọn DB, chọn framework, tách service, chọn cơ chế xác thực, chọn chiến lược cache…) được ghi thành MỘT file ADR, đánh số tăng dần, không bao giờ xóa — chỉ đổi trạng thái. Lưu tại `<workspace_folder>/docs/X2_project-architecture/adr/ADR-NNN-<slug>.md`. Mục đích: người mới hiểu VÌ SAO hệ thống như vậy, và không ai tranh luận lại quyết định cũ mà thiếu dữ kiện mới.

## Trạng thái vòng đời

`Proposed` (đề xuất, chờ duyệt) → `Accepted` (đã chốt) → `Superseded by ADR-MMM` (bị thay thế, giữ nguyên file) hoặc `Deprecated` (không còn áp dụng). Không sửa nội dung ADR `Accepted`; muốn đổi → tạo ADR mới và đánh dấu cũ là `Superseded`.

## Mẫu

```markdown
# ADR-NNN: <Tiêu đề quyết định ngắn, dạng động từ>

- **Trạng thái:** Proposed | Accepted | Superseded by ADR-MMM | Deprecated
- **Ngày:** YYYY-MM-DD
- **Người quyết định:** <tên/vai trò, lấy từ team[] trong context>
- **Liên quan:** FEAT-…, NFR-…, TM-…, ADR-… (nếu có)

## Bối cảnh (Context)
Vấn đề gì đang buộc phải quyết định? Ràng buộc nào (hợp đồng, nhân sự, hạ tầng, thời hạn, NFR)? Số liệu nếu có.

## Các phương án đã xét
| Phương án | Ưu điểm | Nhược điểm | Chi phí vận hành |
|---|---|---|---|
| A | … | … | … |
| B | … | … | … |

## Quyết định (Decision)
Chọn phương án nào và VÌ SAO (một đoạn). Nêu rõ điều gì KHÔNG được làm theo quyết định này.

## Hệ quả (Consequences)
- Tích cực: …
- Tiêu cực / đánh đổi chấp nhận: …
- Việc phải làm kèm theo: … (đưa vào `known_issues[]` hoặc `activity_log` nếu cần theo dõi)

## Điều kiện xem xét lại
Khi nào quyết định này nên được đánh giá lại? (vd: vượt 10k user đồng thời, đổi nhà cung cấp, chi phí vượt ngưỡng)
```

## Quy tắc đi kèm

- Quyết định nào ảnh hưởng `tech_stack` trong context → cập nhật context cùng lúc (`update_context.py set tech_stack.database …`) và ghi `activity_log`.
- Ngôn ngữ ADR theo `settings.languages.internal` (xem `a1-project-init/references/i18n-policy.md`). Thuật ngữ kỹ thuật giữ nguyên tiếng Anh.
- Mỗi ADR tối đa 2 trang. Dài hơn → quyết định đang gộp nhiều việc; tách ra.
- Tạo `docs/X2_project-architecture/adr/README.md` là bảng mục lục: số, tiêu đề, trạng thái, ngày. x2 cập nhật bảng này khi thêm ADR.
