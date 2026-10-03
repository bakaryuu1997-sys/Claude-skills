# Golden case /a4-api-design — input chuẩn

Prompt: "Thiết kế API cho app đặt phòng họp nội bộ: SSO Google login, xem phòng + lịch trống,
đặt/hủy booking khung 30 phút, admin CRUD phòng. KHÔNG có project-context.json."

Kỳ vọng hành vi:
1. Sinh `*_api_spec.json` TRƯỚC, rồi gọi gen_postman.py + gen_openapi.py (không viết 2 file đó tay).
2. Cả 2 script phải in ✅ verified.
3. Excel 16 cột/module sheet, sheet Changelog có dòng v1.0 Initial release.

Checker (Excel):
    python3 <skills_dir>/evals/checkers/check_xlsx.py <file_API_Design.xlsx> <skills_dir>/evals/golden/a4-api-design/expected_structure.json
(Postman/OpenAPI đã được run_evals.py kiểm TỰ ĐỘNG từ api_spec.json mẫu trong folder này.)
