# Đầu vào của `scripts/sprint_metrics.py` và cách lấy dữ liệu

| Trường | Lấy từ | Ghi chú |
|---|---|---|
| `sprint`, `sprint_weeks` | `project.current_sprint`, `settings.sprint_duration_weeks` | Không hardcode 2 tuần nếu context khác |
| `tasks[]` | Sheet "Sprint Plan" của `*_Project_Timeline.xlsx` (A9) + xác nhận của người dùng về trạng thái thực tế | `planned_md` từ A9; `actual_md` là thực tế; `status` ∈ done / partial / not_started / moved |
| `capacity_md` | `estimates.team_capacity_per_sprint` (hoặc Σ `team[].md_per_sprint`) | Dùng cho drag coefficient |
| `bugs` | Defects của /c5-test-execution (`known_issues[]`) và bug phát sinh trong sprint | `p1_open` = bug Critical/High đang mở; ánh xạ P1→Critical, P2→High theo `pipeline.md` §1 |
| `demo` | Người dùng cho biết: ok / partial / no | Không suy đoán |
| `blockers_unresolved` | Người dùng | Số blocker chưa giải quyết tại thời điểm chốt sprint |
| `prev_actions` | Action items retro sprint trước (Sprint_Log, Sheet Action Items) | `total`, `done` |
| `unresolved_debt_md` | Enabler/tech-debt task chưa xong (từ retro 🔴 High) | |
| `remaining_md` | Tổng MD còn lại của scope (A9 trừ completed_md tích lũy) | 0 = sprint cuối |
| `team_daily_burn_md` | Team capacity MD/ngày (capacity_md ÷ số ngày làm việc sprint) | Chỉ để tính delay |
| `history[]` | Sprint_Log (các sprint trước): `sprint, planned_md, completed_md, completion_pct, health` | Lấy 2 sprint gần nhất để đánh giá ESCALATE/UNDER-COMMIT |

Sau khi chạy: đưa `history_entry` vào Sprint_Log (append), cập nhật `project.current_sprint` bằng:
`python <skills_dir>/a1-project-init/scripts/update_context.py <ws> set project.current_sprint <N+1>` — chỉ khi giá trị hiện tại vẫn là N (đọc bằng `load_context.py` trước; tránh nhảy sprint khi chạy lại).
