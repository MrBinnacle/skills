import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'
import type { Approved, Entry, Row, Saved, Thought, View } from '../types'

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
// thoughts, newest last; `memory`, the draft lines; and `approved`, the lines
// Send gave Claude. Draft and snapshot are two atoms so no edit can rewrite
// what was approved.
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
const view = atom({ plugin: 'binnacle-hud', key: 'view' } as const, { ring: 0, expand: 0, failed: '' } as View)

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
// colour never says "Claude has them" beside words that do not.
type Status = { text: string; tone: keyof typeof TONE | null; send: boolean }
export const statusOf = (lines: readonly string[], snap: Approved | null): Status =>
  !snap ? { text: 'Not sent.', tone: null, send: true }
  : !same(lines, snap.lines) ? { text: `Changed since Send. Claude has the ${hhmm(snap.at)} version.`, tone: 'claude', send: true }
  : { text: `In Claude's instructions since ${hhmm(snap.at)}.`, tone: 'remember', send: false }

// Appends in one update, so two quick keeps cannot overwrite each other.
async function keep($: EngineInterface, text: string, from: Thought['from']): Promise<boolean | null> {
  if (!text.trim()) return false
  try {
    await update($, kept, items => [...items, { text, at: new Date().toISOString(), from }])
    return true
  } catch {
    const miss = entry(text)
    await update($, failed, items => [...items, miss]).catch(() => undefined)
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
  if (await keep($, text, 'terminal')) await clearDraft($, text, at)
}

// Adds the field text the pane drew.
async function addLine($: EngineInterface, text: string): Promise<void> {
  const at = edits
  if (!text.trim()) return
  const line = entry(text.trim())
  await update($, draft, lines => [...lines, line])
  await clearDraft($, text, at)
}

async function promote($: EngineInterface, shown: string): Promise<void> {
  const line = entry(shown)
  await update($, draft, saved => entries(saved).at(-1)?.text === shown ? saved : [...saved, line])
}

// Each caller names its atom at the update call, which the hooks scan requires.
const without = (ids: readonly string[]) => (saved: readonly Saved[]) => saved.filter(s => typeof s === 'string' || !ids.includes(s.id))

// The lines are frozen when Send is pressed: the question and the snapshot
// carry that one value, whatever the draft becomes meanwhile. The prompt
// section reads the snapshot, so writing it is the Send.
async function send($: EngineInterface): Promise<void> {
  const lines = entries(await read($, draft)).map(l => l.text)
  if (!lines.length) return
  const question = `Memory for Claude:\n${lines.map(l => `- ${l}`).join('\n')}\n\nGive Claude these ${lines.length} lines now?`
  const answer = await $.ui.ask(question, [SEND, NOT_NOW]).catch(() => NOT_NOW)
  if (answer !== SEND) return
  const at = await $.clock.now()
  const refusal = await update($, approved, () => ({ lines, at })) // overwrite: the newest Send replaces what Claude reads
    .then(() => '', (err: unknown) => err instanceof Error ? err.message : String(err))
  // The engine caches a section answer for the thread; dropping it makes the next turn ask again.
  if (!refusal) $.ui.invalidate('prompt.section')
  await update($, view, v => ({ ...v, failed: refusal, refusedLines: lines }))
}

export const register: Register = (on, options) => {
  const noDock = narrowOf(options.narrow)
  // rows is the inline height alone; a docked pane ignores it.
  const pane = { id: PANE, title: 'Binnacle', columns: 46, rows: noDock === 'hide' ? 1 : 8 }
  // Held from the press to the end of the append, so a second press while
  // the question is open asks nothing.
  let sending = false

  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'hud', description: 'Open the Binnacle HUD. /hud narrow hide|strip sets what it does without room to dock' })
    await $.command.register({ name: 'log', description: 'Keep a thought in the Binnacle Log, from any surface, the phone included' })
    // Unasked, the pane waits undrawn below 144 columns (d.ts 2532-2533).
    void $.ui.open(pane)
    if ((await read($, draft)).some(s => typeof s === 'string')) await update($, draft, minted).catch(() => undefined)
    if ((await read($, failed)).some(s => typeof s === 'string')) await update($, failed, minted).catch(() => undefined)
    return next(e)
  })

  // Memory joins Claude Code's own `memory` section, which the full and the
  // short prompt both carry. A section of the mod's own is a prompt.compose
  // answer, and a changed one waits for the next compaction (probe, 2.1.325).
  // A section answer that breaks the cache goes out on the next turn.
  on('prompt.section', { name: 'memory' }, async ($, e, next) => {
    const out = await next(e)
    const snap = await read($, approved)
    return snap ? { text: [out.text, memoryText(snap)].filter(Boolean).join('\n\n'), breakPromptCache: true } : out
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
    return { text: saved === null ? 'Not kept, the save failed. The thought is shown in the HUD.' : saved ? 'Kept in the Log.' : 'Nothing kept.' }
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
    const said = statusOf(lines, snap)
    const status = said.text
    // A refusal is news only beside the lines it refused, and while they differ from what Claude has.
    const besideRefused = !!st.refusedLines && same(lines, st.refusedLines)
    const claudeHasThem = !said.send
    const refused = besideRefused && !claudeHasThem ? st.failed : ''

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
          <Text key={`mem-${r.id}`} wrap={inline ? 'truncate-end' : 'wrap'}><Text dimColor>{i + 1} </Text>{r.text}</Text>
        ))}
        {lines.length === 0 && quiet('No lines yet. Write one in the field, then press a to add it.')}
      </Box>
    )

    // --- log ---------------------------------------------------------------
    const thought = (t: Thought, i: number) => (
      <Box key={`log-${i}`} flexDirection="row" justifyContent="space-between">
        <Text wrap={inline ? 'truncate-end' : 'wrap'}><Text dimColor>{narrow ? '' : hhmm(t.at)}{t.from === 'phone' ? ' phone' : ''}  </Text>{t.text}</Text>
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
    const acts: Act[] = [
      ...(unsaved.some(f => f.id) ? [{ k: 'd', label: 'dismiss failed', run: () => void update($, failed, without(unsaved.flatMap(f => f.id ?? []))).catch(() => undefined) }] : []),
      ...(inline ? [toggle(1), toggle(2)] : []),
      ...(writing ? [{ k: 'a', label: 'to memory', run: () => addLine($, now) }] : []),
      ...(!writing && newest && lines.at(-1) !== newest ? [{ k: 'p', label: 'last thought to memory', run: () => void promote($, newest) }] : []),
      ...(showsMemory && lines.length && said.send ? [{ k: 's', label: 'send', run: press, primary: true }] : []),
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
      const parts = [`memory ${refused ? `Not sent. ${refused}` : status}`, `log ${thoughts.length}`]
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
        {memory}
        {log}
        {rail}
        {keyline}
      </Box>
    )
  })
}
