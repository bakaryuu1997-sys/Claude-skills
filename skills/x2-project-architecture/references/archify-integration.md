# Hướng dẫn tích hợp Sơ đồ Động & Gắn mã nguồn Archify vào Project Architecture

Tài liệu tham chiếu chuẩn cho kỹ thuật tích hợp sơ đồ kiến trúc động (Archify Engine) vào trang điều hành tổng thể `project-architecture` (Bước X1).

---

## 1. Mô hình kiến trúc kép (Hybrid Architecture)

| Thành phần | Vai trò | Vị trí lưu trữ |
|---|---|---|
| **Trang điều hành tổng thể (Executive Compass)** | Nơi lưu trữ duy nhất gom toàn bộ 18 bước pipeline, cây màn hình, API specs, bảng CSDL, tiến độ Sprint | `docs/X1_project-architecture/[TênDựÁn]_Architecture_v[N].html` |
| **Sơ đồ Code-Backed tương tác (Archify Canvas)** | Khám phá trực quan: Click node xem file code thật, dòng code, Git commit hash | `docs/X1_project-architecture/[TênDựÁn]_Code_Backed.architecture.html` |
| **Sơ đồ tuần tự chuyển động (Archify Motion)** | Diễn hoạt luồng dữ liệu (WebSocket, sync, token dispatch) dạng hạt chuyển động | `docs/X1_project-architecture/[TênDựÁn]_[TênLuồng].sequence.html` |

---

## 2. Quy chuẩn đồng bộ giao diện (Theme Harmonization)

> ⚠️ **Anti-pattern nghiêm cấm:** Cắm dải banner nền đen (`#0F172A`) hoặc nhúng iframe dark mode trực tiếp vào giữa trang Dashboard doanh nghiệp màu sáng. Việc này làm đứt gãy thị giác và giảm tính chuyên nghiệp khi trình chiếu với khách hàng.

### Quy chuẩn Thẻ Launcher trong Section 1:
- **Nền thẻ:** `#FFFFFF` (Surface), viền mảnh `1px solid var(--border)`, bo góc `12px`.
- **Accent Border:** Viền trái `5px solid var(--secondary) (#2E75B6)`.
- **Màu chữ:** Tiêu đề dùng `--primary (#1F4E79)`, mô tả dùng `--text-muted (#6B7280)`.
- **Nút hành động:**
  - Nút Mở Sơ đồ Code: Nền xanh lá `#10B981`, chữ trắng, bóng đổ nhẹ.
  - Nút Mở Sơ đồ Tuần tự: Nền xanh dương nhạt `#F0F9FF`, chữ `#2E75B6`, viền `#BAE6FD`.

### Quy chuẩn Khung nhúng Preview:
- Thu gọn trong thẻ `<details>` có tiêu đề rõ ràng, badge `Interactive Preview`.
- Thuộc tính `src` của `<iframe>` **bắt buộc** kèm query param `?theme=light`.
- **Bắt buộc** có thanh điều khiển chuyển theme nhanh:
  ```html
  <button onclick="document.getElementById('archFrame').src='...architecture.html?theme=light'">☀️ Giao diện Sáng</button>
  <button onclick="document.getElementById('archFrame').src='...architecture.html?theme=dark'">🌙 Giao diện Tối</button>
  ```

---

## 3. Quy chuẩn hiển thị dẫn xuất mã nguồn (Semantic Passport Legibility)

> ⚠️ **Lỗi thường gặp ở Archify mặc định:** Thư viện Archify đặt cỡ chữ mặc định cực nhỏ (`0.5rem` = 8px cho code/path và `0.5625rem` = 9px cho nhãn) kèm theo thuộc tính cắt chữ `white-space: nowrap; text-overflow: ellipsis;`. Trên màn hình thực tế, người dùng không thể đọc được tên file và số dòng code.

### Giải pháp kỹ thuật bắt buộc:
Sau khi sinh file Archify HTML, BẮT BUỘC chạy script:
```bash
python3 <skills_dir>/x2-project-architecture/scripts/patch_archify_legibility.py "<file_or_dir_path>"
```

Bộ CSS tăng cường (`#custom-legibility-enhancement`) áp dụng các thông số chuẩn:
1. **Container `#focus-chip` / `.relationship-lens`:**
   - Mở rộng chiều rộng lên **480px** (thay vì 352px).
   - Bo góc `12px`, bóng đổ sâu `0 16px 48px rgba(0,0,0,0.45)`.
2. **Tiêu đề component (`.relationship-lens-title`):**
   - Font-size: **1.35rem (~21.6px)**, `font-weight: 800`.
3. **Mô tả chức năng (`.semantic-passport-source strong`):**
   - Font-size: **1.05rem (~16.8px)**, `font-weight: 800`, tự động xuống dòng (`white-space: normal`).
4. **Vị trí dòng code (`.semantic-passport-source code`):**
   - Font-size: **0.9rem (~14.4px)**, `font-weight: 800`, định dạng badge nổi bật với độ tương phản cao.
5. **Đường dẫn tệp mã nguồn (`.semantic-passport-source small`):**
   - Font-size: **0.95rem (~15.2px)**, `font-weight: 700`, font Monospace, `word-break: break-all`, không bao giờ bị cắt dấu ba chấm.

---

## 4. Định dạng dữ liệu dẫn xuất mã nguồn (Code Evidence Schema)

Dữ liệu code thật được nhúng trong thẻ script JSON tại trang Archify:
```html
<script id="archify-source-evidence-data" type="application/json">
{
  "schemaVersion": 1,
  "verified": true,
  "repository": {
    "url": "https://github.com/organization/project-name",
    "revision": "74b7c865f6960a4f48abc3cd34456c15493236f2",
    "shortRevision": "74b7c86",
    "label": "project-name",
    "linkMode": "local-only"
  },
  "referenceCount": 10,
  "nodes": {
    "ws_hub": [
      {
        "path": "src/websocket/server.ts",
        "line": 1,
        "endLine": 150,
        "label": "WebSocket broadcast server"
      }
    ],
    "auth_svc": [
      {
        "path": "src/services/auth.service.ts",
        "line": 1,
        "endLine": 130,
        "label": "Argon2id password hashing"
      }
    ]
  }
}
</script>
```

---

## 5. Quy chuẩn viết Script Python sinh HTML (Template Escaping)

Khi viết script Python dùng f-string (`f"""..."""`) để sinh HTML:
- Mọi dấu ngoặc nhọn `{` và `}` trong các khối CSS `<style>` **bắt buộc phải nhân đôi** thành `{{` và `}}`.
- Nếu không nhân đôi, Python sẽ coi nội dung CSS như một biến/biểu thức cần tính toán và ném ra lỗi `NameError: name 'background' is not defined`.
