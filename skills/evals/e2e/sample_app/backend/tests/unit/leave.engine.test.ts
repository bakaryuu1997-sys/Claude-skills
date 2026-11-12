import {
  InvalidTransitionError,
  daysBetween,
  isRangeOrdered,
  isValidDate,
  isWithin,
  overlaps,
  transition,
} from '../../src/leave/leave.engine';
import { businessDay } from '../../src/common/clock';

describe('leave.engine dates', () => {
  it.each([
    ['2026-02-28', true],
    ['2028-02-29', true], // leap year
    ['2026-02-29', false],
    ['2026-04-31', false], // April has 30 days
    ['2026-13-01', false],
    ['2026-1-01', false],
    ['', false],
  ])('isValidDate(%j) -> %s', (value, expected) => {
    expect(isValidDate(value)).toBe(expected);
  });

  it('daysBetween is a difference, so the same day is 0 and one month apart is 30', () => {
    expect(daysBetween('2027-02-01', '2027-02-01')).toBe(0);
    expect(daysBetween('2027-02-01', '2027-03-03')).toBe(30);
    expect(daysBetween('2026-12-31', '2027-01-01')).toBe(1);
  });

  it('isRangeOrdered detects reversed ranges', () => {
    expect(isRangeOrdered('2027-02-05', '2027-02-01')).toBe(false);
    expect(isRangeOrdered('2027-02-01', '2027-02-01')).toBe(true);
  });

  it('isWithin is inclusive at both ends', () => {
    expect(isWithin('2027-02-01', '2027-02-01', '2027-02-10')).toBe(true);
    expect(isWithin('2027-02-10', '2027-02-01', '2027-02-10')).toBe(true);
    expect(isWithin('2027-01-31', '2027-02-01', '2027-02-10')).toBe(false);
    expect(isWithin('2027-02-11', '2027-02-01', '2027-02-10')).toBe(false);
  });

  it('overlaps treats touching ranges as overlapping and adjacent ranges as not', () => {
    expect(overlaps('2027-02-01', '2027-02-05', '2027-02-05', '2027-02-09')).toBe(true);
    expect(overlaps('2027-02-01', '2027-02-04', '2027-02-05', '2027-02-09')).toBe(false);
    expect(overlaps('2027-02-03', '2027-02-04', '2027-02-01', '2027-02-09')).toBe(true);
  });
});

describe('transition (state table 2-1)', () => {
  it.each([
    ['draft', 'submitted'],
    ['submitted', 'approved'],
    ['submitted', 'rejected'],
    ['rejected', 'submitted'],
  ] as const)('%s -> %s is allowed', (from, to) => {
    expect(transition(from, to)).toBe(to);
  });

  it.each([
    ['approved', 'submitted'],
    ['approved', 'rejected'],
    ['draft', 'approved'],
    ['rejected', 'approved'],
  ] as const)('%s -> %s throws INVALID_TRANSITION', (from, to) => {
    expect(() => transition(from, to)).toThrow(InvalidTransitionError);
    expect(() => transition(from, to)).toThrow(/INVALID_TRANSITION/);
  });
});

describe('businessDay (JST)', () => {
  it('rolls over to the next day at 15:00 UTC', () => {
    expect(businessDay(new Date('2027-02-01T14:59:59Z'))).toBe('2027-02-01');
    expect(businessDay(new Date('2027-02-01T15:00:00Z'))).toBe('2027-02-02');
  });
});
