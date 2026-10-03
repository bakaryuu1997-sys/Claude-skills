# BÁO CÁO REVIEW BỘ SKILL — PRODUCTION-GRADE AUDIT

**Ngày:** 08/07/2026 · **Reviewer:** Senior AI Systems Architect (strict mode)
**Phạm vi:** Toàn bộ skill tùy chỉnh trong thư mục skills + hạ tầng dùng chung (pipeline.md, skills-manifest.json, load_context.py, validate_context.py, skill_doctor.py, menu scripts, fill_dev_estimate.py, references/)

> ⚠️ **Phát hiện số 0 — trước khi bắt đầu:** Bạn nói "17 Skills". Thực tế manifest và thư mục có **23 skill tùy chỉnh**. Chính `pipeline.md` — file tự nhận là "nguồn sự thật duy nhất" — vẫn viết *"KHÔNG sửa 17 skill còn lại"*. Nguồn sự thật của bạn đang chứa hằng số lỗi thời về chính kích thước của hệ thống. Đây là triệu chứng thu nhỏ của vấn đề lớn nhất toàn bộ review này: **hợp đồng viết bằng văn xuôi thì không tự cập nhật, không tự thực thi.**

---

## PHẦN I — ĐÁNH GIÁ TOÀN HỆ THỐNG (mục 1–12)

### 1. Architecture — 7/10

**Điểm tốt (thật sự tốt, không phải khen xã giao):**
- Mô hình hub-and-spoke: `project-init` là hub (context + schema + validator + pipeline + style + safety), 22 skill là spoke. Đúng pattern.
- Ranh giới được viết tường minh ở những chỗ dễ nhầm nhất: basic-design ≠ detail-design, test-plan ≠ test-execution, estimate ≠ estimate-template-fill, code-review nội bộ ≠ engineering:code-review. Phần lớn hệ thống skill ngoài kia không làm được điều này.
- Gate có ý thức (P1 > 3 → chặn estimate/kickoff) và ghi rõ "nơi thi hành là ở downstream skill" — hiểu đúng bản chất gate.

**Điểm trừ nghiêm trọng:**
1. **Vi phạm SRP ở api-design**: 1 skill sinh 3 output khác bản chất (Excel spec + Postman collection + OpenAPI YAML) kèm logic re-run merge. 428 dòng. OpenAPI + Postman là **dẫn xuất thuần túy** từ data — đáng lẽ là script (`gen_postman.py`, `gen_openapi.py`), không phải văn xuôi hướng dẫn LLM viết JSON bằng tay.
2. **Chồng lấn thật sự tồn tại**: `project-status` và `project-architecture` cùng cài đặt lại logic "quét file theo manifest pattern + đọc activity_log + tính staleness". Hai mô tả bằng văn xuôi của cùng một thuật toán = sẽ lệch nhau. Phải tách thành 1 script `compute_status.py` trả JSON, hai skill chỉ render.
3. **Xung đột nguồn sự thật test**: `test-plan` có 17 cột trong đó có `Actual Result`, `Status`, `Bug Ticket ID` (cột 11–13) — tức là file test plan CŨNG lưu kết quả thực thi. `test-execution` lại có tracker riêng lưu pass/fail/bug. **Hai file cùng lưu kết quả test → không có nguồn sự thật.** Ranh giới "plan sinh case / execution chạy" bị chính schema cột phá vỡ.
4. **menu tự mâu thuẫn**: tuyên bố "KHÔNG có nội dung hardcode nào trong file này" nhưng chứa bảng decision-tree 18 dòng hardcode map task→skill. Thêm skill mới = phải sửa menu = đúng cái mà menu nói không cần làm.
5. `handover-doc` 340 dòng trong đó ~250 dòng là template mẫu cực kỳ cụ thể (SSH command, IP, URL fpt-canteen). Đây không phải skill — đây là một tài liệu mẫu của MỘT dự án được đội lốt skill.

### 2. Prompt Engineering Quality — 6.5/10

**Tốt:** Progressive disclosure đúng chuẩn Anthropic (SKILL.md + references/); mô tả frontmatter có trigger + anti-trigger ("KHÔNG dùng cho..."); quy tắc chống bịa ("không đọc được → báo rõ, không bịa") xuất hiện nhất quán; cảnh báo "VÍ DỤ MINH HỌA" + rule D10 enforce nó.

**Lỗi cụ thể tìm được (kiểm chứng trên file thật):**

| # | File | Lỗi | Bằng chứng |
|---|---|---|---|
| P1 | `project-timeline/SKILL.md` | Header ghi **"Cấu trúc file Excel (7 sheets)"** nhưng liệt kê **Sheet 1 → Sheet 8** | Sheet 8: Change Log tồn tại ngay dưới header "7 sheets" |
| P2 | `db-design/SKILL.md` | Header ghi **"Cấu trúc file Excel (5 sheets)"** nhưng liệt kê **6 sheet** | "### Sheet 6: Assumptions & Migration Notes" |
| P3 | `test-plan/SKILL.md` | Header "(6 sheets)" nhưng cấu trúc thật là **N+6 sheet** (mỗi module 1 sheet) | "Sheet 3 → N+2: Test Cases per Module" |
| P4 | `pipeline.md` | "KHÔNG sửa **17** skill còn lại" — số sai (23 skill) | dòng 4 pipeline.md |
| P5 | `excel-style.md` vs 6 skill | excel-style nói *"không định nghĩa lại trong từng skill"* — nhưng api-design, db-design, estimate, test-plan, project-timeline, sprint-review **đều lặp lại nguyên khối** "Font Arial 9–10, header navy #1F4E79, zebra, border #AAAAAA, freeze A4" ngay sau câu "chỉ liệt kê màu ĐẶC THÙ" | Kiểm tra trực tiếp 6 file |
| P6 | Mọi skill | `<skills_dir>` và `<workspace_folder>` là placeholder **không được định nghĩa ở đâu cả** — không skill nào nói cách resolve. Model phải đoán. Trên máy thật, đường dẫn skill dưới bash khác đường dẫn dưới Read tool | Không có định nghĩa trong pipeline.md/manifest |
| P7 | `estimate` vs `estimate-template-fill` | Cả hai tuyên bố md_per_person_month "PHẢI trùng, nguồn duy nhất là context" — nhưng khi KHÔNG có context, estimate mặc định **22**, template-fill mặc định **20** (và script hardcode `"20"`). Chính kịch bản không-context là lúc hai file báo giá lệch nhau ~10% | fill_dev_estimate.py: `"md-per-pm", "20"` |
| P8 | `estimate` | "BD 10–20% Dev, DD 15–30%, UT 20–35%..." — **khoảng, không có quy tắc chọn điểm** → hai lần chạy cùng input cho hai tổng MD khác nhau. Phi tất định ở chính con số khách hàng ký | Bảng "Tỷ lệ tham khảo" |
| P9 | `api-design` re-run | "Chỉ sinh phần MỚI hoặc THAY ĐỔI — giữ nguyên phần không đổi" — **không có thuật toán diff**: so khớp endpoint theo khóa nào (URL+method?), xử lý đổi tên thế nào, cell nào được ghi đè? LLM tự sáng tác merge logic mỗi lần chạy = kết quả không lặp lại được | Mục "Chế độ chạy lại" |
| P10 | `basic-design`, `detail-design` | **Không có re-run mode** trong khi api-design/test-plan có → chạy lại là regenerate docx từ đầu, mất mọi chỉnh sửa tay/chữ ký của khách trên bản cũ. Lifecycle không đồng đều giữa các skill | Không có mục re-run trong 2 file |

**Câu chữ yếu điển hình** (mỗi câu kèm đề xuất — chi tiết rewrite ở mục 16):
- *"Không hỏi lại về những điểm nhỏ"* (api-design, db-design, estimate) — "điểm nhỏ" không được định nghĩa → model tự quyết cả điểm lớn. Cần ngưỡng: "điểm ảnh hưởng < 3 MD".
- *"Kiểm tra syntax Mermaid hợp lệ trước khi lưu"* (basic-design, detail-design) — kiểm bằng gì? Không có tool/command → chỉ là lời cầu nguyện. Hoặc chỉ định `mmdc --validate`/quy tắc cụ thể, hoặc bỏ.
- *"Đủ đẹp, không cần hoàn hảo"* (prototype-ui) — không đo được; đã có checklist "Đủ tốt để demo" tốt hơn nhiều ngay bên dưới → xóa câu này.

### 3. AI Reliability — 5.5/10

1. **Toàn bộ pipeline là advisory, không enforced.** Gate "P1 > 3 → DỪNG" phụ thuộc việc LLM (a) nhớ mở QA_Tracker, (b) đếm đúng, (c) tự nguyện dừng. Không có script `check_gate.py` nào tồn tại. Với LLM, quy tắc không được code hóa là quy tắc thi hành ~80–90% thời gian, không phải 100%.
2. **Bug thực chứng trong skill-doctor** (chạy trực tiếp ngày 08/07/2026): `python3 skill_doctor.py <skills_dir>` trả về **44 FAIL** — toàn bộ là false positive trên skill hệ thống (docx, pdf, pptx, xlsx, theme-factory, schedule...) vì script **không có allowlist/marker phân biệt skill của bộ với skill ngoài**. Hệ quả kép: (a) exit code luôn = 1 → "CI" luôn đỏ → alarm fatigue, người dùng học cách bỏ qua linter; (b) SKILL.md của skill-doctor lệnh *"sửa xong chạy lại đến khi sạch"* → **vòng lặp không bao giờ thoát** vì không thể "sửa" skill của Anthropic. Đây chính xác là loại lỗi mà skill-doctor sinh ra để bắt.
3. **`update_context()` không phải script** — nó là snippet Python trong SKILL.md của project-init, được 20+ skill "gọi" bằng cách... tự gõ lại từ trí nhớ. `load_context.py` được tách thành script (đúng), còn nhánh GHI — nhánh nguy hiểm hơn — thì không. Atomic write có, nhưng không có lock: hai skill đọc-sửa-ghi gần nhau vẫn lost-update.
4. **Mâu thuẫn chỉ thị:** footer chung nói *"MỌI skill → append activity_log[]"*, nhưng project-status tuyên bố *"KHÔNG ghi gì vào context"*, code-review không tạo file nhưng vẫn mang footer append. "MỌI" là sai — và với LLM, một từ "MỌI" sai là một lần model phân vân.
5. **Vòng lặp tiềm ẩn:** sprint-review → "velocity <70% 2 sprint → /estimate lại" → estimate → timeline → sprint-review. Không có điều kiện thoát/ceiling cho số lần re-estimate.
6. Điểm cộng: quy tắc "reproduce trước, fix sau" (dev-implement), "không tuyên bố pass phase khi chưa đạt exit criteria" (test-execution), validate .ics bằng parse lại (project-timeline), "verify sau khi tạo file" (estimate-template-fill), self-check HTML (project-architecture) — đây là các verification loop đúng nghĩa.

### 4. Scalability — 6/10

- **100 skill:** Manifest + pipeline.md trung tâm là đúng hướng, NHƯNG: (a) footer "Workflow Integration" + block "Bước -1" bị dán vào từng skill (~15–20 dòng × 23 file) — đổi hợp đồng = sửa 23 file, ở 100 skill = sửa 100 file; (b) bảng decision-tree trong menu và bảng I/O trong pipeline.md tăng tuyến tính; (c) đánh số A0–D1 chỉ mô tả MỘT pipeline waterfall-scrum outsourcing — dự án loại khác (maintenance, R&D, data) không có chỗ đứng.
- **1000 prompts:** Không có eval harness (tự thừa nhận trong skill-doctor: "eval đầy đủ xem roadmap"). Ở quy mô đó, không eval = không dám sửa bất kỳ skill nào.
- **100 agents:** project-context.json là file JSON không lock → 100 agent ghi đồng thời sẽ ăn thịt nhau. activity_log append-only vào 1 file JSON cũng sẽ phình vô hạn (không có rotation/compaction).
- Điểm cộng lớn: skill-doctor là **regression test cho prompt** — tư duy đúng, hiếm gặp; chỉ cần sửa implementation.

### 5. Maintainability — 7/10

- **Tốt:** naming nhất quán (kebab-case, khớp folder), version per-skill, manifest sync 2 chiều có linter, references/ tách đúng chỗ, script có docstring + usage.
- **Xấu:** (a) 3 hệ version song song không liên kết (context schema "1.0", manifest "3.2.0", skill 3.0.0–3.2.0) — không có CHANGELOG file thực tế dù skill-doctor nhắc "thêm dòng CHANGELOG"; (b) khối boilerplate lặp 23 lần (xem 4a); (c) `check_menu_sync.py` chứa `known_external` hardcode có phần tử trùng lặp `"tên-skill"` xuất hiện 2 lần trong set literal — dấu hiệu copy-paste không review; (d) `__pycache__/*.pyc` bị commit trong project-init/scripts — rác build trong source; (e) thuật toán DFS phát hiện circular FK nằm dạng code block TRONG SKILL.md (db-design) thay vì `scripts/` — LLM sẽ gõ lại nó mỗi lần, có thể sai.

### 6. Production Readiness — CÓ ĐIỀU KIỆN (tổng thể: chưa)

Từng skill xem bảng mục 13. Tổng thể: **NO cho "production AI operating system", YES cho "công cụ tăng tốc nội bộ có người giám sát"**. Lý do NO: gate không enforced, không eval, skill-doctor đang hỏng khi chạy trên môi trường thật, hai nguồn sự thật kết quả test, phi tất định ở con số báo giá. Mọi output đều dùng được nếu có con người review — nhưng "production" nghĩa là dùng được khi KHÔNG có.

### 7. Missing Capabilities

| Thiếu | Mức | Ghi chú |
|---|---|---|
| **Eval harness (golden outputs)** | 🔴 Critical | Tự thừa nhận. Không eval = không dám refactor. Tối thiểu: 3 bộ input mẫu → chạy skill → assert cấu trúc file output (số sheet, số cột, công thức là `=`) |
| **`update_context.py` + `check_gate.py` dạng script** | 🔴 Critical | Nhánh ghi context và gate P1/quality-gate phải là code, không phải văn xuôi |
| **`compute_status.py` chung** | 🟠 High | Gộp logic staleness/document-scan của project-status + project-architecture + detail-design |
| **Re-run/merge mode cho basic-design, detail-design, handover** | 🟠 High | Docx bị khách sửa tay — regenerate là mất dữ liệu |
| **Locking / transaction cho context** | 🟠 High | flock hoặc chuyển sang SQLite |
| **Log rotation cho activity_log** | 🟡 Medium | JSON array phình vô hạn |
| **Cost/token budget** | 🟡 Medium | api-design bảo đọc lại toàn bộ Excel cũ mỗi re-run — không có giới hạn |
| **CHANGELOG.md thực + release process** | 🟡 Medium | Được nhắc tới nhưng không tồn tại |
| **i18n strategy** | 🟢 Nice | Output trộn VN/EN/JP tùy skill, không có quy tắc chọn ngôn ngữ deliverable theo khách |
| **Skill mới nên có:** `/gate-check` (chạy mọi gate, in PASS/FAIL), `/doc-sync` (đồng bộ hàng loạt khi spec đổi — hiện staleness chỉ được *phát hiện*, việc *sửa* vẫn thủ công từng skill) | | |

### 8. Redundancy — phải xử lý

1. **Khối Excel style lặp ở 6 skill** (P5 ở trên) — xóa, giữ đúng 2–4 dòng đặc thù. Tiết kiệm ~60 dòng và loại nguy cơ style lệch nguồn.
2. **Block "Bước -1" (~12 dòng) × 23** — thay bằng 1 dòng: `> Bước -1: chạy load_context.py — quy trình chuẩn xem project-init/references/context-protocol.md`.
3. **Footer "Hiển thị cuối response..." nguyên văn × 23** — chuyển vào pipeline.md, mỗi skill chỉ giữ 4 dòng bước hiện tại/input/output/kế tiếp.
4. **Staleness logic × 3** (project-status, project-architecture, detail-design) — 1 script.
5. **Khối "An toàn đầu vào" lặp nguyên văn ở 5 skill** — đã có input-safety.md, chỉ cần 1 dòng trỏ.

Ước tính tổng: **~400–500 dòng (~15–20% token toàn bộ)** cắt được mà không mất thông tin.

### 9. Performance

- **Token:** SKILL.md trung bình ~220 dòng, top 4 (api-design 428, timeline 382, db-design 372, prototype-ui 359) đều nạp toàn bộ vào context khi kích hoạt. Phần lớn nội dung nặng (bảng màu, template Excel chi tiết) chỉ cần **lúc build file** chứ không cần lúc *suy luận* — đáng lẽ nằm ở references/ (db-design, timeline, prototype-ui đã làm một phần; api-design chưa).
- **Latency/reasoning:** mỗi skill yêu cầu chuỗi load_context → đọc nhiều Excel → viết Python → chạy → verify. Đúng về chất lượng, đắt về bước. Chỗ tối ưu rõ nhất: mọi output Excel dùng chung 1 thư viện `excel_builder.py` (style áp tự động) thay vì mỗi lần LLM viết lại 200 dòng openpyxl formatting từ mô tả văn xuôi — giảm cả token, thời gian lẫn xác suất lỗi format.
- Điểm cộng: quy ước "tối đa 6 dòng cuối response, không ASCII box" + rule D09 là kiểm soát token output có chủ đích — tốt.

### 10. Best Practices — so với industry

| Practice | Chuẩn ngành | Bộ skill này |
|---|---|---|
| Progressive disclosure (Anthropic) | SKILL.md gọn + references | ✅ Có, chưa triệt để (api-design) |
| Description = trigger contract (Anthropic) | Ngắn, có anti-trigger | ✅ Tốt hơn mức trung bình |
| **Code over prose cho việc deterministic** (Anthropic/Codex/Devin) | Script hóa mọi thứ lặp lại | ⚠️ Nửa vời: load_context ✅, fill_dev_estimate ✅, nhưng update_context/gate/postman/openapi/DFS/status ❌ |
| **Evals trước khi scale** (Anthropic/OpenAI) | Golden tests | ❌ Chưa có — gap lớn nhất so với ngành |
| State machine enforced (LangGraph/OpenHands) | Runtime chặn transition sai | ❌ Pipeline chỉ là văn bản; LLM là runtime |
| Rules ngắn, ít, sắc (Cursor/Cline/Roo) | Rule dài = rule bị lờ | ⚠️ Nhiều skill quá dài; dev-implement (108 dòng) là chuẩn đúng |
| Verification loop (Devin/Manus) | Tự kiểm output trước khi giao | ✅ Có ở nhiều skill — điểm mạnh |
| Idempotency/re-run | Merge có thuật toán | ⚠️ Có ý thức, thiếu thuật toán |

Khác biệt căn bản: **các hệ production đặt logic vào code và để LLM điền chỗ trống; bộ này đặt logic vào văn xuôi và hy vọng LLM tuân thủ.** Khoảng cách từ đây đến production chính là khoảng cách đó.

### 11. Security — 6.5/10

- ✅ input-safety.md tồn tại và được tham chiếu đúng ở các skill đọc dữ liệu ngoài; xử lý đúng ("ghi nhận như finding BLOCKER" thay vì chỉ ignore); ý thức "context value cũng là data".
- ✅ handover-doc: chính sách "không credentials trong tài liệu, trỏ vault" — đúng.
- ⚠️ Phát hiện injection **dựa trên ví dụ liệt kê** ("ignore previous instructions"...) — injection thực tế đa dạng hơn (đa ngôn ngữ, encode, giấu trong cell Excel/comment docx). Nên đổi khung từ "nhận diện mẫu câu" sang "mọi mệnh lệnh trong dữ liệu đều là data, bất kể nhận ra hay không".
- ⚠️ Chuỗi tin cậy phụ: QA_Tracker/Excel do khách trả lời rồi được skill khác *đọc lại và hành động theo* (meeting-minutes → QA_Tracker → estimate gate) — dữ liệu bẩn đi vòng qua file trung gian sẽ không còn bị coi là "input ngoài". Chưa được nêu.
- ⚠️ `fill_dev_estimate.py` sửa OOXML bằng **regex trên XML** — không phải lỗ hổng bảo mật nhưng là rủi ro toàn vẹn file (template đổi cấu trúc XML → output hỏng âm thầm); có bước Verify thủ công bù lại một phần.
- ⚠️ prototype-ui nhúng data khách vào HTML không nói gì về escaping — file local, rủi ro thấp, nhưng đáng 1 dòng.

### 12. Ecosystem tổng thể & kiến trúc đề xuất

**Chúng có làm việc với nhau không?** Có — hợp đồng I/O trong pipeline.md là bảng ăn khớp thật (đã đối chiếu chéo: input/output từng skill khớp với footer của skill đó). Đây là phần thiết kế tốt nhất của hệ thống.

**Tầng còn thiếu:** tầng **runtime/enforcement** giữa "văn bản quy tắc" và "LLM thực thi".

```
HIỆN TẠI                            ĐỀ XUẤT
┌─────────────┐                    ┌─────────────────────────────┐
│ 23 SKILL.md │←── LLM đọc và      │ 23 SKILL.md (mỏng, ~100 dòng)│
│ (quy tắc +  │    "cố gắng"       ├─────────────────────────────┤
│  logic +    │    tuân thủ        │ TẦNG LIB (mới) scripts/lib/  │
│  template)  │                    │  context_io.py (read+WRITE  │
├─────────────┤                    │   +lock)  · gates.py        │
│ 6 script    │                    │  excel_builder.py · status.py│
│ rời rạc     │                    │  gen_postman.py/openapi.py  │
└─────────────┘                    ├─────────────────────────────┤
                                   │ TẦNG EVAL (mới) evals/       │
                                   │  golden inputs → assert      │
                                   │  output structure            │
                                   ├─────────────────────────────┤
                                   │ skill-doctor (sửa allowlist) │
                                   │  = CI cho cả 3 tầng          │
                                   └─────────────────────────────┘
```

Có redesign không? **Không đập đi xây lại** — topology hub-and-spoke đúng rồi. Chỉ **hạ logic từ văn xuôi xuống code** và thêm tầng eval.

---

## PHẦN II — BẢNG ĐIỂM TỪNG SKILL (mục 13)

Thang 0–10 mỗi tiêu chí; Overall /100 (có trọng số: Reliability + Prompt ×1.5). PR = Production Ready.

| # | Skill | Arch | Prompt | Reliab | Maint | Scal | Sec | PR | **/100** |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **dev-implement** | 9 | 8 | 8 | 9 | 8 | 8 | ✅ YES | **85** |
| 2 | **meeting-minutes** | 8 | 8 | 8 | 8 | 8 | 8 | ✅ YES | **82** |
| 3 | **code-review** | 8 | 8 | 7 | 7 | 7 | 9 | ✅ YES | **80** |
| 4 | **project-status** | 8 | 8 | 7 | 8 | 7 | 8 | ✅ YES | **79** |
| 5 | **requirement-analysis** | 8 | 8 | 7 | 7 | 7 | 8 | ✅ YES | **78** |
| 6 | **project-init** | 8 | 7 | 6 | 7 | 7 | 7 | ⚠️ ĐK¹ | **74** |
| 7 | **detail-design** | 8 | 7 | 7 | 7 | 7 | 7 | ✅ YES | **74** |
| 8 | **test-execution** | 7 | 7 | 7 | 7 | 7 | 7 | ✅ YES | **72** |
| 9 | **basic-design** | 8 | 7 | 6 | 7 | 7 | 7 | ⚠️ ĐK² | **71** |
| 10 | **change-request** | 8 | 7 | 6 | 7 | 7 | 7 | ✅ YES | **71** |
| 11 | **project-kickoff** | 8 | 7 | 6 | 7 | 7 | 7 | ✅ YES | **70** |
| 12 | **sprint-review** | 7 | 7 | 6 | 6 | 6 | 7 | ⚠️ ĐK³ | **67** |
| 13 | **estimate-template-fill** | 8 | 7 | 6 | 6 | 5 | 6 | ⚠️ ĐK⁴ | **66** |
| 14 | **prototype-ui** | 7 | 7 | 6 | 6 | 6 | 6 | ✅ YES | **65** |
| 15 | **estimate** | 7 | 5 | 5 | 6 | 7 | 7 | ❌ NO⁵ | **61** |
| 16 | **project-architecture** | 6 | 7 | 6 | 6 | 6 | 7 | ⚠️ ĐK⁶ | **61** |
| 17 | **db-design** | 7 | 5 | 6 | 5 | 6 | 7 | ❌ NO⁷ | **59** |
| 18 | **skill-doctor** | 8 | 7 | **3** | 7 | 6 | 7 | ❌ NO⁸ | **58** |
| 19 | **api-design** | 5 | 5 | 5 | 5 | 6 | 7 | ❌ NO⁹ | **55** |
| 20 | **test-plan** | 5 | 5 | 5 | 6 | 6 | 7 | ❌ NO¹⁰ | **54** |
| 21 | **menu** | 6 | 6 | 5 | 5 | 5 | 7 | ❌ NO¹¹ | **54** |
| 22 | **project-timeline** | 6 | 4 | 5 | 5 | 5 | 7 | ❌ NO¹² | **51** |
| 23 | **handover-doc** | 5 | 4 | 4 | 5 | 5 | 6 | ❌ NO¹³ | **47** |

¹ update_context chưa là script, không lock. ² Không có re-run mode cho docx. ³ Công thức partial=50% tùy hứng nhưng OK; phụ thuộc timeline output. ⁴ Regex-XML fragile + default 20≠22 + hardcode template Rikkei. ⁵ Khoảng tỷ lệ phi tất định trên con số ký hợp đồng. ⁶ Trùng logic status; self-check tốt cứu lại điểm. ⁷ Header "5 sheets"/6 sheet; DFS code trong prompt. ⁸ 44 false FAIL thực chứng + vòng lặp "chạy đến khi sạch" không thoát được. ⁹ 3 output/1 skill, re-run không thuật toán, 428 dòng. ¹⁰ Cột execution trong file plan → 2 nguồn sự thật với test-execution. ¹¹ Tuyên bố no-hardcode nhưng hardcode decision tree. ¹² "7 sheets"/8 sheet; nặng nhất về heuristic không kiểm chứng. ¹³ 250 dòng template dự án cụ thể; rủi ro leak giá trị mẫu vào tài liệu vận hành là rủi ro THẬT (chính skill thừa nhận "lệnh/URL sai còn nguy hiểm hơn thiếu").

---

## PHẦN III — BRUTAL REVIEW (mục 14)

Nếu đây là hồ sơ ứng tuyển Senior AI Engineer, những điều sau khiến tôi từ chối:

1. **Bạn không chạy công cụ của chính mình.** skill_doctor.py fail 44 lần trên môi trường thật ngay lần chạy đầu tiên của tôi. Nếu bạn có chạy nó ở đúng thư mục production, bạn đã thấy. "Linter cho skill" mà chưa được lint chính nó trên môi trường thật = demo, không phải tool.
2. **"Nguồn sự thật duy nhất" chứa dữ liệu sai** ("17 skill"). Một người kỹ lưỡng cấp senior không để hằng số lỗi thời trong file mình gọi là source of truth.
3. **Ba lỗi đếm sheet (7/8, 5/6, 6/N+6)** trong spec — loại lỗi mà chính bạn viết rule để bắt ("số cột lệch... đã từng lọt trong quá khứ") nhưng rule không cover. Bạn biết vấn đề tồn tại, viết linter, rồi không mở rộng rule cho chính lớp lỗi đó.
4. **Bạn viết văn xuôi mô tả code thay vì viết code** ở ít nhất 5 chỗ (update_context, DFS, gate check, postman/openapi gen, status engine) — trong khi đã chứng minh mình biết làm đúng (load_context.py, fill_dev_estimate.py). Tức là biết best practice nhưng không áp nhất quán — thiếu kỷ luật kỹ thuật, không thiếu kiến thức.
5. **Không có eval.** Bạn ghi "eval đầy đủ xem roadmap" — với 23 prompt × ~5.000 dòng và khách hàng thật ký vào file output, eval không phải roadmap item, nó là điều kiện tồn tại.
6. **Phi tất định ở chỗ đắt nhất:** estimate — thứ khách ký và bạn chịu trách nhiệm — cho kết quả khác nhau giữa hai lần chạy.
7. **Nói một đằng làm một nẻo trong cùng file:** excel-style cấm định nghĩa lại rồi 6 skill định nghĩa lại; menu tuyên bố no-hardcode rồi hardcode.

Những gì CỨU hồ sơ: tư duy hệ thống (context hub, I/O contract, gate, staleness, manifest-driven menu, linter-as-regression-test) là **thật và trên mức senior trung bình**. Vấn đề là execution chưa theo kịp tư duy.

---

## PHẦN IV — ROADMAP (mục 15)

**🔴 CRITICAL — sửa ngay (tổng ~1–2 ngày, impact: hệ thống từ "demo" → "dùng được")**
| Việc | Impact |
|---|---|
| C1. Sửa skill_doctor: allowlist = danh sách skill trong manifest; skill ngoài manifest → skip. | Linter dùng lại được; hết vòng lặp vô hạn. Impact: cực cao, 15 phút |
| C2. Sửa 3 lỗi đếm sheet + "17 skill" → thêm rule D11 (đếm "### Sheet N" so header) vào skill_doctor | Chặn vĩnh viễn lớp lỗi đã tái diễn 3 lần |
| C3. Bỏ cột 11–13 (Actual/Status/Bug) khỏi test-plan — kết quả CHỈ sống ở test-execution tracker | Xóa dual source of truth |
| C4. Thống nhất md_per_pm khi không có context: cả 2 skill BẮT BUỘC AskUserQuestion, không default | Hết lệch 10% giữa 2 file báo giá |
| C5. Tách `update_context.py` thành script thật (kèm flock) | Nhánh ghi context hết phụ thuộc trí nhớ LLM |

**🟠 HIGH (~1 tuần)**
| Việc | Impact |
|---|---|
| H1. `check_gate.py`: đếm P1 mở, bug Critical, quality gates → mọi gate gọi script | Gate từ advisory → enforced |
| H2. Quy tắc tất định cho estimate: "CRUD đơn giản → cận dưới; có integration/unknown → cận trên; ghi lý do vào cột Assumption" | Estimate lặp lại được |
| H3. Thuật toán re-run cho api-design: khóa = `METHOD + URL`; match → update cell khác biệt + changelog CHANGED; mất khỏi input → hỏi trước khi DEPRECATED | Re-run lặp lại được |
| H4. `compute_status.py` dùng chung cho project-status + project-architecture + staleness detail-design | 3 bản logic → 1 |
| H5. Eval tối thiểu: 1 dự án mẫu → chạy estimate + api-design + test-plan → assert số sheet/cột/công thức | Dám refactor |
| H6. Re-run mode cho basic-design/detail-design (docx): sinh `_v2`, không ghi đè + diff summary | Không mất chỉnh sửa của khách |

**🟡 MEDIUM (~2–3 tuần)**
- M1. Khử 5 khối redundancy (mục 8) — ~15–20% token.
- M2. Tách api-design: Postman/OpenAPI → `scripts/gen_postman.py`, `gen_openapi.py` đọc từ JSON trung gian.
- M3. `excel_builder.py` dùng chung (style tự áp) — giảm lỗi format về ~0.
- M4. handover-doc: chuyển 250 dòng template → `references/template-example.md`, SKILL.md còn ~80 dòng quy trình.
- M5. Định nghĩa `<skills_dir>`/`<workspace_folder>` chính thức trong pipeline.md (cách resolve trên từng môi trường).
- M6. Xóa `__pycache__`, thêm CHANGELOG.md thật, hợp nhất 3 hệ version.

**🟢 NICE TO HAVE**
- N1. Sinh decision-tree của menu từ manifest (thêm trường `intents[]` cho mỗi skill).
- N2. i18n policy per-deliverable. N3. activity_log rotation. N4. `/doc-sync` skill. N5. SQLite thay JSON context khi ≥2 agent.

---

## PHẦN V — REWRITE MẪU (mục 16)

**R1. skill_doctor.py — fix false positive (thay đoạn khởi tạo `skills`):**
```python
# CHỈ lint skill thuộc bộ (có trong manifest) — skill hệ thống/plugin ngoài bỏ qua
manifest_names = set(manifest.keys())
skills = {n: p for n, p in skills.items() if n in manifest_names}
# Chiều ngược lại (manifest có mà folder không) vẫn check như cũ.
# Skill MỚI chưa vào manifest: phát hiện bằng marker — folder có SKILL.md
# chứa chuỗi "pipeline.md" nhưng vắng trong manifest → FAIL D08 như cũ.
```

**R2. estimate — thay bảng "Tỷ lệ tham khảo" mở:**
> **Quy tắc chọn trong khoảng (BẮT BUỘC, để 2 lần chạy ra cùng kết quả):**
> - Task CRUD/lặp mẫu đã làm nhiều lần → lấy **cận dưới**.
> - Task có integration ngoài, chưa có sandbox, hoặc công nghệ team chưa dùng → lấy **cận trên**.
> - Còn lại → lấy **trung điểm, làm tròn 0.5 MD**.
> - Mọi lựa chọn ≠ trung điểm phải ghi lý do 1 câu vào cột Assumption của dòng đó.

**R3. "Không hỏi lại về những điểm nhỏ" (api-design/db-design/estimate) →**
> "Điểm có tác động ước tính **< 3 MD và không đổi kiến trúc** → tự quyết + ghi Assumptions. Điểm ≥ 3 MD hoặc đổi kiến trúc/integration → BẮT BUỘC hỏi (AskUserQuestion), không tự quyết."

**R4. Block "Bước -1" 12 dòng × 23 skill → 2 dòng:**
> ```
> > **Bước -1 (chuẩn chung):** `python3 <skills_dir>/project-init/scripts/load_context.py "<ws>"`
> > — giao thức đầy đủ (cget, NO_CONTEXT, field pre-fill): `project-init/references/context-protocol.md`. Field skill này dùng: `project.name`, `tech_stack.backend`, `integrations`.
> ```
(Chỉ dòng "Field skill này dùng" là khác nhau giữa các skill — đó mới là nội dung đặc thù.)

**R5. api-design re-run — thay "Chỉ sinh phần MỚI hoặc THAY ĐỔI":**
> 1. Khóa định danh endpoint = `METHOD + URL đã chuẩn hóa` (lowercase, `{param}` thống nhất).
> 2. Diff input mới vs file cũ: (a) khóa mới → thêm dòng, changelog NEW; (b) khóa trùng nhưng ≥1 trong 16 cột khác → update đúng cell đó, changelog CHANGED (+Breaking?=YES nếu đổi Input/Output/Status); (c) khóa có trong file cũ nhưng vắng trong input mới → **KHÔNG xóa, KHÔNG tự deprecated** — liệt kê và hỏi người dùng.
> 3. In bảng diff (thêm/sửa/nghi-xóa) TRƯỚC khi ghi file.

**R6. menu — thay tuyên bố sai:**
> "Bảng decision-tree dưới đây sinh từ trường `intents[]` trong skills-manifest.json — thêm skill mới: khai báo intents trong manifest, KHÔNG sửa file này." *(và thêm `intents[]` vào manifest — khi chưa làm được thì tối thiểu sửa câu 'KHÔNG có nội dung hardcode nào' thành 'bảng dưới là fallback tĩnh, ưu tiên manifest'.)*

---

## PHẦN VI — FINAL VERDICT (mục 17)

**Hệ thống này có chống đỡ được một AI assistant production không?**
Chưa. Nó chống đỡ tốt một **AI-assisted delivery workflow có con người trong vòng lặp** — và ở vai trò đó nó thuộc nhóm tốt. Nhưng "production AI OS" đòi hỏi: gate enforced bằng code, output tất định ở chỗ có chữ ký khách hàng, eval chặn regression, và tooling tự kiểm hoạt động trên môi trường thật. Cả 4 đang thiếu.

**Kỹ sư AI giàu kinh nghiệm có duyệt kiến trúc này không?**
Duyệt **topology** (hub context, I/O contract, progressive disclosure, linter-as-CI): có, và sẽ khen. Duyệt **implementation**: chưa — họ sẽ trả lại với đúng danh sách Critical ở mục 15.

**Mức trưởng thành: Advanced** — trên Intermediate rõ rệt (có kiến trúc, có ý thức eval/versioning/safety mà 90% bộ skill ngoài kia không có), dưới Production-ready vì khoảng cách prose→code và zero eval. Không phải Enterprise-grade.

**"Nếu đây là dự án của tôi, tôi redesign cái gì đầu tiên?" — thành thật:**
Không phải skill nào cả. Tôi dừng viết SKILL.md trong 1 tuần và làm 3 việc: **(1) sửa skill-doctor chạy sạch trên môi trường thật rồi treo nó thành pre-commit thực sự; (2) hạ 5 khối logic đang là văn xuôi xuống `scripts/lib/` (context write, gates, status, excel builder, api derivatives); (3) dựng 1 eval golden-path (1 dự án giả → 6 skill chính → assert cấu trúc).** Vì 23 skill của bạn đã đủ tốt để dùng — thứ chưa đủ tốt là nền móng để *tin* chúng và để *sửa* chúng mà không sợ. Viết thêm skill thứ 24 lúc này là xây thêm tầng trên móng chưa đổ xong.

---
*Mọi phát hiện trong báo cáo đều được đối chiếu trực tiếp với nội dung file ngày 08/07/2026; riêng lỗi skill-doctor được tái hiện bằng cách chạy script trên thư mục skills thật (44 FAIL / 1 WARN).*
