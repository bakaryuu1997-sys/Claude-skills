# Đầu vào `scripts/cr_impact.py` và cập nhật context

## Trường đầu vào

| Trường | Nguồn | Ghi chú |
|---|---|---|
| `cr_id` | số thứ tự CR của dự án, định dạng `CR-001` | Đọc `change_requests[]` để lấy số tiếp theo; không dùng `CR001`/`CR#001` |
| `cr_type` | người dùng + phân loại (ADDITION / MODIFICATION / REMOVAL / REPLACEMENT / URGENT) | |
| `items[]` | phân tích scope: mỗi dòng là một hạng mục có `kind` = new (tính năng mới), rework (sửa phần đã làm/đã thiết kế), regression (test lại phần bị ảnh hưởng) | Ước lượng theo quy tắc estimate của A6, thang BD/DD/Dev/UT/IT |
| `settings.md_per_person_month` | `project-context.json → settings` | **Bắt buộc.** Không tự đặt số (pipeline.md: một nguồn duy nhất) |
| `settings.buffer_percent` | `settings` | **Bắt buộc** |
| `settings.sprint_duration_weeks` | `settings` | |
| `capacity_md` | `estimates.team_capacity_per_sprint` | |
| `original_total_md` | `estimates.total_md` | Để tính % tác động |
| `rate_per_pm`, `currency` | Hợp đồng / SOW (B0) | Chỉ có khi hợp đồng ghi đơn giá; thiếu thì bỏ dòng chi phí và ghi `[CẦN ĐIỀN]` |

Hệ số rework nhân thêm (nếu dự án dùng): **không có mặc định trong skill**. Chỉ áp dụng khi khách/PM ghi rõ trong hợp đồng hoặc biên bản; khi đó ghi nguồn vào Decision Log. Không dùng số "2.5–3.0×" như sự thật chung.

## Cập nhật context sau khi khách quyết định

Schema item của `change_requests[]`: `id` (bắt buộc), `status` (bắt buộc: pending | received | in analysis | negotiating | approved | rejected | deferred), `title`, `impact_md`, `date`.

```
# Thêm CR mới (ghi JSON vào file rồi --file; PowerShell làm mất dấu " nếu truyền trực tiếp)
python <skills_dir>/a1-project-init/scripts/update_context.py <ws> append change_requests --file cr_item.json

# Cập nhật trạng thái khi khách quyết định (merge theo id)
python <skills_dir>/a1-project-init/scripts/update_context.py <ws> patch change_requests CR-001 '{"status":"approved","impact_md":12.9,"date":"2026-11-11"}'
```

Chỉ đặt `approved` sau khi có biên bản/email xác nhận của khách (lưu đường dẫn vào Decision Log). `check_gate.py` coi `pending`, `received`, `in analysis`, `negotiating` là CR chờ quyết định (cảnh báo, không chặn).
