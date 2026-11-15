#!/usr/bin/env node
/**
 * The physical-utility lint gate — SPEC-FE-001 §2.2–§2.3, `FE-01`, WBS P3-T01.
 *
 * The document is RTL (`dir="rtl"` on <html>). A physical direction utility is
 * therefore a defect: `mr-4` means "margin-right" in both directions, whereas
 * `me-4` means "margin at the logical end", which is what the design intends.
 *
 * Banned (`ml-`, `mr-`, `pl-`, `pr-`, `left-`, `right-`, `text-left`,
 * `text-right`, `border-l`, `border-r`, `rounded-l…`, `float-left/right`).
 * Allowed (`ms-`, `me-`, `ps-`, `pe-`, `start-`, `end-`, `text-start`,
 * `text-end`, `border-s`, `border-e`, `rtl:-scale-x-100`).
 *
 * A physical utility that a third-party component forces is permitted **only**
 * when scoped with the `rtl:` or `ltr:` variant, exactly as §2.3 requires.
 *
 * A line may opt out explicitly with the marker `rtl-gate: allow-physical`.
 * It is used only where a banned token is *fixture data for this gate's own
 * tests* — never in application code, where the correct fix is the logical
 * utility.
 *
 * Usage: node scripts/check-logical-utilities.mjs <dir-or-file> [...]
 */

import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

const SOURCE_EXTENSIONS = new Set(['.ts', '.tsx', '.js', '.jsx', '.css', '.html']);
const ALLOW_MARKER = 'rtl-gate: allow-physical';
const IGNORED_DIRECTORIES = new Set(['node_modules', 'dist', 'build', 'coverage', '.vite']);

/** Physical prefixes, checked after the variant chain is stripped. */
const BANNED_PREFIXES = [
  'ml',
  'mr',
  'pl',
  'pr',
  'left',
  'right',
  'text-left',
  'text-right',
  'border-l',
  'border-r',
  'rounded-l',
  'rounded-r',
  'rounded-tl',
  'rounded-tr',
  'rounded-bl',
  'rounded-br',
  'float-left',
  'float-right',
];

const REPLACEMENTS = {
  ml: 'ms',
  mr: 'me',
  pl: 'ps',
  pr: 'pe',
  left: 'start',
  right: 'end',
  'text-left': 'text-start',
  'text-right': 'text-end',
  'border-l': 'border-s',
  'border-r': 'border-e',
  'rounded-l': 'rounded-s',
  'rounded-r': 'rounded-e',
  'rounded-tl': 'rounded-ss',
  'rounded-tr': 'rounded-se',
  'rounded-bl': 'rounded-es',
  'rounded-br': 'rounded-ee',
  'float-left': 'float-start',
  'float-right': 'float-end',
};

/** String literals only: prose in a comment must not trip the gate. */
const STRING_LITERAL = /(['"`])(?:\\.|(?!\1)[^\\])*\1/g;

function collectFiles(target, accumulator) {
  const stats = statSync(target);
  if (stats.isFile()) {
    const extension = target.slice(target.lastIndexOf('.'));
    if (SOURCE_EXTENSIONS.has(extension)) accumulator.push(target);
    return accumulator;
  }
  for (const entry of readdirSync(target)) {
    if (IGNORED_DIRECTORIES.has(entry)) continue;
    collectFiles(join(target, entry), accumulator);
  }
  return accumulator;
}

function strippedToken(token) {
  const withoutVariants = token.split(':').at(-1) ?? token;
  return withoutVariants.replace(/^!/, '');
}

function isScopedToDirection(token) {
  const variants = token.split(':').slice(0, -1);
  return variants.includes('rtl') || variants.includes('ltr');
}

function bannedPrefixOf(token) {
  const candidate = strippedToken(token);
  return BANNED_PREFIXES.find(
    (prefix) => candidate === prefix || candidate.startsWith(`${prefix}-`),
  );
}

const problems = [];

function auditFile(file) {
  const source = readFileSync(file, 'utf8');
  const lines = source.split(/\r?\n/);

  lines.forEach((line, index) => {
    if (line.includes(ALLOW_MARKER)) return;
    const literalPattern = new RegExp(STRING_LITERAL.source, 'g');
    let match;
    while ((match = literalPattern.exec(line)) !== null) {
      const literal = match[0].slice(1, -1);
      const tokens = literal.split(/[\s"'`]+/).filter(Boolean);
      for (const token of tokens) {
        if (isScopedToDirection(token)) continue;
        const prefix = bannedPrefixOf(token);
        if (prefix === undefined) continue;
        problems.push({
          file,
          line: index + 1,
          token,
          suggestion: REPLACEMENTS[prefix] ?? 'a logical utility',
        });
      }
    }
  });
}

const targets = process.argv.slice(2);
if (targets.length === 0) {
  console.error('usage: check-logical-utilities.mjs <dir-or-file> [...]');
  process.exit(2);
}

const files = [];
for (const target of targets) {
  collectFiles(target, files);
}

for (const file of files) {
  auditFile(file);
}

if (problems.length > 0) {
  for (const problem of problems) {
    console.error(
      `${relative(process.cwd(), problem.file)}:${problem.line}  physical direction utility "${problem.token}" — use ${problem.suggestion} (SPEC-FE-001 §2.2)`,
    );
  }
  console.error(`\n${problems.length} physical direction utility violation(s).`);
  process.exit(1);
}

console.log(`logical utilities only: ${files.length} file(s) checked, 0 violations.`);
