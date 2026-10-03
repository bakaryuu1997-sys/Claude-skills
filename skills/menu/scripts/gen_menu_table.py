import json
from pathlib import Path
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
  sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
  sys.stderr.reconfigure(encoding="utf-8", errors="replace")

root = (
    Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
)
manifest_path = root / "a1-project-init" / "assets" / "skills-manifest.json"
if not manifest_path.exists():
  manifest_path = root / "project-init" / "assets" / "skills-manifest.json"

if not manifest_path.exists():
  print(f"❌ Không tìm thấy manifest tại: {manifest_path}")
  sys.exit(1)

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))


def step_key(entry):
  step = entry.get("step", "-")
  if step == "-":
    return (99, 99, "Z")
  prefix = step[0]
  num_part = re.sub(r"\D", "", step)
  num = int(num_part) if num_part else 0
  phase_order = {"A": 1, "B": 2, "C": 3, "D": 4, "X": 5}
  return (phase_order.get(prefix, 90), num, step)


sorted_skills = sorted(manifest.get("skills", []), key=step_key)

phase_names = {
    "A": "📦 GIAI ĐOẠN A — CHUẨN BỊ & THIẾT KẾ (A1 → A9)",
    "B": "🚀 GIAI ĐOẠN B — KHỞI ĐỘNG & ĐẶC TẢ CHI TIẾT (B0 → B3)",
    "C": "🔄 GIAI ĐOẠN C — VẬN HÀNH, PHÁT TRIỂN & KIỂM THỬ (C1 → C8)",
    "D": "🏁 GIAI ĐOẠN D — KẾT THÚC & BÀN GIAO (D1 → D3)",
    "X": "🛠️ GIAI ĐOẠN X — CROSS-CUTTING & KIẾN TRÚC (X1 → X7)",
    "-": "🧭 META — ĐIỀU HƯỚNG & KIỂM ĐỊNH (menu, x6-skill-doctor)",
}

current_prefix = None
for s in sorted_skills:
  step = s.get("step", "-")
  prefix = step[0] if step != "-" else "-"
  if prefix != current_prefix:
    current_prefix = prefix
    print(f"\n### {phase_names.get(prefix, prefix)}")
    print("| Bước | Lệnh | Tóm tắt | Đầu ra chính |")
    print("|---|---|---|---|")
  outs = ", ".join(s.get("outputs", [])) or "—"
  print(f"| **{step}** | `/{s['name']}` | {s.get('summary')} | {outs} |")

print(f"\nTổng: {len(sorted_skills)} skill trong hệ thống")
