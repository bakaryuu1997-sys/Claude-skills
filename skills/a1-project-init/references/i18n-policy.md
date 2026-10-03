# I18N POLICY — ngôn ngữ deliverable (v3.5.0)

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

**Không có `settings.languages`** → khi tạo deliverable client-facing ĐẦU TIÊN: hỏi 1 lần
(AskUserQuestion: "Khách đọc tài liệu bằng tiếng gì? ja/vi/en") rồi ghi vào context bằng
`update_context.py set settings.languages.client_facing <giá trị>` — các lần sau KHÔNG hỏi lại.
Mặc định khi người dùng từ chối chọn: client_facing=vi, internal=vi, code=en.

## Bảng doc-type → ngôn ngữ

| Deliverable | Skill | Key |
|---|---|---|
| 見積書 / báo giá gửi khách, CR sign-off, Basic Design, Kickoff deck + Charter, UAT checklist, Handover | estimate, estimate-template-fill, change-request, basic-design, project-kickoff, test-plan (UAT), handover-doc | `client_facing` |
| Requirement analysis, QA tracker, Detail Design, Test plan/execution nội bộ, Sprint review, biên bản nội bộ, timeline | requirement-analysis, detail-design, test-plan, test-execution, sprint-review, meeting-minutes (nội bộ), project-timeline | `internal` |
| Code, unit test, PR description, commit, README repo, migration SQL comment | dev-implement, code-review | `code` |
| Biên bản họp VỚI KHÁCH | meeting-minutes | `client_facing` |

## Quy tắc

1. MỘT deliverable = MỘT ngôn ngữ chính. Ngoại lệ cho phép: thuật ngữ chuẩn ngành giữ nguyên
   (見積書, 基本設計, sprint, endpoint…), tên riêng, và bảng message đa ngôn ngữ (cột VN/EN/JP của basic-design).
2. Header/tiêu đề sheet Excel theo ngôn ngữ chính của file — không nửa Anh nửa Việt trong cùng bảng.
3. `client_facing = "ja"` → deliverable khách ký dùng đúng thuật ngữ 基本設計書/詳細設計書/見積明細書;
   ngày định dạng YYYY/MM/DD; xưng hô 御中 khi có tên công ty khách.
4. Mermaid/diagram label theo ngôn ngữ của tài liệu chứa nó.
5. Đổi ngôn ngữ giữa dự án = thay đổi lớn → cập nhật `settings.languages` + liệt kê tài liệu cần dịch lại
   (không âm thầm đổi từ tài liệu kế tiếp).
