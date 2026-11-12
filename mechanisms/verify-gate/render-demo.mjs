// Renders demo.svg from a real run of demo.mjs. Every piece of text in the picture is taken from a
// line the demo printed. Usage: node mechanisms/verify-gate/render-demo.mjs
import { spawnSync } from "node:child_process";
import { readFileSync, realpathSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SVG_PATH = join(HERE, "demo.svg");

// The Binnacle Board palette: dark plank, matte camo panel, one fluorescent light.
const C = {
  night: "#0c0c0b", panel: "#151712", raise: "#1f231b", drab: "#484838", olive: "#9a9d78",
  ink: "#dcddcf", soft: "#b4b5a6", muted: "#8e8f84", light: "#e2e0ae", red: "#d0493a",
};
const DISPLAY = `'Barlow Condensed','Arial Narrow','Roboto Condensed',sans-serif`;
const SANS = `Barlow,'Segoe UI',Helvetica,Arial,sans-serif`;
const MONO = `'Overpass Mono',ui-monospace,'Cascadia Mono',Consolas,Menlo,monospace`;

const W = 1280, PAD = 32, IN = 36, GAP = 40;
const COL = (W - 2 * PAD - 2 * IN - GAP) / 2;
const LABEL = 64, WRAP = 56, LINE = 20;

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

// Wooden planks behind the board, drawn from a fixed seed so every render is identical.
function planks(height) {
  let seed = 7;
  const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const out = [];
  for (let y = 0; y < height; y += 22) {
    let x = -Math.floor(rnd() * 300);
    while (x < W) {
      const w = 260 + Math.floor(rnd() * 420);
      const g = 10 + Math.floor(rnd() * 22);
      out.push(`<rect x="${x}" y="${y}" width="${w - 2}" height="20" fill="rgb(${g},${g},${g - 1})"/>`);
      x += w;
    }
  }
  return out.join("");
}

// An SVG shown through <img> cannot fetch web fonts, so Barlow travels inside the file. The
// subsets in fonts/ keep the font's name table, which carries its SIL Open Font License.
function fontFaces() {
  const face = (family, weight, file) => {
    const data = readFileSync(join(HERE, "fonts", file)).toString("base64");
    return `@font-face{font-family:'${family}';font-weight:${weight};src:url(data:font/ttf;base64,${data}) format('truetype')}`;
  };
  return `<style>${face("Barlow", 400, "Barlow-Regular-subset.ttf")}${face("Barlow Condensed", 600, "BarlowCondensed-SemiBold-subset.ttf")}${face("Overpass Mono", 400, "OverpassMono-Regular-subset.ttf")}</style>`;
}

function renderRows(run, x, y0) {
  const out = [];
  let y = y0;
  for (const part of wrap(run.title, 58)) {
    out.push(text(x, y, part, `font-family="${DISPLAY}" font-weight="600" font-size="22" fill="${C.soft}"`));
    y += 26;
  }
  y += 14;
  for (const row of run.rows) {
    const isGate = row.who === "gate";
    const body = row.lines.flatMap((l, i) => wrap(l, WRAP).map((w) => ({ w, quote: i > 0 })));
    const h = body.length * LINE;
    if (isGate) {
      out.push(`<rect x="${x}" y="${y - 15}" width="${COL}" height="${h + 14}" fill="${C.raise}"/>`);
      out.push(`<rect x="${x}" y="${y - 15}" width="4" height="${h + 14}" fill="${C.light}"/>`);
    }
    const labelFill = isGate ? C.light : C.olive;
    out.push(text(x + (isGate ? 14 : 0), y, row.who.toUpperCase(), `font-family="${DISPLAY}" font-weight="600" font-size="14" letter-spacing="1.4" fill="${labelFill}"`));
    body.forEach(({ w, quote }, i) => {
      const failed = row.who === "tool" && / FAILED$/.test(w);
      const fill = isGate ? C.light : failed ? C.red : quote ? C.soft : C.ink;
      out.push(text(x + LABEL + (isGate ? 8 : 0), y + i * LINE, w, `font-family="${MONO}" font-size="13.5" fill="${fill}"`));
    });
    y += h + (isGate ? 14 : 8);
  }
  return { svg: out.join("\n"), bottom: y + 8 };
}

function renderNotes(run, x, y0) {
  const out = [];
  let y = y0;
  out.push(`<rect x="${x}" y="${y}" width="${COL}" height="1" fill="${C.drab}"/>`);
  y += 30;
  for (const note of run.notes) {
    const m = note.match(/^(.*?: )(FAIL\. .*)$/);
    if (m) {
      out.push(text(x, y, m[1], `font-family="${SANS}" font-size="15" fill="${C.soft}"`));
      y += 30;
      out.push(text(x, y, m[2], `font-family="${DISPLAY}" font-weight="600" font-size="26" fill="${C.red}"`));
      y += 30;
      continue;
    }
    const [settled, ...rest] = note.split(/(?<=\.) /);
    out.push(text(x, y, settled, `font-family="${SANS}" font-size="15" fill="${C.soft}"`));
    y += 30;
    if (rest.length) {
      out.push(text(x, y, rest.join(" "), `font-family="${DISPLAY}" font-weight="600" font-size="26" fill="${C.ink}"`));
      y += 30;
    }
  }
  return { svg: out.join("\n"), bottom: y };
}

export function render(stdout) {
  const { head, runs, tail } = parse(stdout);
  const left = PAD + IN, right = left + COL + GAP, top = PAD + 16 + 40;
  const header = [
    text(left, top + 10, "verify-gate", `font-family="${DISPLAY}" font-weight="600" font-size="38" fill="${C.ink}"`),
    text(left + 190, top + 8, head, `font-family="${SANS}" font-size="16" fill="${C.muted}"`),
    `<rect x="${left}" y="${top + 32}" width="${W - 2 * left}" height="1" fill="${C.drab}"/>`,
  ];
  const rows = [renderRows(runs[0], left, top + 76), renderRows(runs[1], right, top + 76)];
  const notesY = Math.max(rows[0].bottom, rows[1].bottom);
  const r1 = renderNotes(runs[0], left, notesY);
  const r2 = renderNotes(runs[1], right, notesY);
  let y = Math.max(r1.bottom, r2.bottom) + 4;
  const foot = [`<rect x="${left}" y="${y}" width="${W - 2 * left}" height="1" fill="${C.drab}"/>`];
  y += 28;
  for (const line of tail) {
    foot.push(text(left, y, line, `font-family="${SANS}" font-size="14" fill="${C.muted}"`));
    y += 22;
  }
  const panelBottom = y + IN - 14;
  const H = panelBottom + PAD;
  const alt = `verify-gate demo. Run 1, without the gate: the agent edits price.mjs, says done, and the run ends with the tests failing. Run 2, same script with the gate: the gate sends the agent back, it runs npm test, and reports the failure.`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(alt)}">
<title>${esc(alt)}</title>
<defs>
${fontFaces()}
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.004 0.35" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.48  0 0 0 0.3 0"/></filter>
<filter id="camo" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.011 0.05" numOctaves="2" seed="11"/><feColorMatrix values="1 0 0 0 0  1 0 0 0 0  1 0 0 0 0  0 0 0 0 1"/><feComponentTransfer><feFuncR type="discrete" tableValues="0.05 0.11 0.2 0.29"/><feFuncG type="discrete" tableValues="0.055 0.13 0.22 0.3"/><feFuncB type="discrete" tableValues="0.045 0.09 0.16 0.21"/></feComponentTransfer></filter>
</defs>
<rect width="${W}" height="${H}" fill="${C.night}"/>
${planks(H)}
<rect width="${W}" height="${H}" filter="url(#grain)"/>
<rect x="${PAD - 1}" y="${PAD - 1}" width="${W - 2 * PAD + 2}" height="${panelBottom - PAD + 2}" fill="#000"/>
<rect x="${PAD}" y="${PAD}" width="${W - 2 * PAD}" height="${panelBottom - PAD}" fill="${C.panel}" fill-opacity="0.94"/>
<rect x="${PAD}" y="${PAD}" width="${W - 2 * PAD}" height="16" filter="url(#camo)"/>
<rect x="${PAD}" y="${PAD + 16}" width="${W - 2 * PAD}" height="1" fill="#000"/>
${header.join("\n")}
${rows[0].svg}
${rows[1].svg}
${r1.svg}
${r2.svg}
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
  writeFileSync(SVG_PATH, render(runDemo()));
  console.log(`wrote ${SVG_PATH}`);
}
