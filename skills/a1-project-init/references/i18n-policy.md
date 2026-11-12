# I18N POLICY — ngôn ngữ deliverable (v3.17.0)

> NGUỒN DUY NHẤT cho quyết định "tài liệu này viết tiếng gì". Mọi skill sinh file đọc bảng này,
> KHÔNG tự quyết theo cảm giác — output trộn ngôn ngữ tùy hứng là lỗi.

## Nguồn cấu hình: `settings.languages` trong project-context.json

```json
"settings": {
  "languages": {
    "client_facing": "ja",   // tài liệu khách đọc/ký (ja | vi | en)
    "internal": "vi",        // tài liệu nội bộ team
    "code": "en"             // code, comment, commit message, PR description
  }
}
```

### Một lựa chọn ngôn ngữ duy nhất lúc khởi tạo (chế độ mặc định)

Ở bước khởi tạo dự án hỏi **một câu**: "Ngôn ngữ tài liệu của dự án: ja / vi / en?". Đáp án được ghi vào CẢ HAI khóa
`client_facing` và `internal` (code luôn `en`): **toàn bộ tiến trình sinh tài liệu theo đúng ngôn ngữ đó**, từ yêu cầu,
thiết kế, test, review, báo cáo tới bàn giao. Chỉ tách `internal` khác `client_facing` khi người dùng nói rõ muốn tách
(ví dụ khách đọc tiếng Nhật nhưng team nội bộ làm việc bằng tiếng Việt).

```
python <skills_dir>/a1-project-init/scripts/update_context.py <ws> set settings.languages.client_facing ja
python <skills_dir>/a1-project-init/scripts/update_context.py <ws> set settings.languages.internal ja
python <skills_dir>/a1-project-init/scripts/update_context.py <ws> set settings.languages.code en
```

**Thiếu `settings.languages`** → hỏi 1 lần như trên rồi ghi; các lần sau KHÔNG hỏi lại. Thiếu riêng `internal` → dùng
giá trị của `client_facing`. Người dùng từ chối chọn: client_facing = internal = vi, code = en.

### Cách script và tài liệu bám theo cấu hình
- MỌI script có chữ chảy vào tài liệu giao đều theo ngôn ngữ đã chọn (`--context <project-context.json>` hoặc `--lang ja|vi|en`;
  thiếu cả hai → `vi` như trước). Mã máy đọc (QUALIFIED, GO/NO-GO, PASS/FAIL, Critical/High…) không dịch. Gồm:
  báo cáo số liệu (`test_metrics`, `sprint_metrics`, `cr_impact`, `smoke_test_runner`, `timeline_calc`, `check_gate`),
  bằng chứng kiểm tra (`health_check`, `check_circular_fk`, `check_crud_coverage`, `verify_fe_scaffold`, `coverage_summary`, `parse_npm_audit`),
  bộ dựng/sinh tài liệu (`xlsx_build` — nhãn tổng + thông báo validate theo `spec.language`; `build_deck` — nhãn Nguồn; `gen_openapi`, `gen_postman`; `gen_architecture_html`).
- Placeholder chưa điền theo ngôn ngữ: vi `[CẦN ĐIỀN]` · ja `[要記入]` · en `[TO BE FILLED]` (`i18n.placeholder()`); `xlsx_verify` coi cả ba là chưa điền.
- Công cụ chẩn đoán cho agent/dev (`update_context`, `validate_context`, `xlsx_verify`, `lang_check`, `load_context`, `menu`…) in thông báo kỹ thuật,
  KHÔNG phải nội dung tài liệu: không bắt buộc theo ngôn ngữ dự án. Câu trả lời trong chat theo ngôn ngữ người dùng đang dùng.
- Linter x6 rule D18: skill có `outputs[]` mà SKILL.md không dẫn chiếu file này → FAIL.
- Trước khi giao tài liệu, quét rò rỉ ngôn ngữ: `python <skills_dir>/a1-project-init/scripts/lang_check.py --ws <ws>`
  (bắt tiếng Việt lọt vào tài liệu `ja`/`en`, kana lọt vào tài liệu `vi`; exit 1 khi có rò rỉ).

## Bảng doc-type → ngôn ngữ

| Deliverable | Skill | Key |
|---|---|---|
| 見積書 / báo giá gửi khách, Proposal & SOW, Prototype, CR sign-off, Basic Design, Kickoff deck + Charter, UAT checklist, Release Plan (bản gửi khách), Handover, UAT Acceptance, User Manual / Admin Guide, slide gửi khách | estimate, estimate-template-fill, proposal-sow, prototype-ui, change-request, basic-design, project-kickoff, test-plan (UAT), release-deployment, handover-doc, uat-acceptance, user-guide-manual, presentation-deck | `client_facing` |
| Requirement analysis, QA tracker, API/DB design, Detail Design, Test plan/execution nội bộ, Code review report, Security audit report, Sprint review, biên bản nội bộ, timeline, Architecture survey, ENGINEERING_STANDARDS | requirement-analysis, api-design, db-design, detail-design, test-plan, test-execution, code-review, trailofbits-security-skills, sprint-review, meeting-minutes (nội bộ), project-timeline, acquire-codebase-knowledge, coding-standards | `internal` |
| Code, unit test, API test suite, PR description, commit, README repo, migration SQL comment, comment/label trong UI code | dev-implement, frontend-dev, api-test-suite-generator | `code` |
| Biên bản họp VỚI KHÁCH | meeting-minutes | `client_facing` |

## Font theo ngôn ngữ (docx / pptx / xlsx) — BẮT BUỘC đặt rõ, không dựa font mặc định

| Ngôn ngữ chính của file | Font | Cách đặt |
|---|---|---|
| `ja` | **Yu Gothic** (dự phòng Meiryo) | docx: đặt `w:rFonts` cả `ascii`, `hAnsi`, `eastAsia`; pptx: `a:latin` + `a:ea` + `a:cs`; openpyxl: `Font(name="Yu Gothic")` |
| `vi` | Arial (hoặc Calibri) | font có đủ dấu tiếng Việt, không dùng font chỉ có Latin cơ bản |
| `en` | Arial | — |

python-docx/python-pptx mặc định Calibri và KHÔNG đặt `eastAsia` → chữ Nhật rơi về font thay thế tùy máy, lệch layout. File lẫn Nhật + Việt dùng Yu Gothic cho cả hai (có glyph Latin mở rộng) và kiểm tra lại dấu sau khi render.

## Quy tắc

1. MỘT deliverable = MỘT ngôn ngữ chính. Ngoại lệ cho phép: thuật ngữ chuẩn ngành giữ nguyên
   (見積書, 基本設計, sprint, endpoint…), tên riêng, và bảng message đa ngôn ngữ (cột VN/EN/JP của basic-design).
2. Header/tiêu đề sheet Excel theo ngôn ngữ chính của file — không nửa Anh nửa Việt trong cùng bảng.
3. `client_facing = "ja"` → deliverable khách ký dùng đúng thuật ngữ 基本設計書/詳細設計書/見積明細書;
   ngày định dạng YYYY/MM/DD; xưng hô 御中 khi có tên công ty khách.
4. Mermaid/diagram label theo ngôn ngữ của tài liệu chứa nó.
5. Đổi ngôn ngữ giữa dự án = thay đổi lớn → cập nhật `settings.languages` + liệt kê tài liệu cần dịch lại
   (không âm thầm đổi từ tài liệu kế tiếp).
6. **Zero Language Leakage từ template**: Mọi template mẫu (Excel, Word, Slide) trước khi render phải được rà soát sạch 100%. Nếu tài liệu là tiếng Nhật (`client_facing = ja`), tuyệt đối không để sót tiếng Việt hay ghi chú cũ từ template trong bất kỳ trang hay sheet nào.
7. **Anti-Vendor-Branding Leak**: Tuyệt đối cấm để tên các nhà thầu cũ (Rikkei, Rikkeisoft, FPT, v.v.) lọt vào deliverable. Phải dùng tên tổ chức được chỉ định trong `project-context.json` hoặc tên trung tính `システム開発チーム`.
