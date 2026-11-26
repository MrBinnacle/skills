// Renders the demo pictures (VARIANTS) from a real run of demo.mjs and saves that run's output as demo-output.txt,
// which the tests render again to prove the committed pictures match this code. Every piece of
// visible text in the picture is taken from a line the demo printed.
// Usage: node mechanisms/verify-gate/render-demo.mjs
import { spawnSync } from "node:child_process";
import { readFileSync, realpathSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));

// Colours come from assets/tokens.json, one scheme each, so the picture is drawn in the site's
// own system. The red is the one colour the tokens do not have: FAIL only, and nothing else.
// Contrast on the panel (WCAG 2, measured 2026-11-27): dark red 4.87, light red 5.38.
const TOKENS = JSON.parse(readFileSync(join(HERE, "..", "..", "assets", "tokens.json"), "utf-8"));
const RED = { dark: "#EC7868", light: "#A6362A" };
function palette(scheme) {
  const t = TOKENS.color[scheme === "light" ? "structural_light" : "structural"];
  const v = (k) => t[k].value;
  return { bg: v("bg"), surface: v("surface"), ink: v("ink"), muted: v("muted"), line: v("line"), red: RED[scheme] };
}
// An SVG behind <img> cannot load the site's @font-face; tokens.json names the system fallback.
const SANS = TOKENS.type["font.body"].replace(/"/g, "'");
const MONO = TOKENS.type["font.mono"].replace(/"/g, "'");

export const VARIANTS = [
  { file: "demo-dark.svg", scheme: "dark", narrow: false },
  { file: "demo-light.svg", scheme: "light", narrow: false },
  { file: "demo-dark-narrow.svg", scheme: "dark", narrow: true },
  { file: "demo-light-narrow.svg", scheme: "light", narrow: true },
];

// Wide: two columns at 1280. Narrow: one column at 480, drawn larger so a phone can read it.
function layout(narrow) {
  const W = narrow ? 480 : 1280, PAD = narrow ? 20 : 32, IN = narrow ? 20 : 36, GAP = 40;
  const COL = narrow ? W - 2 * (PAD + IN) : (W - 2 * PAD - 2 * IN - GAP) / 2;
  const mono = narrow ? 15 : 13.5;
  return { W, PAD, IN, GAP, COL, LABEL: narrow ? 60 : 64, LINE: narrow ? 22 : 20, mono,
    wrap: Math.floor((COL - (narrow ? 60 : 64) - 12) / (mono * 0.62)), title: narrow ? 20 : 22, big: narrow ? 20 : 26 };
}

export function parse(stdout) {
  const lines = stdout.replace(/\r/g, "").split("\n");
  const head = lines.find((l) => l.startsWith("verify-gate demo: "));
  const runs = [];
  const tail = [];
  for (const line of lines) {
    if (/^Run \d: /.test(line)) runs.push({ title: line, rows: [], notes: [] });
    else if (/^(Real|Scripted): /.test(line)) tail.push(line);
    else if (!runs.length || !line.trim() || line.startsWith("Guard: ")) continue;
    else {
      const run = runs.at(-1);
      const row = line.match(/^  (\w+)\s*\| (.*)$/);
      const more = line.match(/^ {8}\| (.*)$/);
      if (row) run.rows.push({ who: row[1], lines: [row[2]] });
      else if (more && run.rows.length) run.rows.at(-1).lines.push(more[1]);
      else run.notes.push(line.trim());
    }
  }
  if (!head || runs.length !== 2 || tail.length !== 2 || runs.some((r) => !r.rows.length || !r.notes.length)) {
    throw new Error("demo output did not have the expected shape: a header, two runs and the Real/Scripted lines");
  }
  return { head: head.slice("verify-gate demo: ".length), runs, tail };
}

function wrap(text, width) {
  const out = [];
  let rest = text;
  while (rest.length > width) {
    const cut = Math.max(rest.lastIndexOf(" ", width), rest.lastIndexOf(",", width) + 1);
    const at = cut > width / 2 ? cut : width;
    out.push(rest.slice(0, at).trimEnd());
    rest = rest.slice(at).trimStart();
  }
  out.push(rest);
  return out;
}

const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const text = (x, y, s, attrs) => `<text x="${x}" y="${y}" ${attrs}>${esc(s)}</text>`;

function renderRows(run, x, y0, L, C) {
  const out = [];
  let y = y0;
  for (const part of wrap(run.title, Math.floor(L.COL / (L.title * 0.62)))) {
    out.push(text(x, y, part, `font-family="${SANS}" font-weight="600" font-size="${L.title}" fill="${C.ink}"`));
    y += L.title + 6;
  }
  y += 14;
  for (const row of run.rows) {
    const isGate = row.who === "gate";
    const body = row.lines.flatMap((l, i) => wrap(l, L.wrap).map((w) => ({ w, quote: i > 0 })));
    const h = body.length * L.LINE;
    if (isGate) {
      out.push(`<rect x="${x}" y="${y - 15}" width="${L.COL}" height="${h + 14}" fill="${C.bg}"/>`);
      out.push(`<rect x="${x}" y="${y - 15}" width="3" height="${h + 14}" fill="${C.ink}"/>`);
    }
    out.push(text(x + (isGate ? 12 : 0), y, row.who.toUpperCase(), `font-family="${MONO}" font-weight="500" font-size="${L.mono - 1.5}" letter-spacing="1" fill="${C.muted}"`));
    body.forEach(({ w, quote }, i) => {
      const failed = row.who === "tool" && / FAILED$/.test(w);
      const fill = failed ? C.red : quote ? C.muted : C.ink;
      out.push(text(x + L.LABEL + (isGate ? 8 : 0), y + i * L.LINE, w, `font-family="${MONO}" font-size="${L.mono}" fill="${fill}"`));
    });
    y += h + (isGate ? 14 : 8);
  }
  return { svg: out.join("\n"), bottom: y + 8 };
}

function renderNotes(run, x, y0, L, C) {
  const out = [];
  let y = y0;
  out.push(`<rect x="${x}" y="${y}" width="${L.COL}" height="1" fill="${C.line}"/>`);
  y += 30;
  const small = (s) => { out.push(text(x, y, s, `font-family="${SANS}" font-size="15" fill="${C.muted}"`)); y += 26; };
  const big = (s, fill) => {
    for (const part of wrap(s, Math.floor(L.COL / (L.big * 0.62)))) {
      out.push(text(x, y, part, `font-family="${SANS}" font-weight="600" font-size="${L.big}" fill="${fill}"`));
      y += L.big + 6;
    }
  };
  for (const note of run.notes) {
    const m = note.match(/^(.*?: )(FAIL\. .*)$/);
    if (m) {
      small(m[1]);
      big(m[2], C.red);
      continue;
    }
    const [settled, ...rest] = note.split(/(?<=\.) /);
    small(settled);
    if (rest.length) big(rest.join(" "), C.ink);
  }
  return { svg: out.join("\n"), bottom: y };
}

export function render(stdout, { scheme = "dark", narrow = false } = {}) {
  const { head, runs, tail } = parse(stdout);
  const L = layout(narrow), C = palette(scheme);
  const left = L.PAD + L.IN, right = left + L.COL + L.GAP;
  let top = L.PAD + L.IN + 30;
  const header = [text(left, top, "verify-gate", `font-family="${SANS}" font-weight="700" font-size="${narrow ? 30 : 36}" fill="${C.ink}"`)];
  for (const part of wrap(head, Math.floor((L.W - 2 * left) / (15 * 0.58)))) {
    top += 24;
    header.push(text(left, top, part, `font-family="${SANS}" font-size="15" fill="${C.muted}"`));
  }
  top += 22;
  header.push(`<rect x="${left}" y="${top}" width="${L.W - 2 * left}" height="1" fill="${C.line}"/>`);
  const r0 = renderRows(runs[0], left, top + 44, L, C);
  const parts = [r0.svg];
  let y;
  if (narrow) {
    const n0 = renderNotes(runs[0], left, r0.bottom, L, C);
    const r1 = renderRows(runs[1], left, n0.bottom + 36, L, C);
    const n1 = renderNotes(runs[1], left, r1.bottom, L, C);
    parts.push(n0.svg, r1.svg, n1.svg);
    y = n1.bottom + 4;
  } else {
    const r1 = renderRows(runs[1], right, top + 44, L, C);
    const notesY = Math.max(r0.bottom, r1.bottom);
    const n0 = renderNotes(runs[0], left, notesY, L, C);
    const n1 = renderNotes(runs[1], right, notesY, L, C);
    parts.push(r1.svg, n0.svg, n1.svg);
    y = Math.max(n0.bottom, n1.bottom) + 4;
  }
  const foot = [`<rect x="${left}" y="${y}" width="${L.W - 2 * left}" height="1" fill="${C.line}"/>`];
  y += 28;
  for (const line of tail) {
    for (const part of wrap(line, Math.floor((L.W - 2 * left) / (14 * 0.58)))) {
      foot.push(text(left, y, part, `font-family="${SANS}" font-size="14" fill="${C.muted}"`));
      y += 22;
    }
  }
  const panelBottom = y + L.IN - 14;
  const H = panelBottom + L.PAD;
  const alt = `verify-gate demo. Run 1, without the gate: the agent edits price.mjs, says done, and the run ends with the tests failing. Run 2, same script with the gate: the gate sends the agent back, it runs npm test, and reports the failure.`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${L.W}" height="${H}" viewBox="0 0 ${L.W} ${H}" role="img" aria-label="${esc(alt)}">
<title>${esc(alt)}</title>
<rect width="${L.W}" height="${H}" fill="${C.bg}"/>
<rect x="${L.PAD}" y="${L.PAD}" width="${L.W - 2 * L.PAD}" height="${panelBottom - L.PAD}" fill="${C.surface}" stroke="${C.line}"/>
${header.join("\n")}
${parts.join("\n")}
${foot.join("\n")}
</svg>
`;
}

function runDemo() {
  const res = spawnSync(process.execPath, [join(HERE, "demo.mjs")], { encoding: "utf-8" });
  if (res.status !== 0) {
    process.stderr.write(res.stdout + res.stderr);
    console.error(`demo.mjs exited ${res.status}; no picture rendered.`);
    process.exit(res.status === 2 ? 2 : 1);
  }
  return res.stdout;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === realpathSync(process.argv[1])) {
  // The Guard line carries the run time, which the picture leaves out and every run changes.
  const output = runDemo().replace(/^Guard: .*\n?/m, "");
  writeFileSync(join(HERE, "demo-output.txt"), output);
  for (const v of VARIANTS) writeFileSync(join(HERE, v.file), render(output, v));
  console.log(`wrote ${VARIANTS.map((v) => v.file).join(", ")} and demo-output.txt`);
}
