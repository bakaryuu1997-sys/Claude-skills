# Security Audit Report — <Project> — <PR/commit/phạm vi> — <YYYY-MM-DD>

> Lưu: `docs/C4_trailofbits-security-skills/Security_Audit_Report_PR<id>.md` (audit toàn hệ thống: `Security_Audit_Report_Full_<YYYYMMDD>.md`). Mỗi lần audit một file — không ghi đè.

## 1. Phạm vi & phương pháp
- Phạm vi: commit/PR, module, route đã rà. Ngoài phạm vi: …
- Phương pháp: đọc mã tĩnh theo 10 vector; công cụ đã chạy (ghi lệnh + phiên bản): `npm audit`/`pip-audit`, `semgrep`, `gitleaks`… Không chạy được → ghi rõ lý do.
- Kiểm thử động (PoC request) có thực hiện không: Có/Không (môi trường nào).

## 2. Tóm tắt
| Critical | High | Medium | Low |
|---|---|---|---|
| n | n | n | n |

Kết luận phát hành: **CHẶN** nếu còn Critical/High chưa xử lý · cho phép với điều kiện … · cho phép.

## 3. Findings
| ID | Severity | Vector | CWE/OWASP | Vị trí (file:dòng) | Mô tả & tác động | Bằng chứng / PoC | Khuyến nghị | Owner | Hạn | Trạng thái |
|---|---|---|---|---|---|---|---|---|---|---|
| BUG-NNN | Critical/High/Medium/Low | V1…V10 | CWE-639 / API1:2023 | `src/…:42` | … | request/log/mã đoạn | cách sửa cụ thể | [CẦN ĐIỀN] | [CẦN ĐIỀN] | open |

(ID `BUG-<NNN>` theo `pipeline.md` §3; Critical/High đồng thời ghi vào `known_issues[]`.)

## 4. Bảng triage dependency (từ `scripts/parse_npm_audit.py`)
Dán bảng; mỗi dòng Critical/High điền cột Reachability (Unreachable / Mitigated / Action Required) kèm lý do đã đọc mã.

## 5. Bằng chứng test auth/IDOR
Liên kết test (vd `tests/api/auth_api.test.ts`, Test ID) chứng minh phân quyền đã được kiểm.

## 6. Điểm tốt đã xác nhận
(Tối đa 5, có file:dòng.)

## 7. Việc còn lại / Giới hạn của lần audit này
