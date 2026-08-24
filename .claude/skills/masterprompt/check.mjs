#!/usr/bin/env node
// Lints a masterprompt against the rules in SKILL.md.
//
// WHY THIS IS A SCRIPT AND NOT A CHECKLIST
//
// The three rules that matter most are all countable — what language the
// instructions are in, whether the required sections exist, and whether the
// prompt hedges. A checklist gets skimmed; this fails with a line number.
//
//   node .claude/skills/masterprompt/check.mjs <file.md>
//
// Exit 0 = clean. Exit 1 = findings printed, newest-blocking first.

import { readFileSync } from "node:fs";

const file = process.argv[2];
if (!file) {
  console.error("usage: node check.mjs <masterprompt.md>");
  process.exit(2);
}
const src = readFileSync(file, "utf8");
const lines = src.split("\n");

const findings = [];
const add = (level, line, msg) => findings.push({ level, line, msg });

// --- 1. Instruction language -----------------------------------------------
//
// Hebrew is legitimate in exactly two places: inside `backticks` (an identifier,
// a column value, a UI string the agent must match byte-for-byte) and on a line
// the author marked DATA. Everywhere else it is instruction prose, and
// instruction prose in Hebrew costs ~3x the tokens and loses the model's
// strongest reasoning register.
const HEB = /[֐-׿]/;
const stripAllowed = (l) =>
  l.replace(/`[^`]*`/g, "").replace(/^\s*>.*$/, "").replace(/\|[^|]*\|/g, (m) => m);

let inFence = false;
lines.forEach((raw, i) => {
  const n = i + 1;
  if (/^\s*```/.test(raw)) { inFence = !inFence; return; }
  if (inFence) return;                       // code blocks may hold anything
  if (/DATA:/.test(raw)) return;             // explicitly marked data line
  const bare = stripAllowed(raw);
  if (HEB.test(bare)) {
    add("error", n, `Hebrew in instruction prose. Move it into \`backticks\` if it is a literal the agent must match, or translate it.`);
  }
});

// --- 2. The output-language directive --------------------------------------
// Without it the pasted session mirrors the language of whatever the user types
// next, and the prompt's own language stops governing anything.
// A dedicated Language heading counts: house style may govern artifact languages
// and reply register separately, and that is a legitimate shape.
if (!/output language/i.test(src) && !/^#+.*\blanguage\b/im.test(src)) {
  add("error", 0, "No output-language directive and no Language section. The target session will mirror whatever the user types next.");
}

// --- 3. Required spine ------------------------------------------------------
// Deliberately generous. These match against the WHOLE document, and a false
// "missing section" on a document that has it under different wording destroys
// trust in every other finding the checker reports.
const SECTIONS = [
  [/verified|already works|ground truth|what is built/i, "a VERIFIED-TRUTH section (what not to rebuild)"],
  [/blocker|what blocks|remaining|workstream|last mile/i, "a BLOCKERS or WORKSTREAMS section"],
  [/only .*(you|the user|human) can|user must|hand off|'s part\b|the human's part|your part|blocked on (a|the) (person|human)/i,
    "a HUMAN-ONLY-ACTIONS section"],
  [/done|acceptance|exit criteria|definition of done/i, "a DONE-CONDITIONS section"],
  [/never|forbidden|do not|boundar|halt condition/i, "a BOUNDARIES or HALT-CONDITIONS section"],
  [/first (action|step|message|thing)|start here|begin by|before any code/i, "a FIRST-ACTION section"],
];
for (const [re, label] of SECTIONS) {
  if (!re.test(src)) add("error", 0, `Missing ${label}.`);
}

// --- 4. Hedging -------------------------------------------------------------
// A masterprompt exists to remove uncertainty. These phrases put it back.
const HEDGE = /\b(should work|probably|might work|I think|hopefully|seems to|appears to work|more or less|roughly right)\b/i;
lines.forEach((l, i) => {
  // A prompt that BANS hedging quotes the hedge to ban it. Strip quoted spans
  // first, or the rule fires on its own statement of itself.
  const unquoted = l.replace(/"[^"]*"/g, "").replace(/`[^`]*`/g, "").replace(/\u201c[^\u201d]*\u201d/g, "");
  if (HEDGE.test(unquoted)) add("warn", i + 1, `Hedge: "${l.trim().slice(0, 70)}". State it as verified, or state it as unknown.`);
});

// --- 5. Unsourced claims ----------------------------------------------------
// A number with no origin is the thing the next session will trust and be wrong
// about. Wants a date, an id, a query, or a run reference somewhere on the line.
// A number is sourced if ITS OWN line shows an origin, or if the same number
// appears on a sourced line elsewhere -- restating a figure the document
// already grounded is normal prose, not an unsourced claim.
const SOURCE = /`|\d{4}-\d{2}-\d{2}|select |run |#\d+|Z\b/i;
const groundedNums = new Set();
for (const l of lines) {
  if (SOURCE.test(l)) for (const m of l.match(/\b\d{2,}\b/g) || []) groundedNums.add(m);
}
lines.forEach((l, i) => {
  if (!/^\s*[-*|>]|\*\*/.test(l)) return;
  if (SOURCE.test(l)) return;
  // U-011 / GT-013 / v2.1 -- digits inside an identifier are not a claim.
  const scrubbed = l.replace(/[A-Za-z]+[-_.]\d+/g, "");
  const nums = (scrubbed.match(/\b\d{2,}\b/g) || []).filter((n) => !groundedNums.has(n));
  if (nums.length > 0) {
    add("warn", i + 1, `Number with no source anywhere (${nums.join(", ")}): "${l.trim().slice(0, 60)}"`);
  }
});

// --- 6. Cost ----------------------------------------------------------------
// Hebrew is the worst-tokenising script in common use -- roughly a third of
// English's characters-per-token -- so the same brief in Hebrew eats context
// that could have held facts.
const heb = (src.match(/[֐-׿]/g) || []).length;
const ascii = src.length - heb;
const est = Math.round(ascii / 4 + heb / 1.3);
const allHeb = Math.round(src.length / 1.3);

console.log(`${file}`);
console.log(`  ~${est} tokens (${heb} Hebrew chars). All-English equivalent: ~${Math.round(src.length / 4)}.`);

if (findings.length === 0) {
  console.log("  clean\n");
  process.exit(0);
}
const errs = findings.filter((f) => f.level === "error");
const warns = findings.filter((f) => f.level === "warn");
for (const f of [...errs, ...warns]) {
  console.log(`  ${f.level.toUpperCase().padEnd(5)} ${f.line ? "L" + f.line : "-"}  ${f.msg}`);
}
console.log(`\n  ${errs.length} error(s), ${warns.length} warning(s)`);
process.exit(errs.length > 0 ? 1 : 0);
