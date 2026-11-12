'use client';

// Local CommandPalette (Ctrl/Cmd + K): no external dependency.
// - Case-insensitive substring filter; Up/Down to move, Enter to choose, Esc to close.
// - Accessibility: role="dialog" + aria-modal, combobox/listbox, aria-activedescendant.
// - Commands are supplied by the app (`commands`), each with `run()`; user data is never written to the DOM via innerHTML.
import { useEffect, useId, useMemo, useRef, useState, type KeyboardEvent } from 'react';

export type PaletteCommand = {
  id: string;
  label: string;
  group?: string;
  keywords?: string[];
  run: () => void;
};

type Props = {
  commands: PaletteCommand[];
  open: boolean;
  onOpenChange: (open: boolean) => void;
  // UI text is required (no default) so an internal language never leaks into the customer UI.
  placeholder: string;
  emptyText: string;
  dialogLabel: string;
};

function matches(cmd: PaletteCommand, q: string): boolean {
  if (!q) return true;
  const hay = [cmd.label, cmd.group ?? '', ...(cmd.keywords ?? [])].join(' ').toLowerCase();
  return q
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)
    .every((part) => hay.includes(part));
}

export function CommandPalette({ commands, open, onOpenChange, placeholder, emptyText, dialogLabel }: Props) {
  const [query, setQuery] = useState('');
  const [active, setActive] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const listId = useId();

  const filtered = useMemo(() => commands.filter((c) => matches(c, query)), [commands, query]);

  // Reset on open and focus the input.
  useEffect(() => {
    if (open) {
      setQuery('');
      setActive(0);
      queueMicrotask(() => inputRef.current?.focus());
    }
  }, [open]);

  // Global Ctrl/Cmd+K shortcut toggles the palette.
  useEffect(() => {
    const onKey = (e: globalThis.KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        onOpenChange(!open);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onOpenChange]);

  if (!open) return null;

  const choose = (index: number) => {
    const cmd = filtered[index];
    if (!cmd) return;
    onOpenChange(false);
    cmd.run();
  };

  const onKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActive((i) => (filtered.length ? (i + 1) % filtered.length : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActive((i) => (filtered.length ? (i - 1 + filtered.length) % filtered.length : 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      choose(active);
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onOpenChange(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/40 p-4 pt-[15vh]" onMouseDown={() => onOpenChange(false)}>
      <div
        role="dialog"
        aria-modal="true"
        aria-label={dialogLabel}
        className="w-full max-w-lg overflow-hidden rounded-lg border border-slate-200 bg-white shadow-xl dark:border-slate-800 dark:bg-slate-900"
        onMouseDown={(e) => e.stopPropagation()}
      >
        <input
          ref={inputRef}
          role="combobox"
          aria-expanded="true"
          aria-controls={listId}
          aria-activedescendant={filtered[active] ? `${listId}-${filtered[active].id}` : undefined}
          aria-autocomplete="list"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setActive(0);
          }}
          onKeyDown={onKeyDown}
          placeholder={placeholder}
          className="w-full border-b border-slate-200 bg-transparent px-4 py-3 text-sm outline-none dark:border-slate-800"
        />
        <ul id={listId} role="listbox" className="max-h-80 overflow-y-auto py-2">
          {filtered.length === 0 && <li className="px-4 py-3 text-sm text-slate-500">{emptyText}</li>}
          {filtered.map((cmd, i) => (
            <li
              key={cmd.id}
              id={`${listId}-${cmd.id}`}
              role="option"
              aria-selected={i === active}
              onMouseEnter={() => setActive(i)}
              onClick={() => choose(i)}
              className={`flex cursor-pointer items-center justify-between px-4 py-2 text-sm ${
                i === active ? 'bg-slate-100 dark:bg-slate-800' : ''
              }`}
            >
              <span>{cmd.label}</span>
              {cmd.group && <span className="text-xs text-slate-500">{cmd.group}</span>}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
