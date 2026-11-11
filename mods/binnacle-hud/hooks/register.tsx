import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, SessionAppendInput } from 'claude-code'
import type { Approved, Attached, Entry, Row, Saved, Thought, View } from '../types'

// Binnacle HUD. The mod does not send the Log to Claude; absence from later
// model requests is unverified. Memory holds a draft and the snapshot a confirmed Send
// gave Claude. Watch is still a preview with one sample finding.
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
const attached = atom({ plugin: 'binnacle-hud', key: 'attached' } as const, null as Attached | null)

type Finding = { text: string; why: string; source: string; age: string }
const FINDING: Finding = {
  text: 'Tests were skipped in the last run',
  why: 'The test step printed "skipped: 12" and exited 0, so the green result covers only 3 of 15 tests. The skip came from a missing fixture file, not a marker.',
  source: 'ysk',
  age: '1m',
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

// The compaction replay and the watcher match this exact text.
const memoryText = (snap: Approved) => [`Memory the operator approved at ${hhmm(snap.at)}:`, ...snap.lines].join('\n')

// Only a compaction that replayed this snapshot speaks for it.
const replayOf = (snap: Approved, att: Attached | null) => att?.approvedAt === snap.at ? att : null

export const statusOf = (lines: readonly string[], snap: Approved | null, att: Attached | null = null): string => {
  if (!snap) return 'Not sent.'
  const replay = replayOf(snap, att)
  const at = replay && hhmm(replay.at)
  return replay?.state === 'missing' ? `Not in Claude's context after the compaction at ${at}. Send again to restore it.`
    : replay && replay.state !== 'found' ? `Approved ${hhmm(snap.at)}. Not checked after the compaction at ${at}.`
    : !same(lines, snap.lines) ? `Changed since Send. Claude has the ${hhmm(snap.at)} version.`
    : replay ? `Re-attached after the compaction at ${at}.`
    : `In Claude's context since ${hhmm(snap.at)}.`
}

const textOf = (row: SessionAppendInput) => row.message.content.flatMap(b => b.type === 'text' ? [b.text] : []).join('\n')

// Rows a compaction installs are stored after every compact hook ran: the
// boundary first, then the summary and the rows hooks added (probe P6). A
// prompt or a response stored before the row means the row never arrived.
export const step = (att: Attached, row: SessionAppendInput): Attached =>
  att.state === 'waiting' && row.message.type === 'system' && row.message.name === 'compact_boundary' ? { ...att, state: 'checking' }
  : att.state !== 'checking' ? att
  : textOf(row) === att.text ? { ...att, state: 'found' }
  : row.door === 'prompt' || row.door === 'response' ? { ...att, state: 'missing' }
  : att

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

// The lines are frozen when Send is pressed: the question, the row and the
// snapshot all carry that one value, whatever the draft becomes meanwhile.
// The snapshot is written only after the append lands, so it always means
// Claude has those lines.
async function send($: EngineInterface): Promise<void> {
  const lines = entries(await read($, draft)).map(l => l.text)
  if (!lines.length) return
  const question = `Memory for Claude:\n${lines.map(l => `- ${l}`).join('\n')}\n\nGive Claude these ${lines.length} lines now?`
  const answer = await $.ui.ask(question, [SEND, NOT_NOW]).catch(() => NOT_NOW)
  if (answer !== SEND) return
  const at = await $.clock.now()
  const text = memoryText({ lines, at })
  const out = await $.session.append({ message: { type: 'user', content: [{ type: 'text', text }] } })
    .catch((err: unknown) => ({ deny: err instanceof Error ? err.message : String(err) }))
  // The append landed but the snapshot write can still fail. Then Claude has
  // the lines and the HUD must not say "Not sent."
  // A refused Send changes nothing Claude has, so it keeps the earlier notice.
  let unrecorded = 0
  if (!out.deny) await update($, approved, () => ({ lines, at })).catch(() => { unrecorded = at }) // overwrite: the Send that landed last is the one Claude read last
  await update($, view, v => ({ ...v, failed: out.deny ?? '', refusedLines: lines, unrecorded: out.deny ? v.unrecorded : unrecorded }))
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

  // Send approved replay (O7): after a main-conversation compaction, Claude
  // gets the snapshot again. `approved` is read after the summary, so a Send
  // that lands meanwhile is the one replayed. A precompute installs nothing.
  // shortcut: a Send whose record failed (view.unrecorded) is not replayed and its notice stays; store its lines if that failure is ever seen.
  on('session.compact', async ($, e, next) => {
    const out = await next(e)
    if (e.agentId || e.trigger === 'precompute' || !out.messages) return out
    const snap = await read($, approved)
    if (!snap) return out
    const text = memoryText(snap)
    const at = await $.clock.now()
    await update($, attached, () => ({ at, approvedAt: snap.at, text, state: 'waiting' as const })).catch(() => undefined)
    return out.messages.some(m => m.text === text) ? out
      : { ...out, messages: [...out.messages, { role: 'user' as const, text, toolUses: [] }] }
  })

  // Watches what the session stores, after every hook, to check the replay.
  on('session.append', async ($, e, next) => {
    const out = await next(e)
    const att = e.agentId ? null : await read($, attached)
    if (att && step(att, e) !== att) await update($, attached, now => now && step(now, e)).catch(() => undefined)
    return out
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
      const ring = e.element === undefined ? 0 : e.element === 'thought' ? 1 : 2
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
    const att = await read($, attached)
    const lost = !!snap && replayOf(snap, att)?.state === 'missing'
    const status = st.unrecorded
      ? `Claude has the lines sent at ${hhmm(st.unrecorded)}. The HUD could not record that Send.`
      : statusOf(lines, snap, att)
    // A refusal is news only beside the lines it refused, and while they differ from what Claude has.
    const besideRefused = !!st.refusedLines && same(lines, st.refusedLines)
    const claudeHasThem = !!snap && same(lines, snap.lines)
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
        {!(refused && !snap && !st.unrecorded) && (st.unrecorded || lost
          ? <Text wrap="wrap" color={TONE.warning}>{status}</Text>
          : <Text wrap="wrap" color={!snap ? undefined : same(lines, snap.lines) ? TONE.remember : LIGHT} dimColor={!snap}>{status}</Text>
        )}
        {refused && <Text wrap="wrap" color={TONE.warning}>{st.unrecorded ? `The later Send was refused: ${refused}` : `Not sent. ${refused}`}</Text>}
        {rows.map((r, i) => (
          <Text key={`mem-${r.id}`} wrap={inline ? 'truncate-end' : 'wrap'}><Text dimColor>{i + 1} </Text>{r.text}</Text>
        ))}
        {lines.length === 0 && quiet('No lines yet. Write one in the field, then press a to add it.')}
      </Box>
    )

    // --- watch -------------------------------------------------------------
    const watch = (
      <Box flexDirection="column">
        {header('Watch', 'preview')}
        <Box key="watch-0" flexDirection="column">
          <Box flexDirection="row">
            <Text color={LIGHT}>▎</Text>
            <Text wrap="truncate-end" hover={{ bold: true }}>{FINDING.text}</Text>
          </Box>
          <Text dimColor>▎{FINDING.source} · {FINDING.age}</Text>
          <Box position="absolute" top={2} left={1} width={w - 2} display="none" hover={{ display: 'flex' }}
            borderStyle="round" borderDimColor paddingX={1} flexDirection="column">
            <Text wrap="wrap">{FINDING.why}</Text>
          </Box>
        </Box>
        {quiet('Preview. Not connected to an observer yet.')}
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
    const toggle = (n: number): Act => ({ k: 'mwl'[n - 1]!, label: ['memory', 'watch', 'log'][n - 1]!,
      run: () => void update($, view, v => ({ ...v, expand: v.expand === n ? 0 : n })) })
    const press = () => {
      if (sending) return
      sending = true
      return send($).finally(() => { sending = false })
    }
    const acts: Act[] = [
      ...(unsaved.some(f => f.id) ? [{ k: 'd', label: 'dismiss failed', run: () => void update($, failed, without(unsaved.flatMap(f => f.id ?? []))).catch(() => undefined) }] : []),
      ...(inline ? [toggle(1), toggle(2), toggle(3)] : []),
      ...(writing ? [{ k: 'a', label: 'to memory', run: () => addLine($, now) }] : []),
      ...(!writing && newest && lines.at(-1) !== newest ? [{ k: 'p', label: 'last thought to memory', run: () => void promote($, newest) }] : []),
      ...(showsMemory && lines.length && (lost || !(snap && same(lines, snap.lines))) ? [{ k: 's', label: 'send', run: press, primary: true }] : []),
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
      const parts = [`memory ${refused ? (st.unrecorded ? `${status} The later Send was refused: ${refused}` : `Not sent. ${refused}`) : status}`, 'watch preview', `log ${thoughts.length}`]
      const section = st.expand === 1 ? memory : st.expand === 2 ? watch : st.expand === 3 ? log : null
      const hasField = !section || st.expand === 3
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
        {watch}
        {log}
        {rail}
        {keyline}
      </Box>
    )
  })
}
