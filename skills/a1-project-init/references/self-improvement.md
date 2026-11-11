# SELF-IMPROVEMENT LOOP — NGUỒN DUY NHẤT (v3.17.0)

> Mọi skill kết thúc bằng một khối ngắn (≤ 8 dòng) trỏ về file này. KHÔNG chép lại quy trình vào từng SKILL.md.
> Mục tiêu: skill tự học từ thực tế dùng, nhưng mọi thay đổi đều NHỎ, CÓ KIỂM TRA, CÓ THỂ HOÀN TÁC.

## 1. Cuối MỖI tác vụ — trả lời 3 câu (trong đầu, không in nếu không có gì)

1. Có lỗi, workaround hoặc bước phải làm thủ công vì skill thiếu/sai hướng dẫn không?
2. Người dùng có đính chính hoặc từ chối điều skill vừa làm không?
3. Có quy tắc/ví dụ mới nào giúp LẦN SAU làm đúng ngay từ đầu không?

Cả ba đều "không" → **im lặng**, kết thúc. Không in thêm gì, không đề xuất cho có.

## 2. Phân loại: chỉ phát hiện HỆ THỐNG mới được đề xuất

| Đủ điều kiện | KHÔNG đủ điều kiện |
|---|---|
| Lỗi/thiếu sót sẽ lặp lại với dự án khác (thiếu bước, sai tên file, sai công thức, trigger sai) | Sở thích riêng của một người/một dự án (màu, tên, giọng văn) |
| Người dùng đính chính một quy tắc chung | Yêu cầu đặc thù một khách hàng |
| Ví dụ/checklist còn thiếu mà nhiều dự án cần | Dữ liệu dự án, tên khách, email, token, đường dẫn cá nhân (**cấm tuyệt đối**) |

Phát hiện đặc thù dự án → ghi vào `project-context.json` (`known_issues[]`/ghi chú) hoặc bỏ, **không** đưa vào skill.

## 3. Đề xuất — in tối đa 3 dòng

```
💡 Đề xuất cải thiện <skill>: <thiếu sót hệ thống, 1 dòng>
   Sửa: <thêm/làm rõ gì, ở mục nào>   ·   Tác động: <lần sau tránh được gì>
```

## 4. Áp dụng — chỉ khi đủ 5 điều kiện

1. Có repo nguồn: biến `SKILLS_REPO` trỏ tới bản clone `Claude-skills` (mặc định: thư mục gốc chứa `scripts/skill_self_update.py`), đang ở nhánh `main`. **Không có repo** (vd chạy từ plugin cache trên máy khác) → chỉ in đề xuất, KHÔNG tự sửa. Không bao giờ sửa trong `~/.claude/plugins/cache/...`.
2. **Tối đa 1 lần tự sửa mỗi tác vụ của người dùng, và chỉ sửa 1 skill.**
3. Diff **≤ 40 dòng thêm, ≤ 5 dòng xóa**; chỉ THÊM hoặc LÀM RÕ — không xóa/đảo ngược quy tắc sẵn có; file mới chỉ là `references/*.md` (≤ 2). Muốn thay đổi lớn hơn → đưa thành đề xuất cho người dùng duyệt thủ công.
4. Nội dung sửa không chứa email, API key/token, đường dẫn cá nhân (ví dụ `C:\Users\…`, `/home/…`), tên khách hay dữ liệu dự án.
5. Không đổi hành vi mặc định của pipeline, không đổi tên skill/trigger.

Cách làm:

```bash
# 1) Sửa file trong "$SKILLS_REPO/skills/<skill>/" (Edit) — KHÔNG đụng version/manifest/CHANGELOG
# 2) Chạy script (task-id: mã duy nhất của tác vụ hiện tại, vd 20261106-1432)
python "$SKILLS_REPO/scripts/skill_self_update.py" --skill <skill> --task-id <mã> \
       --summary "<một câu ≤120 ký tự>" [--type changed|added|fixed]
```

Script tự: từ chối nếu repo/nhánh sai · chỉ cho phép thay đổi trong `skills/<skill>/` · kiểm giới hạn diff · quét dữ liệu nhạy cảm · chạy `skill_doctor.py` (FAIL → hoàn tác, lưu bản vá bị từ chối ở thư mục temp) · bump patch version của skill + manifest + 4 file plugin + `manifest_version` · thêm dòng CHANGELOG (Keep a Changelog) · `git add` đúng đường dẫn (cấm `-A`) · commit Conventional Commits · `git pull --rebase` · `git push origin main` (cấm force). Rebase/push lỗi → giữ commit ở local và báo lý do.

Mã thoát: `0` xong · `2` từ chối (chưa đổi gì) · `3` doctor FAIL (đã hoàn tác) · `4` rebase lỗi · `5` push lỗi.

## 5. Sau khi push — luôn báo người dùng (4 dòng)

`skill` · đổi gì · commit hash · lệnh hoàn tác `git revert <hash>`. Nếu exit ≠ 0 báo đúng lý do script in ra; KHÔNG thử lách (không `--force`, không bỏ qua rào, không sửa thêm lần thứ hai).

## 6. Khối chuẩn ở cuối mỗi SKILL.md (đúng 1 lần, ≤ 8 dòng — rule D13)

```markdown
## Self-Improvement Loop
Cuối tác vụ trả lời 3 câu (lỗi/workaround? người dùng đính chính? quy tắc mới cho lần sau?). Không có gì → im lặng.
Có phát hiện HỆ THỐNG → in `💡 Đề xuất cải thiện` (≤ 3 dòng) rồi áp dụng theo quy trình duy nhất:
`a1-project-init/references/self-improvement.md` (1 skill/tác vụ, ≤ 40 dòng thêm, không xóa quy tắc,
chạy `scripts/skill_self_update.py`, báo skill · thay đổi · commit hash · `git revert <hash>`).
```
