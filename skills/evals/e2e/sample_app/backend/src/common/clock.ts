export type Clock = () => Date;
export const CLOCK = Symbol('CLOCK');

const JST_OFFSET_MS = 9 * 60 * 60 * 1000;

/** Business "today" in Japan Standard Time as YYYY-MM-DD (the clock is injected, never read directly). */
export function businessDay(now: Date): string {
  return new Date(now.getTime() + JST_OFFSET_MS).toISOString().slice(0, 10);
}
