#!/usr/bin/env python3
"""
patch_archify_legibility.py — Tiện ích tăng cường độ sắc nét và kích thước chữ cho sơ đồ Archify.
Khắc phục triệt để lỗi chữ tí hon (8px) trong Semantic Passport (#focus-chip) và đồng bộ Theme.
"""
import sys
import re
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

# Dấu hiệu nhận diện file do Archify sinh ra. Không có dấu hiệu nào → KHÔNG vá (tránh làm hỏng file khác).
ARCHIFY_MARKERS = ("focus-chip", "relationship-lens", "archify-source-evidence-data", "semantic-passport")

CUSTOM_LEGIBILITY_CSS = """
  <!-- CUSTOM LEGIBILITY & CONTRAST ENHANCEMENT OVERRIDE -->
  <style id="custom-legibility-enhancement">
    /* 1. EXPAND FOCUS CHIP & SEMANTIC PASSPORT WINDOW */
    #focus-chip,
    .focus-chip,
    .relationship-lens {
      width: 480px !important;
      max-width: 95vw !important;
      font-size: 0.95rem !important;
      box-shadow: 0 16px 48px rgba(0,0,0,0.45) !important;
      border: 1.5px solid var(--frontend-stroke) !important;
      border-radius: 12px !important;
      backdrop-filter: blur(20px) !important;
      background: var(--toolbar-menu-bg) !important;
      z-index: 99 !important;
    }

    /* 2. HEADER & TITLES */
    .relationship-lens-head {
      padding: 1.1rem 1.1rem 0.85rem !important;
    }
    .relationship-lens-eyebrow {
      font-size: 0.75rem !important;
      font-weight: 800 !important;
      letter-spacing: 0.1em !important;
      margin-bottom: 0.3rem !important;
      opacity: 0.9 !important;
    }
    .relationship-lens-title,
    #relationship-lens-title {
      font-size: 1.35rem !important;
      font-weight: 800 !important;
      line-height: 1.3 !important;
      color: var(--text) !important;
    }
    .semantic-passport-detail,
    #focus-detail {
      font-size: 0.92rem !important;
      line-height: 1.5 !important;
      color: var(--text-muted) !important;
      margin-top: 0.35rem !important;
      white-space: normal !important;
    }

    /* 3. METADATA TAGS & CHIPS */
    .semantic-passport-meta {
      gap: 0.45rem !important;
      margin-top: 0.65rem !important;
    }
    .semantic-passport-meta span,
    .semantic-passport-meta code {
      font-size: 0.8rem !important;
      padding: 0.25rem 0.65rem !important;
      font-weight: 700 !important;
      border-radius: 6px !important;
      line-height: 1.4 !important;
    }

    /* 4. VERIFIED SOURCE EVIDENCE CONTAINER */
    .semantic-passport-evidence,
    #focus-evidence {
      margin-top: 0.9rem !important;
      padding: 1rem !important;
      border-radius: 10px !important;
      border: 1px solid color-mix(in srgb, var(--backend-stroke) 40%, var(--toolbar-border)) !important;
      background: color-mix(in srgb, var(--backend-fill) 25%, var(--panel)) !important;
    }
    .semantic-passport-evidence-head {
      margin-bottom: 0.75rem !important;
      gap: 0.75rem !important;
    }
    .semantic-passport-evidence-status {
      font-size: 0.82rem !important;
      font-weight: 800 !important;
      letter-spacing: 0.06em !important;
      text-transform: uppercase !important;
    }
    .semantic-passport-repository,
    #focus-repository {
      font-size: 0.82rem !important;
      font-weight: 700 !important;
      color: var(--frontend-stroke) !important;
    }

    /* 5. CODE FILE SOURCE CITATION BOX (CRITICAL FOR READABILITY) */
    .semantic-passport-evidence-links {
      display: grid !important;
      gap: 0.65rem !important;
    }
    .semantic-passport-source {
      display: flex !important;
      flex-direction: column !important;
      align-items: flex-start !important;
      padding: 0.85rem 1rem !important;
      border-radius: 8px !important;
      gap: 0.35rem !important;
      background: color-mix(in srgb, var(--panel) 85%, transparent) !important;
      border: 1px solid color-mix(in srgb, var(--backend-stroke) 35%, transparent) !important;
      box-shadow: 0 2px 8px rgba(0,0,0,0.12) !important;
      text-decoration: none !important;
    }
    /* Component description label (e.g. WebSocket broadcast server) */
    .semantic-passport-source strong {
      font-size: 1.05rem !important;
      font-weight: 800 !important;
      line-height: 1.35 !important;
      color: var(--text) !important;
      white-space: normal !important;
      overflow: visible !important;
    }
    /* Line number badge (e.g. Line 1 - 150) */
    .semantic-passport-source code {
      display: inline-block !important;
      font-size: 0.9rem !important;
      font-weight: 800 !important;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
      padding: 0.2rem 0.55rem !important;
      border-radius: 4px !important;
      background: color-mix(in srgb, var(--backend-stroke) 22%, transparent) !important;
      color: var(--backend-stroke) !important;
      letter-spacing: 0.04em !important;
      border: 1px solid color-mix(in srgb, var(--backend-stroke) 35%, transparent) !important;
    }
    /* File Path (e.g. src/websocket/server.ts) */
    .semantic-passport-source small {
      display: block !important;
      font-size: 0.95rem !important;
      font-weight: 700 !important;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
      line-height: 1.4 !important;
      color: var(--frontend-stroke) !important;
      white-space: normal !important;
      word-break: break-all !important;
      overflow: visible !important;
      margin-top: 0.25rem !important;
      opacity: 1 !important;
    }

    /* 6. REACHABILITY & RELATIONSHIPS LIST */
    .semantic-passport-reach {
      margin-top: 0.85rem !important;
      gap: 0.45rem !important;
    }
    .semantic-passport-reach-label {
      font-size: 0.78rem !important;
      font-weight: 800 !important;
      letter-spacing: 0.08em !important;
    }
    .semantic-passport-reach-actions button {
      min-height: 2.2rem !important;
      font-size: 0.82rem !important;
      padding: 0.35rem 0.7rem !important;
    }
    .relationship-lens-summary,
    #focus-summary {
      font-size: 0.82rem !important;
      margin-top: 0.45rem !important;
      color: var(--text-muted) !important;
    }
    .relationship-lens-group-label {
      font-size: 0.78rem !important;
      font-weight: 800 !important;
      letter-spacing: 0.08em !important;
    }
    .relationship-lens-item {
      font-size: 0.85rem !important;
      padding: 0.4rem 0.55rem !important;
    }
  </style>
"""

def is_archify_file(content: str) -> bool:
    return any(m in content for m in ARCHIFY_MARKERS)


def patch_file(target_path: Path) -> bool:
    if not target_path.exists():
        print(f"[-] Không tìm thấy file: {target_path}")
        return False
    try:
        content = target_path.read_text(encoding="utf-8")
        if not is_archify_file(content):
            print(f"[-] Bỏ qua (không phải sơ đồ Archify — thiếu marker {ARCHIFY_MARKERS[0]}…): {target_path.name}")
            return False
        if "custom-legibility-enhancement" in content:
            updated = re.sub(
                r'\s*<!-- CUSTOM LEGIBILITY.*?</style>',
                "\n" + CUSTOM_LEGIBILITY_CSS.strip(),
                content,
                flags=re.DOTALL,
            )
        elif "</head>" in content:
            updated = content.replace("</head>", f"{CUSTOM_LEGIBILITY_CSS}\n</head>", 1)
        else:
            print(f"[-] Không có </head> trong {target_path.name} — không vá để tránh cấu trúc HTML hỏng")
            return False
        tmp = target_path.with_suffix(target_path.suffix + ".tmp")
        tmp.write_text(updated, encoding="utf-8", newline="\n")
        tmp.replace(target_path)
        print(f"[+] Đã vá CSS tăng kích thước chữ và tương phản: {target_path.name}")
        return True
    except (OSError, UnicodeError) as e:
        print(f"[!] Lỗi khi xử lý {target_path.name}: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Cách dùng: python patch_archify_legibility.py <file_or_dir_path>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if input_path.is_file():
        sys.exit(0 if patch_file(input_path) else 1)
    if input_path.is_dir():
        # Chỉ vá file có marker Archify. KHÔNG fallback sang "mọi .html" (dễ làm hỏng trang Compass).
        targets = [f for f in sorted(input_path.glob("*.html")) if is_archify_file(f.read_text(encoding="utf-8", errors="replace"))]
        if not targets:
            print(f"[i] Không có file sơ đồ Archify trong {input_path} (không có gì để vá)")
            sys.exit(0)
        count = sum(1 for f in targets if patch_file(f))
        print(f"[i] Đã vá {count}/{len(targets)} file Archify trong {input_path}")
        sys.exit(0 if count == len(targets) else 1)
    print(f"[-] Đường dẫn không hợp lệ: {input_path}")
    sys.exit(1)


if __name__ == "__main__":
    main()
