#!/usr/bin/env python3
"""
patch_archify_legibility.py — Tiện ích tăng cường độ sắc nét và kích thước chữ cho sơ đồ Archify.
Khắc phục triệt để lỗi chữ tí hon (8px) trong Semantic Passport (#focus-chip) và đồng bộ Theme.
"""
import sys
import re
from pathlib import Path

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

def patch_file(target_path: Path) -> bool:
    if not target_path.exists():
        print(f"[-] Không tìm thấy file: {target_path}")
        return False
    try:
        content = target_path.read_text(encoding="utf-8")
        if "custom-legibility-enhancement" in content:
            # Thay thế block CSS hiện tại bằng bản mới nhất
            updated = re.sub(
                r'<!-- CUSTOM LEGIBILITY.*?<\/style>',
                CUSTOM_LEGIBILITY_CSS.strip(),
                content,
                flags=re.DOTALL
            )
        elif "</head>" in content:
            updated = content.replace("</head>", f"{CUSTOM_LEGIBILITY_CSS}\n</head>")
        else:
            updated = f"{CUSTOM_LEGIBILITY_CSS}\n{content}"

        target_path.write_text(updated, encoding="utf-8")
        print(f"[+] Đã vá thành công CSS tăng kích thước chữ và tương phản cho: {target_path}")
        return True
    except Exception as e:
        print(f"[!] Lỗi khi xử lý {target_path}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Cách dùng: python patch_archify_legibility.py <file_or_dir_path>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if input_path.is_file():
        success = patch_file(input_path)
        sys.exit(0 if success else 1)
    elif input_path.is_dir():
        html_files = list(input_path.glob("*.html"))
        arch_files = [f for f in html_files if "architecture" in f.name or "sequence" in f.name]
        targets = arch_files if arch_files else html_files
        count = 0
        for f in targets:
            if patch_file(f):
                count += 1
        print(f"[i] Đã hoàn tất vá {count} file HTML trong thư mục {input_path}")
        sys.exit(0)
    else:
        print(f"[-] Đường dẫn không hợp lệ: {input_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()
