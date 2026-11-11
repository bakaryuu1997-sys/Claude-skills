# Archify — tích hợp tùy chọn vào bản kiến trúc (X2)

Tài liệu tham chiếu cho việc dùng sơ đồ Code-Backed của **Archify** cạnh bản `*_Architecture_v[N].html`.
Archify là công cụ NGOÀI bộ skill: không có trong repo, cài riêng. Không có Archify vẫn đủ bản Architecture (section 1 vẽ SVG thuần).

---

## 1. Hai file, hai vai trò

| File | Vai trò | Nơi lưu |
|---|---|---|
| `[TênDựÁn]_Architecture_v[N].html` | Bản tổng hợp chỉ đọc cho team và khách (sinh bởi `gen_architecture_html.py`) | `docs/X2_project-architecture/` |
| `[TênDựÁn]_Code_Backed.architecture.html` (Archify) | Sơ đồ khám phá: click node xem file/dòng code thật | cùng thư mục |

Bản gửi khách nên là MỘT file. Vì vậy KHÔNG nhúng iframe trỏ tới file Archify. Thay vào đó, mục 1 của bản Architecture có liên kết tương đối (`href="…Code_Backed.architecture.html"`) để người nhận mở riêng khi có cả thư mục.

---

## 2. Vá độ đọc (legibility)

Archify mặc định dùng chữ quá nhỏ (≈ 8–9px) và cắt chữ bằng ellipsis trong thẻ "Semantic Passport", nên tên file và số dòng không đọc được. Script vá CSS:

```bash
python <skills_dir>/x2-project-architecture/scripts/patch_archify_legibility.py "<file_or_dir>"
```

- Chỉ vá file có dấu hiệu Archify (`focus-chip`, `relationship-lens`, `archify-source-evidence-data`, `semantic-passport`). Trang Architecture và file HTML khác bị bỏ qua.
- Chạy lại nhiều lần an toàn: block CSS `custom-legibility-enhancement` được thay thế, không nhân đôi.
- Ghi file bằng tệp tạm rồi thay thế nguyên tử; nếu file không có `</head>` thì không vá.

Các cỡ chữ đặt bởi script (tham khảo): tiêu đề component 1.35rem/800; mô tả 1.05rem; vị trí dòng code 0.9rem (badge); đường dẫn file 0.95rem monospace, `word-break: break-all`.

---

## 3. Theme

Thẻ/bảng của Architecture dùng nền sáng (`#FFFFFF`), viền `1px solid #E5E7EB`, accent `#2E75B6`. Nếu Archify mở ở nền tối, chọn chế độ sáng trong Archify trước khi xuất (tham số `?theme=light` nếu bản Archify hỗ trợ) — KHÔNG chèn banner nền tối `#0F172A` vào trang doanh nghiệp.

---

## 4. Dữ liệu dẫn xuất mã nguồn (Code Evidence)

Archify nhúng dữ liệu bằng thẻ script JSON `archify-source-evidence-data`:

```json
{
  "schemaVersion": 1,
  "verified": true,
  "repository": { "url": "…", "revision": "<commit>", "shortRevision": "<7 ký tự>", "label": "…", "linkMode": "local-only" },
  "referenceCount": 0,
  "nodes": { "<node_id>": [ { "path": "src/…", "line": 1, "endLine": 150, "label": "…" } ] }
}
```

Chỉ đưa vào bản gửi khách khi `verified` là `true` và đường dẫn tồn tại trong repo. Không ghi URL repo riêng tư vào bản gửi khách (`linkMode: local-only` thì bỏ).
