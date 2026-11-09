import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'
import type { Approved, Lost, Thought, View } from '../types'

// Binnacle HUD. The mod does not send the Log to Claude; absence from later
// model requests is unverified. Memory holds a draft and the snapshot a confirmed Send
// gave Claude. Watch is still a preview with one sample finding.
//
// Keys inside the pane (after /hud, ctrl+x tab or a click, then Tab off the
// field): the action row under the field is the whole list, built from what
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
const failed = atom({ plugin: 'binnacle-hud', key: 'failed' } as const, [] as string[])
// Counts edits for both capture actions: equality cannot identify a retyped draft.
let edits = 0
const draft = atom({ plugin: 'binnacle-hud', key: 'memory' } as const, [] as string[])
const approved = atom({ plugin: 'binnacle-hud', key: 'approved' } as const, null as Approved | null)
const view = atom({ plugin: 'binnacle-hud', key: 'view' } as const, { ring: 0, expand: 0, failed: '' } as View)

// The draft shadow. `box` is the prompt box as the newest edit or change left
// it, held in module memory, so no other plugin can read a draft that was
// never cleared. Only a cleared draft goes to session state. A process kill
// loses both. Each box event takes the next number in `moves` when it
// arrives, so an event that finishes late cannot overwrite a newer one, and a
// submit can tell the clear it caused from a clear after more typing.
let box = ''
let moves = 0
let applied = 0
let lossAt = 0
let sentAt = -1
let lossWrite: Promise<void> = Promise.resolve()
const lost = atom({ plugin: 'binnacle-hud', key: 'lost' } as const, null as Lost | null)

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

export const statusOf = (lines: readonly string[], snap: Approved | null): string =>
  !snap ? 'Not sent.'
  : same(lines, snap.lines) ? `In Claude's context since ${hhmm(snap.at)}.`
  : `Changed since Send. Claude has the ${hhmm(snap.at)} version.`

// Appends in one update, so two quick keeps cannot overwrite each other.
async function keep($: EngineInterface, text: string, from: Thought['from']): Promise<boolean | null> {
  if (!text.trim()) return false
  try {
    await update($, kept, items => [...items, { text, at: new Date().toISOString(), from }])
    return true
  } catch {
    await update($, failed, items => [...items, text]).catch(() => undefined)
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

async function addLine($: EngineInterface): Promise<void> {
  const at = edits
  const text = await read($, typed)
  if (!text.trim()) return
  await update($, draft, lines => [...lines, text.trim()])
  await clearDraft($, text, at)
}

// Enter keeps a thought in the Log, so a line meant for Memory can land
// there by habit. This copies the newest Log thought into Memory; the Log keeps it.
async function promote($: EngineInterface): Promise<void> {
  const last = (await read($, kept)).at(-1)?.text
  if (last) await update($, draft, lines => lines.at(-1) === last ? lines : [...lines, last])
}

async function removeLine($: EngineInterface, at: number): Promise<void> {
  await update($, draft, lines => lines.filter((_, i) => i !== at))
}

// The lines are frozen when Send is pressed: the question, the row and the
// snapshot all carry that one value, whatever the draft becomes meanwhile.
// The snapshot is written only after the append lands, so it always means
// Claude has those lines.
async function send($: EngineInterface): Promise<void> {
  const lines = [...await read($, draft)]
  if (!lines.length) return
  const question = `Memory for Claude:\n${lines.map(l => `- ${l}`).join('\n')}\n\nGive Claude these ${lines.length} lines now?`
  const answer = await $.ui.ask(question, [SEND, NOT_NOW]).catch(() => NOT_NOW)
  if (answer !== SEND) return
  const at = await $.clock.now()
  const text = [`Memory the operator approved at ${hhmm(at)}:`, ...lines].join('\n')
  const out = await $.session.append({ message: { type: 'user', content: [{ type: 'text', text }] } })
    .catch((err: unknown) => ({ deny: err instanceof Error ? err.message : String(err) }))
  if (!out.deny) await update($, approved, () => ({ lines, at }))
  await update($, view, v => ({ ...v, failed: out.deny ?? '' }))
}

// A submit sets `sentAt` to the newest event number. That is this clear's
// own number when the submit came while this clear was still on its way in,
// and the number before it when the submit came first.
// Applies one change to the box. A clear that empties a draft nobody
// submitted keeps the draft as lost. A stash or recall that brings the lost
// text back drops it. A keystroke touches no state.
async function boxChanged($: EngineInterface, text: string, kind: string, seen: number): Promise<void> {
  if (seen < applied) return
  applied = seen
  const before = box
  box = text
  if (kind === 'clear' && sentAt !== seen - 1 && sentAt !== seen && before.trim() && !before.startsWith('/') && text !== before) {
    lossAt = seen
    // Assigned before any await, so a submit arriving right after this clear
    // waits for this write and then drops it (live order on 2.1.321).
    lossWrite = keepLoss($, before, seen)
    await lossWrite
  } else if (kind !== 'edit' && text && (await read($, lost).catch(() => null))?.text === text) {
    await update($, lost, now => now && now.text === text ? null : now).catch(() => undefined)
  }
}

async function keepLoss($: EngineInterface, before: string, seen: number): Promise<void> {
  const rec = { text: before, at: await $.clock.now(), moves: seen }
  // On a retry, a newer clear's draft wins.
  await update($, lost, now => lossAt === seen ? rec : now).catch(() => undefined)
}

// The person submitted. When the clear came first, that clear was the submit,
// so its loss, written or still being written, is dropped.
async function submitted($: EngineInterface): Promise<void> {
  const at = sentAt = moves
  await lossWrite
  await update($, lost, now => now && now.moves === at ? null : now).catch(() => undefined)
}

// Copies the cleared draft for the person to paste. It never writes the
// prompt box: prompt.fill has no "only if still empty" form, so a fill in
// flight could mix into text typed meanwhile (live repro, review of d372767).
async function copyLost($: EngineInterface, rec: Lost): Promise<void> {
  const out = await $.ui.copy({ text: rec.text }).catch(() => null)
  const restoring = out?.isCopied ? 'Copied. Paste it into the prompt with Ctrl+V.'
    : `Not copied${out && !out.isCopied ? `: ${out.reason}` : ''}.`
  await update($, view, v => ({ ...v, restoring })).catch(() => undefined)
}

async function forgetLost($: EngineInterface, rec: Lost): Promise<void> {
  await update($, lost, cur => cur && cur.at === rec.at && cur.moves === rec.moves ? null : cur).catch(() => undefined)
  await update($, view, v => ({ ...v, restoring: '' })).catch(() => undefined)
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
    return next(e)
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

  // Each event takes its number on arrival, before the chain below can delay it.
  on('prompt.edit', async ($, e, next) => {
    const seen = ++moves
    const out = await next(e)
    if (typeof out?.text === 'string') await boxChanged($, out.text, 'edit', seen)
    return out
  })

  on('prompt.change', async ($, e, next) => {
    const seen = ++moves
    const out = await next(e)
    await boxChanged($, e.text, e.origin.kind, seen)
    return out
  })

  on('prompt.submit', async ($, e, next) => {
    if (e.origin.kind === 'composer') await submitted($)
    return next(e)
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
    const unsaved = await read($, failed)
    const gone = await read($, lost)
    const thoughts = await read($, kept)
    const lines = await read($, draft)
    const snap = await read($, approved)
    const status = statusOf(lines, snap)

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
        {!(st.failed && !snap) && (
          <Text wrap="wrap" color={!snap ? undefined : same(lines, snap.lines) ? TONE.remember : LIGHT} dimColor={!snap}>{status}</Text>
        )}
        {st.failed && <Text wrap="wrap" color={TONE.warning}>{`Not sent. ${st.failed}`}</Text>}
        {lines.map((l, i) => (
          <Text key={`mem-${i}`} wrap={inline ? 'truncate-end' : 'wrap'}><Text dimColor>{i + 1} </Text>{l}</Text>
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
        {gone && <Text color={LIGHT} wrap="truncate-end">Last cleared draft {hhmm(gone.at)} · {gone.text.length} chars: {gone.text}</Text>}
        {gone && st.restoring && <Text dimColor wrap="wrap">{st.restoring}</Text>}
        {unsaved.map((text, i) => <Text key={`failed-${i}`} color="warning" wrap="wrap">Not kept, the save failed: {text}</Text>)}
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
      ...(gone ? [{ k: 'c', label: 'copy draft', run: () => void copyLost($, gone) }, { k: 'x', label: 'forget draft', run: () => void forgetLost($, gone) }] : []),
      ...(inline ? [toggle(1), toggle(2), toggle(3)] : []),
      ...(writing ? [{ k: 'a', label: 'to memory', run: () => addLine($) }] : []),
      ...(!writing && newest && lines.at(-1) !== newest ? [{ k: 'p', label: 'last thought to memory', run: () => void promote($) }] : []),
      ...(showsMemory && lines.length && !(snap && same(lines, snap.lines)) ? [{ k: 's', label: 'send', run: press, primary: true }] : []),
      // shortcut: lines past the ninth have only 0, which removes the last one; add paging if Memory grows that long.
      ...(showsMemory && !writing ? lines.slice(0, 9).map((_, i) => ({ k: String(i + 1), label: 'remove', run: () => void removeLine($, i) })) : []),
      ...(showsMemory && !writing && lines.length > 9 ? [{ k: '0', label: 'remove last', run: () => void removeLine($, lines.length - 1) }] : []),
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
      const parts = [`memory ${st.failed ? `Not sent. ${st.failed}` : status}`, 'watch preview', `log ${thoughts.length}`]
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
