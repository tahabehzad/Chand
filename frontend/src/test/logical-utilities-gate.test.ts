import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { afterEach, describe, expect, it } from 'vitest';

// Vitest runs with the frontend directory as its root.
const SCRIPT = resolve(process.cwd(), 'scripts/check-logical-utilities.mjs');

const created: string[] = [];

function fixture(source: string): string {
  const directory = mkdtempSync(join(tmpdir(), 'rtl-gate-'));
  created.push(directory);
  writeFileSync(join(directory, 'component.tsx'), source, 'utf8');
  return directory;
}

function runGate(directory: string) {
  return spawnSync(process.execPath, [SCRIPT, directory], { encoding: 'utf8' });
}

afterEach(() => {
  while (created.length > 0) {
    const directory = created.pop();
    if (directory !== undefined) rmSync(directory, { recursive: true, force: true });
  }
});

describe('the physical-utility lint gate (FE-01)', () => {
  it('accepts logical utilities', () => {
    const result = runGate(
      fixture(`export const A = () => <div className="ms-2 pe-4 text-start border-s" />;`),
    );
    expect(result.stderr).toBe('');
    expect(result.status).toBe(0);
  });

  it('rejects a physical margin utility', () => {
    const result = runGate(fixture(`export const A = () => <div className="mr-4" />;`));  // rtl-gate: allow-physical
    expect(result.status).toBe(1);
    expect(result.stderr).toContain('mr-4');  // rtl-gate: allow-physical
    expect(result.stderr).toContain('me');
  });

  it('rejects a physical positioning utility behind a variant', () => {
    const result = runGate(fixture(`export const A = () => <div className="md:left-0" />;`));  // rtl-gate: allow-physical
    expect(result.status).toBe(1);
    expect(result.stderr).toContain('md:left-0');  // rtl-gate: allow-physical
  });

  it('rejects physical text alignment', () => {
    const result = runGate(fixture(`export const A = () => <td className="text-right" />;`));  // rtl-gate: allow-physical
    expect(result.status).toBe(1);
  });

  it('rejects a physical value inside a template literal', () => {
    const result = runGate(fixture('export const cls = `flex pl-3`;'));  // rtl-gate: allow-physical
    expect(result.status).toBe(1);
  });

  it('permits a physical utility explicitly scoped to a direction', () => {
    const result = runGate(
      fixture(`export const A = () => <div className="rtl:left-0 ltr:right-0" />;`),
    );
    expect(result.status).toBe(0);
  });

  it('permits the direction-scoped mirror utility', () => {
    const result = runGate(fixture(`export const A = () => <svg className="rtl:-scale-x-100" />;`));
    expect(result.status).toBe(0);
  });

  it('honours an explicit opt-out marker on the same line', () => {
    // Only this gate's own fixtures use the marker; application code must not.
    const result = runGate(
      fixture('export const A = () => <div className="mr-4" />; // rtl-gate: allow-physical'), // rtl-gate: allow-physical
    );
    expect(result.status).toBe(0);
  });

  it('does not trip on prose in a comment', () => {
    const result = runGate(fixture(`// not right-aligned: logical only\nexport const a = 1;\n`));
    expect(result.status).toBe(0);
  });
});
