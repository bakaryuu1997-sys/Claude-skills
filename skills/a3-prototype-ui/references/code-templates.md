# Prototype UI — JS điều hướng/feedback + CSS templates + header comment

> File tham chiếu của skill /a3-prototype-ui — SKILL.md trỏ tới đây (progressive disclosure). ĐỌC TOÀN BỘ file này khi thực thi skill.

## JavaScript cho Prototype Chrome nâng cấp

```javascript
// ── Screen navigation với prev/next + keyboard ───────────────────
const SCREENS = [/* điền id theo thứ tự */];
let currentIndex = 0;

function go(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('screen-' + id)?.classList.add('active');
  currentIndex = SCREENS.indexOf(id);
  document.getElementById('screen-counter').textContent =
    `${currentIndex + 1}/${SCREENS.length}`;
  document.querySelectorAll('.nav-item').forEach(n => n.classList.toggle('active', n.dataset.screen === id));
  renderFeedback(id); // cập nhật feedback panel khi đổi screen
}
function prevScreen() { if (currentIndex > 0) go(SCREENS[--currentIndex]); }
function nextScreen() { if (currentIndex < SCREENS.length - 1) go(SCREENS[++currentIndex]); }
document.addEventListener('keydown', e => {
  if (e.key === 'ArrowLeft') prevScreen();
  if (e.key === 'ArrowRight') nextScreen();
});

// ── Device toggle (Mobile / Desktop / Admin) ─────────────────────
function setDevice(type) {
  document.getElementById('device-area').className = 'device-' + type;
  document.querySelectorAll('.device-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('btn-' + type)?.classList.add('active');
}

// ── Feedback / Annotation system ─────────────────────────────────
const feedbackStore = {}; // { screenId: [{note, time}] }

function getCurrentScreenId() {
  return SCREENS[currentIndex];
}
function addFeedback() {
  const id = getCurrentScreenId();
  const input = document.getElementById('feedback-input');
  const text = input.value.trim();
  if (!text) return;
  if (!feedbackStore[id]) feedbackStore[id] = [];
  feedbackStore[id].push({ note: text, time: new Date().toLocaleTimeString('vi-VN') });
  input.value = '';
  renderFeedback(id);
}
function renderFeedback(id) {
  const list = document.getElementById('feedback-list');
  const notes = feedbackStore[id] || [];
  list.innerHTML = notes.map((n, i) =>
    `<div style="display:flex;gap:8px;margin-bottom:8px;">
       <span style="background:#1F4E79;color:#fff;border-radius:50%;width:20px;height:20px;
             display:flex;align-items:center;justify-content:center;font-size:11px;flex-shrink:0;">
         ${i+1}</span>
       <div><div style="font-size:13px;">${n.note}</div>
       <div style="font-size:11px;color:#aaa;">${n.time}</div></div>
     </div>`
  ).join('') || '<div style="color:#aaa;font-size:12px;">Chưa có ghi chú cho màn hình này</div>';
}
function exportFeedback() {
  let out = '=== PROTOTYPE FEEDBACK — [Tên dự án] ===\n\n';
  SCREENS.forEach(sid => {
    const notes = feedbackStore[sid] || [];
    if (notes.length) {
      out += `📱 Màn hình: ${sid}\n`;
      notes.forEach((n, i) => out += `  ${i+1}. ${n.note}\n`);
      out += '\n';
    }
  });
  if (!Object.values(feedbackStore).some(a => a.length))
    out += '(Chưa có feedback)\n';
  navigator.clipboard.writeText(out)
    .then(() => alert('✅ Đã copy toàn bộ feedback vào clipboard!\nPaste vào email/chat để gửi cho team.'))
    .catch(() => { document.getElementById('export-out').value = out; });
}
```

**HTML cho Feedback Panel (đặt bên phải device frame):**
```html
<div id="feedback-panel" style="width:240px;background:#fff;border-radius:12px;
     padding:16px;box-shadow:0 4px 16px rgba(0,0,0,.1);height:fit-content;">
  <div style="font-size:14px;font-weight:700;margin-bottom:12px;">💬 Ghi chú màn hình này</div>
  <div id="feedback-list" style="min-height:60px;margin-bottom:12px;"></div>
  <textarea id="feedback-input" placeholder="Nhập nhận xét..." rows="3"
    style="width:100%;padding:8px;border:1.5px solid #E5E7EB;border-radius:8px;
           font-size:13px;resize:none;outline:none;"></textarea>
  <button onclick="addFeedback()"
    style="width:100%;padding:8px;background:#1F4E79;color:#fff;border:none;
           border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;margin-top:6px;">
    + Thêm ghi chú
  </button>
  <button onclick="exportFeedback()"
    style="width:100%;padding:8px;background:#f0f0f0;color:#333;border:none;
           border-radius:8px;font-size:12px;cursor:pointer;margin-top:6px;">
    📋 Export tất cả feedback
  </button>
  <textarea id="export-out" style="display:none;width:100%;height:80px;margin-top:6px;
    font-size:11px;border:1px solid #ccc;border-radius:6px;padding:6px;"></textarea>
</div>
```

## CSS Techniques quan trọng

### Phone Frame
```css
.phone-frame {
  width: 390px;
  height: 844px;
  background: #1a1a1a;
  border-radius: 55px;
  padding: 12px;
  box-shadow: 0 50px 100px rgba(0,0,0,0.3), inset 0 0 0 2px #333;
  margin: 40px auto;
}
.phone-notch {
  width: 120px; height: 34px;
  background: #1a1a1a;
  border-radius: 0 0 20px 20px;
  margin: 0 auto 8px;
}
.phone-screen {
  width: 100%; height: calc(100% - 46px);
  background: white;
  border-radius: 44px;
  overflow: hidden;
  position: relative;
}

/* ── RESPONSIVE DEVICE TOGGLE CSS (BẮT BUỘC KHI CÓ TOGGLE MOBILE/DESKTOP) ── */
.viewport-mobile .app-sidebar { display: none !important; }
.viewport-mobile .app-shell { flex-direction: column !important; width: 100% !important; }
.viewport-mobile .app-main { width: 100% !important; }
.viewport-mobile .app-header { padding: 0 12px !important; }
.viewport-mobile .screen-content-area { padding: 12px !important; padding-bottom: 70px !important; }
.viewport-mobile .stats-grid { grid-template-columns: repeat(2, 1fr) !important; gap: 8px !important; }
.viewport-mobile .stat-val { font-size: 16px !important; }
.viewport-mobile .card { padding: 12px 14px !important; margin-bottom: 12px !important; }
.viewport-mobile .mobile-bottom-nav { display: flex !important; }
.viewport-mobile .desktop-only { display: none !important; }
.viewport-mobile .mobile-only { display: block !important; }
```

### Screen switching
```css
.screen { display: none; height: 100%; overflow-y: auto; }
.screen.active { display: flex; flex-direction: column; }
```

### CSS-only Bar Chart (thống kê)
```css
.bar { height: var(--h); background: var(--primary); border-radius: 4px 4px 0 0; }
/* Dùng inline style="--h: 80%" cho từng bar */
```

### Skeleton Loading
```css
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
```

---

## Header Comment trong file HTML

Luôn thêm comment đầu file để khách hàng biết:

```html
<!--
  ┌─────────────────────────────────────────────────────────┐
  │  [TÊN DỰ ÁN] — UX/UI PROTOTYPE v1.0                    │
  │  Tạo bởi: AI Prototype Skill                            │
  │  Ngày: [date]                                           │
  ├─────────────────────────────────────────────────────────┤
  │  HƯỚNG DẪN SỬ DỤNG:                                    │
  │  1. Mở file này bằng Chrome/Firefox/Edge                │
  │  2. Click vào tên màn hình ở panel trái để điều hướng   │
  │  3. Click các button/tab trong màn hình để trải nghiệm  │
  │  4. Đây là PROTOTYPE — data là mẫu, không phải thật     │
  ├─────────────────────────────────────────────────────────┤
  │  SCREENS ([N] màn hình):                                │
  │  Role Nhân viên : [danh sách màn hình]                  │
  │  Role Canteen   : [danh sách màn hình]                  │
  ├─────────────────────────────────────────────────────────┤
  │  ASSUMPTIONS:                                           │
  │  - Mobile first (390px width — iPhone 14)               │
  │  - [các assumption khác]                                │
  └─────────────────────────────────────────────────────────┘
-->
```

---

