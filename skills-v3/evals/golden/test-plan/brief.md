# Golden case /test-plan — input chuẩn

Prompt: "Tạo test plan cho app đặt phòng họp (spec: dùng api_spec.json trong evals/golden/api-design/).
Module: Auth, Rooms. KHÔNG có project-context.json."

Kỳ vọng hành vi:
1. File plan 14 cột — TUYỆT ĐỐI không có cột Actual Result / Status / Bug Ticket ID.
2. Mỗi endpoint ≥ 7 case (happy/auth/permission/invalid/notfound/edge/concurrent).
3. Traceability Matrix tự sinh, requirement 0 test → đỏ.

Checker:
    python3 <skills_dir>/evals/checkers/check_xlsx.py <file_Test_Plan.xlsx> <skills_dir>/evals/golden/test-plan/expected_structure.json
