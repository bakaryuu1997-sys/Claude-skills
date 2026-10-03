# Golden case /a6-estimate — input chuẩn (chạy y nguyên, không thêm thông tin)

Prompt: "Estimate dự án sau: App web đặt phòng họp nội bộ cho công ty ~500 nhân viên.
Chức năng: (1) đăng nhập SSO Google Workspace, (2) xem danh sách phòng + lịch trống theo ngày,
(3) đặt/hủy phòng theo khung 30 phút, (4) admin quản lý phòng (CRUD), (5) email nhắc trước 15 phút.
Tech: React + FastAPI + PostgreSQL. Team: 1 BE, 1 FE, 0.5 QA. KHÔNG có project-context.json."

Kỳ vọng hành vi (kiểm tay 3 điểm + chạy checker):
1. Skill PHẢI hỏi md_per_person_month qua AskUserQuestion (không có context) — trả lời "22".
2. Không có QA_Tracker → gate P1 báo "không kiểm được" (không chặn, không bịa).
3. Điểm trong khoảng tỷ lệ chọn theo quy tắc tất định (CRUD → cận dưới, email/SSO → cận trên, ghi Assumption).

Sau khi skill sinh file:
    python3 <skills_dir>/evals/checkers/check_xlsx.py <file_Estimate.xlsx> <skills_dir>/evals/golden/a6-estimate/expected_structure.json
