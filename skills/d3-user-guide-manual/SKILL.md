---
name: d3-user-guide-manual
version: "3.17.4"
description: >-
  Biên soạn User Manual (người dùng cuối), Admin Guide và Quick Start: thao tác từng bước kèm UI Cue và
  ảnh chụp màn hình (đã che dữ liệu nhạy cảm), FAQ bắt buộc, lịch sử thay đổi, cây quyết định xử lý sự cố
  liên kết mã INC-xx của Runbook. Quick Start không chứa tài khoản mặc định. Trigger: "hướng dẫn sử dụng",
  "user manual", "user guide", "tài liệu hdsd", "sổ tay người dùng", "admin guide". Bước D3 — sau nghiệm thu D2.
---

# User Guide & Manual — Sổ Tay Hướng Dẫn Người Dùng Cuối & Quản Trị Viên

> ⚠️ **Mọi giá trị cụ thể trong skill và `references/` (tên màn hình, nút, mã thông báo, mã sự cố) là KHUNG MINH HỌA** — khi làm dự án thực phải lấy từ tài liệu thiết kế, prototype và Runbook của dự án đó; thiếu thì `[CẦN ĐIỀN]`, không bịa.

## Mục tiêu

Bộ tài liệu hướng dẫn hoàn chỉnh cho **người dùng cuối** và **quản trị viên**: làm quen nhanh, giảm yêu cầu hỗ trợ, vận hành trơn tru sau go-live.

Nguyên tắc biên soạn:
- **Ngôn ngữ người dùng**: từ nghiệp vụ thân thiện, tránh thuật ngữ lập trình khi viết cho người dùng cuối.
- **Từng bước + UI Cue + ảnh**: mỗi thao tác là một bước đánh số có ký hiệu vị trí UI (`[<vị trí>: <nhãn>]`, theo ngôn ngữ tài liệu) và ảnh chụp màn hình — `references/screenshot-and-masking.md` (nguồn ảnh, quy cách, **che dữ liệu nhạy cảm**, khung giữ chỗ khi chưa chụp được).
- **FAQ bắt buộc** trong cả End User Manual và Admin Guide, lấy từ nguồn thật (Message_List, QA Tracker, giới hạn đã biết của D2) — không bịa cho đủ số.
- **Chỉ ghi điều có thật**: phím tắt, nút, thông báo, vai trò lấy từ thiết kế/prototype; không có thì bỏ mục hoặc `[CẦN ĐIỀN]`.
- **Không lộ credential**: tài liệu và Quick Start KHÔNG chứa tài khoản/mật khẩu mặc định hay thử nghiệm, token, URL nội bộ.
- **Quản trị phiên bản**: mỗi tài liệu có bảng *Lịch sử thay đổi*; chạy lại sinh `_v2`, `_v3`.
- **Ngôn ngữ & thương hiệu**: ngôn ngữ/font theo `settings.languages.client_facing` (`i18n-policy.md`; `ja` ⇒ 100% tiếng Nhật; nhiều ngôn ngữ ⇒ một file cho mỗi ngôn ngữ). Không lộ mã bước nội bộ (`A1`…`D3`) hay tên nhà thầu cũ.

Thư mục xuất: `<workspace_folder>/docs/D3_user-guide-manual/`.

---

## Bước -1 — Đọc Project Context (nếu có)

> **Giao thức chuẩn: `a1-project-init/references/context-protocol.md`** (KHÔNG chép lại): đọc bằng `load_context.py` + `cget()`; ghi bằng `update_context.py`. `NO_CONTEXT` → chạy chế độ hỏi/suy luận thủ công.

Có context → tự trích: `project.name`, `project.client`, `links.production_url` (URL truy cập), `release{}` (phiên bản hệ thống), `settings.languages`; liên hệ hỗ trợ từ `team[]` có `side=vendor` (vai trò hỗ trợ) và kênh bảo hành trong `Warranty_Scope` của D2. Danh sách vai trò người dùng KHÔNG nằm trong context — lấy từ mục User Role/Permission của Requirement Specification (A2) và thiết kế cơ bản.

## Bước 0 — Thu thập đầu vào

1. `*_Basic_Design*.docx` và `*_BasicDesign_Workbook*.xlsx` (B2): `Screen_List`, `Screen_Items` (nút, trường), `Message_List` (thông báo/lỗi), Business Flow.
2. `*_Prototype_v[N].html` (A3): luồng thao tác và bố cục (chỉ làm nguồn ảnh khi chưa có bản chạy).
3. `*_Requirement_Specification*.xlsx` (A2): vai trò, ma trận phân quyền.
4. `*_Runbook*.md` (D1): mã sự cố `INC-<NN>` thực tế → cây quyết định của Admin Guide.
5. `*_UAT_SignOff_Workbook*.xlsx` (D2): `Punch_List_Minor_Defects` (giới hạn đã biết → FAQ/lưu ý) và `Warranty_Scope` (kênh hỗ trợ).

---

## Bộ tài liệu (3 file)

| STT | File | Định dạng | Tiêu chuẩn tối thiểu |
|---|---|---|---|
| 1 | `[TênDựÁn]_User_Manual_EndUser_v1.docx` | Word | Đăng nhập/đổi mật khẩu; hướng dẫn theo luồng nghiệp vụ (UI Cue + ảnh đã che dữ liệu nhạy cảm); bảng phím tắt (chỉ khi có thật); thông báo & lỗi thường gặp từ `Message_List`; **FAQ**; giới hạn đã biết; hỗ trợ; lịch sử thay đổi + glossary |
| 2 | `[TênDựÁn]_Admin_Guide_v1.docx` | Word | RBAC; tài khoản; cấu hình; Audit Log; **cây quyết định sự cố tự phục hồi** liên kết các `INC-xx` có trong Runbook; sao lưu/giám sát (dẫn chiếu D1); **FAQ quản trị**; lịch sử thay đổi |
| 3 | `[TênDựÁn]_Quick_Start_Guide_v1.md` | Markdown | 1 trang: URL truy cập, **cách nhận tài khoản (KHÔNG ghi tài khoản/mật khẩu mặc định)**, 5 bước cơ bản, 3 lỗi hay gặp, kênh hỗ trợ |

Khung nội dung từng tài liệu: **`references/manual-templates.md`**. Cây quyết định vẽ Mermaid `flowchart TD`; khi nhúng vào docx phải render ra hình hoặc trình bày bằng bảng quyết định — không để mã Mermaid thô trong Word.

## Quy trình thực hiện

1. Đọc context + đầu vào; liệt kê vai trò, luồng, màn hình, thông báo, `INC-xx`.
2. Soạn User Manual theo luồng nghiệp vụ; Admin Guide; Quick Start.
3. Chèn ảnh theo `screenshot-and-masking.md`; ảnh chưa có ⇒ khung giữ chỗ `[ẢNH CẦN CHỤP: …]` và danh sách ảnh cần chụp ở cuối response.
4. Kiểm: không credential, không thông tin cá nhân thật, mọi `INC-xx` trong cây quyết định tồn tại trong Runbook, FAQ có nguồn, ngôn ngữ đồng nhất, không mã bước nội bộ.
5. Lưu `docs/D3_user-guide-manual/`; `append activity_log` bằng `update_context.py`.

---

**Dựng file Word — BẮT BUỘC dùng bộ chung:** spec JSON (đầu file `a1-project-init/scripts/docx_build.py`) → `python <skills_dir>/a1-project-init/scripts/docx_build.py spec.json <out>.docx`. Font ja = Yu Gothic (đã đặt eastAsia).

## 🔗 Workflow Integration

**Nguồn sự thật pipeline: `<skills_dir>/a1-project-init/references/pipeline.md`** — KHÔNG vẽ lại pipeline trong response; nếu nơi khác mô tả thứ tự lệch, pipeline.md thắng.

- **Bước hiện tại:** D3 — User Guide & Manual (hoàn tất bàn giao tài liệu cho người dùng)
- **Input từ:** B2 (màn hình, thông báo) · A3 (luồng) · D1 (`Runbook` — mã `INC-xx`) · D2 (Punch List, Warranty_Scope)
- **Output cho:** Người dùng cuối và quản trị viên vận hành hệ thống độc lập
- **Bước kế tiếp:** Hoàn tất chu trình dự án; chuyển sang bảo hành/vận hành

**Kết thúc response:** theo quy ước chung trong `pipeline.md` (≤ 6 dòng ✅→▶; skill tạo/sửa file append `activity_log[]` bằng `update_context.py`).

---

## Self-Improvement Loop
Cuối tác vụ tự trả lời 3 câu: có lỗi/workaround không? người dùng có đính chính không? có quy tắc mới giúp lần sau không? Không có gì → im lặng.
Có phát hiện HỆ THỐNG → in `💡 Đề xuất cải thiện` (≤ 3 dòng) rồi áp dụng theo quy trình duy nhất: `a1-project-init/references/self-improvement.md`.
Áp dụng: 1 skill/tác vụ, ≤ 40 dòng thêm, không xóa quy tắc, chạy `scripts/skill_self_update.py`; báo skill · thay đổi · commit · `git revert <hash>`.
