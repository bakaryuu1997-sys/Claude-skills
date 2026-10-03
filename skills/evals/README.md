# EVALS — kiểm định bộ skill (v3.4.0)

Hai tầng. Chạy TẦNG 1 sau mỗi lần sửa script/skill (cùng skill_doctor). Tầng 2 chạy khi sửa prompt của một skill sinh file.

## Tầng 1 — Tự động (không cần LLM)

```bash
python3 <skills_dir>/evals/run_evals.py <skills_dir>
# Exit 0 = PASS hết. Kiểm: update_context (atomic/lock/validate), check_gate (3 kịch bản),
# compute_status (staleness), check_circular_fk, gen_postman + gen_openapi (golden spec),
# skill_doctor (0 FAIL), và tự kiểm checker check_xlsx.
```

## Tầng 2 — Golden cases (LLM-in-loop)

Mỗi case trong `golden/<skill>/` gồm `brief.md` (prompt input CHUẨN — chạy y nguyên)
và `expected_structure.json` (spec cấu trúc cho checker).

Quy trình khi sửa prompt một skill:
1. Mở `golden/<skill>/brief.md`, chạy skill với đúng prompt đó trong workspace sạch.
2. Chạy checker trên file sinh ra:
   `python3 evals/checkers/check_xlsx.py <output.xlsx> golden/<skill>/expected_structure.json`
3. Kiểm tay các mục "Kỳ vọng hành vi" trong brief (thường 3 mục — hỏi đúng chỗ, gate đúng, tất định).
4. PASS cả 3 bước → được commit thay đổi prompt. FAIL → prompt mới gây regression, sửa lại.

Case hiện có: `estimate/`, `test-plan/`, `api-design/`.

## Thêm case mới

1. Tạo `golden/<skill>/brief.md`: prompt input cố định + danh sách "Kỳ vọng hành vi" kiểm tay.
2. Tạo `expected_structure.json` theo format của `checkers/check_xlsx.py` (xem docstring).
3. Nguyên tắc: mỗi lần một lỗi output "lọt lưới" ra thực tế → thêm assertion bắt đúng lỗi đó
   (giống cơ chế mở rộng rule Dxx của skill-doctor — eval là regression test cho prompt).

## Checker có sẵn

- `checkers/check_xlsx.py` — sheet tồn tại, số cột tối thiểu, PHẢI có công thức (bắt hardcode tổng),
  chuỗi cấm (bắt leak giá trị mẫu FPT/F-Pay/Lorem), số dòng dữ liệu tối thiểu.
- Cần checker docx/html → thêm vào `checkers/` theo cùng pattern (exit 0/1 + liệt kê lỗi).
