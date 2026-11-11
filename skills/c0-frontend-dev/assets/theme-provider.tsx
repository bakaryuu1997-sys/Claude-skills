'use client';

// Mẫu ThemeProvider cục bộ (xem SKILL.md c0, trụ cột UI): sáng / tối / theo hệ thống.
// - Không có thư viện ngoài. Đổi class `dark` trên <html>; Tailwind đọc qua `darkMode: 'class'`.
// - Lưu lựa chọn trong localStorage bọc try/catch (chế độ riêng tư / bị chặn vẫn render đúng).
// - Chống nháy sai theme: đặt script inline trong <head> (xem THEME_INIT_SCRIPT) trước khi React hydrate.
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';

export type ThemeChoice = 'light' | 'dark' | 'system';
type ResolvedTheme = 'light' | 'dark';

const STORAGE_KEY = 'app-theme';

type ThemeContextValue = {
  choice: ThemeChoice;
  resolved: ResolvedTheme;
  setChoice: (next: ThemeChoice) => void;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);

function readStored(): ThemeChoice {
  try {
    const v = window.localStorage.getItem(STORAGE_KEY);
    return v === 'light' || v === 'dark' || v === 'system' ? v : 'system';
  } catch {
    return 'system';
  }
}

function writeStored(value: ThemeChoice): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, value);
  } catch {
    // Trình duyệt chặn lưu trữ: bỏ qua, theme vẫn đổi trong phiên hiện tại.
  }
}

function systemPrefersDark(): boolean {
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [choice, setChoiceState] = useState<ThemeChoice>('system');
  const [resolved, setResolved] = useState<ResolvedTheme>('light');

  // Đọc lựa chọn đã lưu sau khi mount (tránh lệch SSR/hydration).
  useEffect(() => {
    setChoiceState(readStored());
  }, []);

  // Áp dụng theme lên <html> và theo dõi thay đổi của hệ thống khi ở chế độ 'system'.
  useEffect(() => {
    const apply = () => {
      const next: ResolvedTheme = choice === 'system' ? (systemPrefersDark() ? 'dark' : 'light') : choice;
      setResolved(next);
      document.documentElement.classList.toggle('dark', next === 'dark');
      document.documentElement.style.colorScheme = next;
    };
    apply();
    if (choice !== 'system') return;
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    mq.addEventListener('change', apply);
    return () => mq.removeEventListener('change', apply);
  }, [choice]);

  const setChoice = useCallback((next: ThemeChoice) => {
    writeStored(next);
    setChoiceState(next);
  }, []);

  const value = useMemo(() => ({ choice, resolved, setChoice }), [choice, resolved, setChoice]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme phải nằm trong <ThemeProvider>');
  return ctx;
}

// Script inline đặt trong <head> của layout (chạy trước khi render) để không nháy sai theme.
// Dùng dangerouslySetInnerHTML với chuỗi hằng số này — KHÔNG ghép dữ liệu người dùng vào đây.
export const THEME_INIT_SCRIPT = `(function(){try{var c=localStorage.getItem('${STORAGE_KEY}');var d=c==='dark'||((c===null||c==='system')&&window.matchMedia('(prefers-color-scheme: dark)').matches);document.documentElement.classList.toggle('dark',d);document.documentElement.style.colorScheme=d?'dark':'light';}catch(e){}})();`;
