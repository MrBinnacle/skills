import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'
import type { Approved, Delivered, Entry, Row, Saved, Thought, View } from '../types'
import { dismissAll, handAll, heldHeadsUps, mergedHeadsUps, restoreHeadsUps, scanStore, unhidden, waitingHeadsUps, watchHeadsUps } from './headsups'
import type { HeadsUps } from '../types'

// Binnacle HUD. The mod does not send the Log to Claude; absence from later
// model requests is unverified. Memory holds a draft and the snapshot a confirmed
// Send gave Claude, which rides in Claude's system prompt on every request.
//
// Keys inside the pane (after /hud or a click, then Tab off the field): the action row under the field is the whole list, built from what
// is on screen, so no key is shown that has no button.
//
// State lives under keys types/index.d.ts declares: `view`, the pane's own UI
// state; `typed`, the field's text, echoed wrapped above it because the host's
// Input cuts a long line off at the edge (native, 2026-11-08); `log`, the kept
// thoughts, newest last; `memory`, the draft lines; `approved`, the lines
// Send gave Claude; and `delivered`, which Send the memory section last carried.
// Draft and snapshot are two atoms so no edit can rewrite what was approved,
// and only the section hook writes `delivered`, so a Send cannot claim it arrived.
const PANE = 'binnacle-hud'
const SEND = 'Send'
// $.ui.ask needs two labels; neither keeps anything.
const NOT_NOW = 'Not now'
const CANCEL = 'Cancel'
const typed = atom({ plugin: 'binnacle-hud', key: 'typed' } as const, '')
const kept = atom({ plugin: 'binnacle-hud', key: 'log' } as const, [] as Thought[])
const failed = atom({ plugin: 'binnacle-hud', key: 'failed' } as const, [] as Saved[])
// Counts edits for both capture actions: equality cannot identify a retyped draft.
let edits = 0
const draft = atom({ plugin: 'binnacle-hud', key: 'memory' } as const, [] as Saved[])
const approved = atom({ plugin: 'binnacle-hud', key: 'approved' } as const, null as Approved | null)
const delivered = atom({ plugin: 'binnacle-hud', key: 'delivered' } as const, null as Delivered | null)
const view = atom({ plugin: 'binnacle-hud', key: 'view' } as const, { ring: 0, expand: 0, failed: '' } as View)

// Session state has no documented size limit, so the mod sets its own.
// The Log and the failed list drop their oldest entry; Memory refuses a new
// line instead, because dropping one would change what the next Send carries.
const LOG_MAX = 100
const FAILED_MAX = 100
const MEMORY_MAX = 20
const TEXT_MAX = 2000 // characters in one thought or line
// Hidden characters go first, so the cut counts what Claude reads (G5).
const clip = (text: string) => Array.from(unhidden(text)).slice(0, TEXT_MAX).join('')
const isLong = (text: string) => Array.from(unhidden(text)).length > TEXT_MAX
// A docked row stops at this many lines, so one long thought cannot push the
// field out of the pane. Text took maxLines in 2.1.326; an older engine refuses
// the prop and the pane draws nothing (measured on 2.1.325), so it waits for a version.
const ROW_LINES = 3
const MAX_LINES_SINCE = [2, 1, 326]
export const takesMaxLines = (version: string): boolean => {
  const have = version.split(/[.-]/).slice(0, 3).map(Number)
  const i = MAX_LINES_SINCE.findIndex((want, n) => have[n] !== want)
  return i === -1 || (have[i] ?? 0) > MAX_LINES_SINCE[i]!
}

// Binnacle Board palette, dark (artifact AQriRu2Xwo2ACiR981H89b, via the skills session 2026-11-08).
// shortcut: dark values only; add the light variants once a theme read exists.
const MARK = ['#9a9d78', '#85876a', '#70725c', '#5c5d4a', '#484838'] // olive fading to drab
const LIGHT = '#e2e0ae' // the board's one light: only the thing that wants you
const DRAB = '#484838'
const TONE: Record<string, string> = { remember: 'success', warning: '#d0493a', claude: LIGHT }

// Claude Code alone decides dock or inline: dock needs fullscreen and 110
// columns (d.ts 2532). The one choice left to the person is what the HUD does
// when it cannot dock.
const NARROW = ['hide', 'strip'] as const
type Narrow = (typeof NARROW)[number]
export const narrowOf = (v: unknown): Narrow => NARROW.find(one => one === v) ?? 'hide'
const DOCK_COLUMNS = 110

export const whyNoDock = (isFullscreen: boolean | undefined, columns: number | undefined): string | undefined =>
  isFullscreen === false ? 'needs fullscreen (/tui fullscreen)'
  : columns !== undefined && columns < DOCK_COLUMNS ? `needs ${DOCK_COLUMNS} columns, now ${columns}`
  : undefined

const hhmm = (at: number | string) => new Date(at).toTimeString().slice(0, 5)
const same = (a: readonly string[], b: readonly string[]) => a.length === b.length && a.every((l, i) => l === b[i])

const entry = (text: string): Entry => ({ id: crypto.randomUUID(), text })
// An id is only ever minted, never derived from a value, so it cannot recur.
// A bare string (4.1.0) has none until session.start mints one, and no key acts on it.
const entries = (saved: readonly Saved[]): Row[] => saved.map(s => typeof s === 'string' ? { id: null, text: s } : s)
const minted = (saved: readonly Saved[]): Saved[] => saved.map(s => typeof s === 'string' ? entry(s) : s)

const memoryText = (snap: Approved) => [`Memory the operator approved at ${hhmm(snap.at)}:`, ...snap.lines].join('\n')

// The words, their colour and the Send key come from one answer, so the
// colour never says "Claude has them" beside words that do not. Only the
// section hook's record says Claude has a Send; a Send alone is pending.
type Status = { text: string; tone: keyof typeof TONE | null; send: boolean }
export const statusOf = (lines: readonly string[], snap: Approved | null, seen: Delivered | null, missed?: number): Status => {
  if (!snap) return { text: 'Not sent.', tone: null, send: true }
  const arrived = seen?.at === snap.at
  if (!same(lines, snap.lines)) return arrived
    ? { text: `Changed since Send. Claude has the ${hhmm(snap.at)} version.`, tone: 'claude', send: true }
    : { text: `Changed since Send. The ${hhmm(snap.at)} version is not yet in Claude's instructions.`, tone: 'claude', send: true }
  return arrived
    ? { text: `In Claude's instructions since ${hhmm(seen.since)}.`, tone: 'remember', send: false }
    : missed === snap.at
      ? { text: `Sent at ${hhmm(snap.at)}, but a turn ran without it in Claude's instructions. Press q to put the lines in the prompt instead.`, tone: 'warning', send: false }
      : { text: `Sent at ${hhmm(snap.at)}. Not yet in Claude's instructions.`, tone: null, send: false }
}

// Appends in one update, so two quick keeps cannot overwrite each other.
async function keep($: EngineInterface, text: string, from: Thought['from']): Promise<boolean | null> {
  if (!clip(text).trim()) return false
  try {
    await update($, kept, items => [...items, { text: clip(text), at: new Date().toISOString(), from }].slice(-LOG_MAX))
    return true
  } catch {
    const miss = entry(clip(text))
    await update($, failed, items => [...items, miss].slice(-FAILED_MAX)).catch(() => undefined)
    return null
  }
}

async function clearDraft($: EngineInterface, text: string, at: number): Promise<void> {
  await update($, typed, now => edits === at && now === text ? '' : now).catch(() => undefined)
}

// Clears the field after a keep, unless typing went on while the keep was
// saving. A keep that fails leaves the field alone and records the text it did
// not keep, so newer typing never hides the loss.
async function submit($: EngineInterface, text: string): Promise<void> {
  const at = edits
  if (!(await keep($, text, 'terminal'))) return
  if (isLong(text)) $.ui.toast(`binnacle-hud kept the first ${TEXT_MAX} characters. The rest was dropped.`)
  await clearDraft($, text, at)
}

// Adds the field text the pane drew. A full Memory keeps the field's text.
async function addLine($: EngineInterface, text: string): Promise<void> {
  const at = edits
  if (!clip(text).trim()) return
  const line = entry(clip(text).trim())
  let added = false
  await update($, draft, lines => (added = lines.length < MEMORY_MAX) ? [...lines, line] : lines)
  if (!added) return
  if (isLong(text.trim())) $.ui.toast(`binnacle-hud kept the first ${TEXT_MAX} characters. The rest was dropped.`)
  await clearDraft($, text, at)
}

async function promote($: EngineInterface, shown: string): Promise<void> {
  const line = entry(clip(shown))
  await update($, draft, saved => entries(saved).at(-1)?.text === line.text || saved.length >= MEMORY_MAX ? saved : [...saved, line])
}

// Each caller names its atom at the update call, which the hooks scan requires.
const without = (ids: readonly string[]) => (saved: readonly Saved[]) => saved.filter(s => typeof s === 'string' || !ids.includes(s.id))

// The lines are frozen when Send is pressed: the question and the snapshot
// carry that one value, whatever the draft becomes meanwhile. The prompt
// section reads the snapshot, so writing it is the Send.
async function send($: EngineInterface): Promise<void> {
  const lines = entries(await read($, draft)).map(l => l.text)
  if (!lines.length) return
  const question = `Memory for Claude:\n${lines.map(l => `- ${l}`).join('\n')}\n\nGive Claude these ${lines.length} lines now? Claude's next request rewrites the prompt cache once, so it costs more and takes longer than a cached one.`
  const answer = await $.ui.ask(question, [SEND, NOT_NOW]).catch(() => NOT_NOW)
  if (answer !== SEND) return
  const at = await $.clock.now()
  const refusal = await update($, approved, () => ({ lines, at })) // overwrite: the newest Send replaces what Claude reads
    .then(() => '', (err: unknown) => err instanceof Error ? err.message : String(err))
  // The engine caches a section answer for the thread; dropping it makes the next turn ask again.
  if (!refusal) $.ui.invalidate('prompt.section')
  await update($, view, v => ({ ...v, failed: refusal, refusedLines: lines }))
}

// Puts the approved lines in the prompt box, for a Send the memory section
// never carried. Only the operator's submit sends them.
async function quoteApproved($: EngineInterface): Promise<void> {
  const snap = await read($, approved)
  if (!snap) return
  const draft = (await $.prompt.read().catch(() => ({ text: '' }))).text
  const text = `${draft.trim() ? '\n\n' : ''}Keep to these decisions for the rest of this session (Memory I approved at ${hhmm(snap.at)}):\n${snap.lines.map(l => `- ${l}`).join('\n')}`
  const filled = await $.prompt.fill({ text, mode: 'append' }).catch(() => ({ isFilled: false }))
  if (!filled.isFilled) $.ui.toast('binnacle-hud could not put the Memory lines in the prompt box. Close any open dialog and press q again.')
}

// A main-loop turn that started after a Send and ended with the memory
// section never carrying it: the lines did not reach Claude (G6). statusOf
// ignores the mark once the section has carried that Send.
async function checkCarried($: EngineInterface, from: number): Promise<void> {
  const snap = await read($, approved)
  if (!snap || from < snap.at) return
  await update($, view, v => ({ ...v, missed: snap.at }))
}

// What /clear and /resume carry. The approved snapshot and its delivery
// record are never carried: Memory is approved for one conversation. A resume
// opens another conversation, so its heads-ups stay behind.
type Held = { log: Thought[]; failed: Saved[]; draft: Saved[]; typed: string; heads: HeadsUps | null }
const idOf = (s: Saved) => typeof s === 'string' ? s : s.id
const merged = <T,>(held: readonly T[], now: readonly T[], same: (a: T, b: T) => boolean) => [...held, ...now.filter(n => !held.some(h => same(h, n)))]

async function holdAll($: EngineInterface, reason: 'clear' | 'resume'): Promise<Held> {
  return {
    log: await read($, kept), failed: await read($, failed), draft: await read($, draft), typed: await read($, typed),
    heads: reason === 'clear' ? await heldHeadsUps($) : null,
  }
}

// Two holds, the older first: a second /clear before the first restore ran
// folds into it, so one restore runs and the newer draft wins.
const combined = (older: Held, newer: Held): Held => ({
  log: merged(older.log, newer.log, (a, b) => a.at === b.at && a.text === b.text).slice(-LOG_MAX),
  failed: merged(older.failed, newer.failed, (a, b) => idOf(a) === idOf(b)).slice(-FAILED_MAX),
  draft: merged(older.draft, newer.draft, (a, b) => idOf(a) === idOf(b)).slice(0, MEMORY_MAX),
  typed: newer.typed || older.typed,
  heads: newer.heads && older.heads ? mergedHeadsUps(older.heads, newer.heads) : newer.heads,
})

// Merges by identity into whatever the new session already holds, so running
// it twice loses and doubles nothing.
async function restoreAll($: EngineInterface, held: Held): Promise<void> {
  if (held.log.length) await update($, kept, now => merged(held.log, now, (a, b) => a.at === b.at && a.text === b.text).slice(-LOG_MAX))
  if (held.failed.length) await update($, failed, now => merged(held.failed, now, (a, b) => idOf(a) === idOf(b)).slice(-FAILED_MAX))
  if (held.draft.length) await update($, draft, now => merged(held.draft, now, (a, b) => idOf(a) === idOf(b)).slice(0, MEMORY_MAX))
  if (held.typed) await update($, typed, now => now || held.typed)
  if (held.heads && (held.heads.waiting.length || held.heads.done.length)) await restoreHeadsUps($, held.heads)
}

const COMMANDS = [
  { name: 'hud', description: 'Open the Binnacle HUD. /hud narrow hide|strip sets what it does without room to dock' },
  { name: 'log', description: 'Keep a thought in the Binnacle Log, from any surface, the phone included' },
]

export const register: Register = (on, options) => {
  const noDock = narrowOf(options.narrow)
  // rows is the inline height alone; a docked pane ignores it.
  const pane = { id: PANE, title: 'Binnacle', columns: 46, rows: noDock === 'hide' ? 1 : 8 }
  // Held from the press to the end of the Send, so a second press while
  // the question is open asks nothing.
  let sending = false
  watchHeadsUps(on)
  // Unknown until session.start reads the engine's version.
  let rowLines: number | undefined

  // A hook that throws is skipped from that point, so a refused command name
  // is caught, and the pane, the migrations and both registers come before
  // the version read.
  on('session.start', async ($, e, next) => {
    // Unasked, the pane waits undrawn below 144 columns (d.ts 2532-2533).
    void $.ui.open(pane).catch((err: unknown) => $.ui.toast(`binnacle-hud could not open the HUD: ${err instanceof Error ? err.message : String(err)}. Run /hud to try again.`))
    if ((await read($, draft)).some(s => typeof s === 'string')) await update($, draft, minted).catch(() => undefined)
    if ((await read($, failed)).some(s => typeof s === 'string')) await update($, failed, minted).catch(() => undefined)
    for (const command of COMMANDS) {
      await $.command.register(command).catch(() => $.ui.toast(`binnacle-hud could not register /${command.name}: Claude Code refused the name.`))
    }
    rowLines = await $.session.version().then(v => takesMaxLines(v.base ?? v.version) ? ROW_LINES : undefined, () => undefined)
    // The pane may have drawn before the version was known.
    if (rowLines) $.ui.invalidate('ui.render')
    await scanStore($).catch(() => undefined)
    return next(e)
  })

  // /clear and /resume reset session state and raise no session.start. State
  // is still readable here, and a write from clock.after(0) lands in the new
  // session (headless probes a and c, 2.1.326, each seen twice).
  // A module variable outlives /clear (probe b), so a hold waits here for its restore.
  let pending: Held | null = null
  on('session.end', async ($, e, next) => {
    const reason = e.reason === 'clear' || e.reason === 'resume' ? e.reason : null
    const held = reason ? await holdAll($, reason).catch(() => null) : null
    const ended = await next(e)
    if (!held) return ended
    pending = pending ? combined(pending, held) : held
    $.clock.after(0, () => {
      const due = pending
      pending = null
      if (due) void restoreAll($, due).catch(() => undefined)
    })
    return ended
  })

  // Subagents fire these too (`e.agentId`); only the main loop's turn counts.
  let turnFrom: number | null = null
  on('turn.start', async ($, e, next) => {
    if (e.agentId === undefined) turnFrom = await $.clock.now()
    return next(e)
  })
  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId !== undefined) return result
    const from = turnFrom
    turnFrom = null
    await scanStore($).catch(() => undefined)
    // A stopped turn or an API error can end before any request asked for the section.
    if (from !== null && (e.reason === 'answer' || e.reason === 'refusal')) await checkCarried($, from).catch(() => undefined)
    return result
  })

  // Memory joins Claude Code's own `memory` section, which the full and the
  // short prompt both carry. A section of the mod's own is a prompt.compose
  // answer, and a changed one waits for the next compaction (probe, 2.1.325).
  // A section answer that breaks the cache goes out on the next turn.
  on('prompt.section', { name: 'memory' }, async ($, e, next) => {
    const out = await next(e)
    const snap = await read($, approved)
    if (!snap) return out
    const since = await $.clock.now()
    // A failed write must not fail the hook: a failed hook passes through and drops the lines.
    await update($, delivered, now => now && now.at >= snap.at ? now : { at: snap.at, since }).catch(() => undefined)
    return { text: [out.text, memoryText(snap)].filter(Boolean).join('\n\n'), breakPromptCache: true }
  })

  on('command.run', { command: 'hud' }, async ($, e) => {
    const [word = '', value = ''] = e.args.trim().toLowerCase().split(/\s+/)
    if (word === 'narrow') {
      const wanted = NARROW.find(one => one === value)
      if (!wanted) return { text: `Without room for the side panel the HUD will ${noDock}. Change it with /hud narrow hide or /hud narrow strip.` }
      const set = await $.config.set({ key: 'binnacle-hud.narrow', value: wanted })
      return { text: set.deny ? `Could not change it: ${set.deny}` : `Done. Without room for the side panel the HUD will ${wanted === 'hide' ? 'shrink to one line' : 'show as a strip above the prompt'}.` }
    }
    // Asked, the composer is empty again, so focus is honoured (d.ts PaneOpenArgs.focus).
    const opened = await $.ui.open({ ...pane, focus: true })
    const why = whyNoDock(e.presentation.isFullscreen, e.presentation.columns)
    if (!opened.isPlaced) return { text: `Binnacle not placed: ${opened.reason}` }
    return { text: !why ? 'Binnacle open beside the chat, ready to type. Esc returns to the prompt.'
      : noDock === 'hide' ? `The side panel ${why}: widen or maximize the window. Until then it shows one line. /hud narrow strip shows the full HUD above the prompt instead.`
      : `The side panel ${why}: widen or maximize the window. Showing it above the prompt for now.` }
  })

  // The phone draws no pane, but it draws the question dialog, and text typed
  // under Other reaches the mod without entering the conversation (phone probe,
  // 2026-11-09). The command line and its reply are recorded, so neither
  // carries the thought.
  on('command.run', { command: 'log' }, async ($, e) => {
    if (e.args.trim()) return { text: 'Nothing kept. Text after /log is in the conversation; run /log alone and type the thought in the dialog.' }
    const answer = await $.ui.ask("What's the thought? Type it under Other.", [NOT_NOW, CANCEL]).catch(() => NOT_NOW)
    if (answer === NOT_NOW || answer === CANCEL) return { text: 'Nothing kept.' }
    const from = e.origin.kind === 'bridge' ? 'phone' : 'terminal'
    const saved = await keep($, answer, from)
    const cut = isLong(answer) ? ` Only its first ${TEXT_MAX} characters were kept.` : ''
    return { text: saved === null ? 'Not kept, the save failed. The thought is shown in the HUD.' : saved ? `Kept in the Log.${cut}` : 'Nothing kept.' }
  })

  // Where the ring stands decides the key line.
  on('ui.focus', async ($, e, next) => {
    if (e.component === 'Pane' && e.requestId === PANE) {
      const ring: View['ring'] = e.element === undefined ? 0 : e.element === 'thought' ? 1 : 2
      void update($, view, v => ({ ...v, ring })).catch(() => undefined)
    }
    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button, Input } = $.ui.resolve(e)
    const st = await read($, view)
    const now = await read($, typed)
    const unsaved = entries(await read($, failed))
    const thoughts = await read($, kept)
    const rows = entries(await read($, draft))
    const lines = rows.map(r => r.text)
    const last = rows.at(-1)?.id
    const snap = await read($, approved)
    const notes = await waitingHeadsUps($)
    const said = statusOf(lines, snap, await read($, delivered), st.missed)
    const room = lines.length < MEMORY_MAX
    const status = said.text
    // A refusal is news only beside the lines it refused, and while they differ from the last Send.
    const besideRefused = !!st.refusedLines && same(lines, st.refusedLines)
    const sentThem = !said.send
    const refused = besideRefused && !sentThem ? st.failed : ''

    const focused = e.props.isFocused
    const inline = e.props.placement === 'inline'
    const cols = e.props.bodyColumns
    const w = Math.max(20, cols - 2) // paddingX 1
    const narrow = w < 36

    // --- vocabulary -------------------------------------------------------
    const seg = Math.max(1, Math.floor(w * 0.08))
    const hairline = (
      <Box flexDirection="row">
        {MARK.map((c, i) => <Text key={`hl-${i}`} color={c}>{'─'.repeat(seg)}</Text>)}
        <Text dimColor>{'─'.repeat(Math.max(0, w - MARK.length * seg))}</Text>
      </Box>
    )
    const title = <Text bold><Text color={MARK[0]}>◆</Text> Binnacle</Text>
    const header = (label: string, count: string) => (
      <Box flexDirection="row" justifyContent="space-between" marginTop={1}>
        <Text bold>{label}</Text>
        <Text dimColor wrap="truncate-start">{count}</Text>
      </Box>
    )
    const quiet = (t: string) => <Text dimColor wrap="wrap">{t}</Text>
    const key = (k: string, label: string, onPress: () => void, primary?: boolean) => (
      <Button key={`k-${k}`} hotkey={k} plain={primary ? undefined : true} dimColor={!primary}
        variant={primary ? 'primary' : undefined} onPress={onPress}>{label}</Button>
    )

    // --- memory ------------------------------------------------------------
    // The status is its own wrapped line, so its words survive a narrow pane.
    const memory = (
      <Box flexDirection="column">
        {header('Memory', lines.length ? `${lines.length} lines` : 'empty')}
        {!(refused && !snap) && <Text wrap="wrap" color={said.tone ? TONE[said.tone] : undefined} dimColor={!said.tone}>{status}</Text>}
        {refused && <Text wrap="wrap" color={TONE.warning}>{`Not sent. ${refused}`}</Text>}
        {rows.map((r, i) => (
          <Text key={`mem-${r.id}`} wrap={inline ? 'truncate-end' : 'wrap'} maxLines={inline ? undefined : rowLines}><Text dimColor>{i + 1} </Text>{r.text}</Text>
        ))}
        {lines.length === 0 && quiet('No lines yet. Write one in the field, then press a to add it.')}
        {!room && quiet(`Memory holds ${lines.length} lines and keeps at most ${MEMORY_MAX}. Remove one to add another.`)}
      </Box>
    )

    // --- heads-ups: shown only while one waits ----------------------------
    const heads = notes.length > 0 && (
      <Box flexDirection="column">
        {header('Heads-ups', `${notes.length} waiting`)}
        {notes.map((n, i) => (
          <Text key={`hu-${i}`} color={LIGHT} wrap={inline ? 'truncate-end' : 'wrap'} maxLines={inline ? undefined : rowLines}><Text dimColor>{i + 1} </Text>{n.line}</Text>
        ))}
      </Box>
    )

    // --- log ---------------------------------------------------------------
    const thought = (t: Thought, i: number) => (
      <Box key={`log-${i}`} flexDirection="row" justifyContent="space-between">
        <Text wrap={inline ? 'truncate-end' : 'wrap'} maxLines={inline ? undefined : rowLines}><Text dimColor>{narrow ? '' : hhmm(t.at)}{t.from === 'phone' ? ' phone' : ''}  </Text>{t.text}</Text>
      </Box>
    )
    const shown = w - 12 // the field's width less its frame, label and Enter hint
    const field = (
      <Box flexDirection="column">
        {unsaved.map(f => <Text key={`failed-${f.id}`} color="warning" wrap="wrap">Not kept, the save failed: {f.text}</Text>)}
        {now.length > shown && <Text dimColor wrap="wrap">{now}</Text>}
        <Box borderStyle="round" borderColor={focused ? LIGHT : DRAB} paddingX={1}>
          <Input key="thought" label="›" placeholder="a thought for later" submitLabel="keep"
            value={now} autoFocus onSubmit={v => void submit($, v)}
            onInput={v => { const mine = ++edits; void update($, typed, now => edits === mine ? v : now).catch(() => undefined) }} />
        </Box>
      </Box>
    )
    const log = (
      <Box flexDirection="column" flexGrow={1} justifyContent="flex-end">
        {header('Log', thoughts.length ? `${thoughts.length} kept` : 'empty')}
        {thoughts.length === 0 && quiet('Nothing kept yet. The mod does not send the Log to Claude. Absence from later model requests is unverified.')}
        {thoughts.map(thought)}
        {field}
      </Box>
    )

    // --- actions: one list, built from what is on screen -----------------
    // The row that shows a key is the row that holds its button. It follows
    // the field: a click hands the ring to the first focusable element drawn,
    // not to autoFocus (native, 2026-11-08). With no field shown it stays near
    // the top, inside the scroll window.
    type Act = { k: string; label: string; run: () => void; primary?: boolean }
    const showsMemory = !inline || st.expand === 1
    const writing = now.trim() !== ''
    const newest = thoughts.at(-1)?.text
    const toggle = (n: number): Act => ({ k: 'ml'[n - 1]!, label: ['memory', 'log'][n - 1]!,
      run: () => void update($, view, v => ({ ...v, expand: v.expand === n ? 0 : n })) })
    const press = () => {
      if (sending) return
      sending = true
      return send($).finally(() => { sending = false })
    }
    const hand = () => void handAll($).then(why => { if (why) $.ui.toast(`Heads-ups not put in the prompt: ${why}.`) }).catch(() => undefined)
    const acts: Act[] = [
      ...(notes.length ? [{ k: 'h', label: `${notes.length > 1 ? `all ${notes.length}` : 'heads-up'} to prompt`, run: hand, primary: true },
        { k: 'x', label: 'dismiss heads-ups', run: () => void dismissAll($).catch(() => undefined) }] : []),
      ...(unsaved.some(f => f.id) ? [{ k: 'd', label: 'dismiss failed', run: () => void update($, failed, without(unsaved.flatMap(f => f.id ?? []))).catch(() => undefined) }] : []),
      ...(inline ? [toggle(1), toggle(2)] : []),
      ...(writing && room ? [{ k: 'a', label: 'to memory', run: () => addLine($, now) }] : []),
      ...(!writing && room && newest && lines.at(-1) !== newest ? [{ k: 'p', label: 'last thought to memory', run: () => void promote($, newest) }] : []),
      ...(showsMemory && lines.length && said.send ? [{ k: 's', label: 'send', run: press, primary: true }] : []),
      ...(said.tone === 'warning' ? [{ k: 'q', label: 'memory to prompt', run: () => void quoteApproved($).catch(() => undefined), primary: true }] : []),
      // shortcut: lines past the ninth have only 0, which removes the last one; add paging if Memory grows that long.
      ...(showsMemory && !writing ? rows.slice(0, 9).flatMap(({ id }, i) => id ? [{ k: String(i + 1), label: 'remove', run: () => void update($, draft, without([id])).catch(() => undefined) }] : []) : []),
      ...(showsMemory && !writing && rows.length > 9 && last ? [{ k: '0', label: 'remove last', run: () => void update($, draft, without([last])).catch(() => undefined) }] : []),
    ]
    const rail = focused && (
      <Box flexDirection="row" flexWrap="wrap" gap={1}>
        {acts.map(a => key(a.k, a.label, a.run, a.primary))}
        <Text dimColor>esc prompt</Text>
      </Box>
    )
    const hint = !focused ? '/hud or a click to write' : st.ring === 1 ? 'enter keeps it · tab to the actions' : undefined
    const keyline = hint && <Text dimColor wrap="truncate-end">{hint}</Text>

    // --- inline, hide: one line saying how to get the side panel ----------
    const why = inline && noDock === 'hide' ? whyNoDock(e.viewport?.isFullscreen, e.viewport?.columns) ?? 'is not available here' : undefined
    if (why) {
      return (
        <Box paddingX={1}>
          <Text wrap="truncate-end">{title}<Text dimColor>  side panel {why} · or /hud narrow strip</Text></Text>
        </Box>
      )
    }

    // --- inline: summary, actions, the field -------------------------------
    if (inline) {
      const parts = [...(notes.length ? [`heads-ups ${notes.length}`] : []), `memory ${refused ? `Not sent. ${refused}` : status}`, `log ${thoughts.length}`]
      const section = st.expand === 1 ? memory : st.expand === 2 ? log : null
      const hasField = !section || st.expand === 2
      return (
        <Box flexDirection="column" paddingX={1}>
          <Text wrap="truncate-end">{title}<Text dimColor>  {parts.join(' · ')}</Text></Text>
          {!hasField && rail}
          {section}
          {!section && field}
          {hasField && rail}
          {keyline}
        </Box>
      )
    }

    // --- dock ---------------------------------------------------------------
    return (
      <Box flexDirection="column" paddingX={1} height={e.props.scroll.bodyRows}>
        {title}
        {hairline}
        {heads}
        {memory}
        {log}
        {rail}
        {keyline}
      </Box>
    )
  })
}
