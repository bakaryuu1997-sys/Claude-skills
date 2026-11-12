'use client';

// Local ThemeProvider: light / dark / follow system.
// - No external library. Toggles the `dark` class on <html>; Tailwind reads it through the class-based dark variant.
// - The choice is stored in localStorage inside try/catch (private mode or blocked storage still renders).
// - Avoids a wrong-theme flash: put the inline script (THEME_INIT_SCRIPT) in <head> before React hydrates.
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
    // Storage blocked: ignore; the theme still changes for the current session.
  }
}

function systemPrefersDark(): boolean {
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [choice, setChoiceState] = useState<ThemeChoice>('system');
  const [resolved, setResolved] = useState<ResolvedTheme>('light');

  // Read the stored choice after mount (avoids SSR/hydration mismatch).
  useEffect(() => {
    setChoiceState(readStored());
  }, []);

  // Apply the theme to <html> and follow system changes while in 'system' mode.
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
  if (!ctx) throw new Error('useTheme must be used inside <ThemeProvider>');
  return ctx;
}

// Inline script for the layout <head> (runs before render) so the wrong theme never flashes.
// Use dangerouslySetInnerHTML with this constant only; never concatenate user data into it.
export const THEME_INIT_SCRIPT = `(function(){try{var c=localStorage.getItem('${STORAGE_KEY}');var d=c==='dark'||((c===null||c==='system')&&window.matchMedia('(prefers-color-scheme: dark)').matches);document.documentElement.classList.toggle('dark',d);document.documentElement.style.colorScheme=d?'dark':'light';}catch(e){}})();`;
