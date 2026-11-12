import { csvField } from '../../src/report/report.service';

describe('csvField', () => {
  it('leaves plain text untouched', () => {
    expect(csvField('abc')).toBe('abc');
  });

  it('quotes fields with separators and doubles inner quotes', () => {
    expect(csvField('a,b')).toBe('"a,b"');
    expect(csvField('say "hi"')).toBe('"say ""hi"""');
    expect(csvField('line1\nline2')).toBe('"line1\nline2"');
  });

  it.each(['=SUM(A1)', '+1', '-1', '@cmd'])('neutralises formula injection for %j', (v) => {
    expect(csvField(v)).toBe(`'${v}`);
  });
});
