import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'
import type { Thought } from '../types'

// Binnacle HUD, design 2 (Pi session, 2026-11-08). Memory and Watch are fixed
// sample data, nothing saved or sent. Real: the Log, the pane's placement
// (dock or inline), its width, whether it holds the keys, the focus ring, hover.
//
// Keys inside the pane (after /hud, ctrl+x tab or a click, then Tab off the
// field): the action row under the field is the whole list, built from what
// is on screen, so no key is shown that has no button. In the dock, 1-5 pick a
// preview scene from their own row at the bottom.
//
// State lives under keys types/index.d.ts declares: `scene`, a number packed
// as digits; `typed`, the field's text, echoed wrapped above it because the
// host's Input cuts a long line off at the edge (native, 2026-11-08); and
// `log`, the kept thoughts, newest last. None of it reaches the model.
const PANE = 'binnacle-hud'
const SEND = 'k-s' // the send button's key, as ui.focus names it
// $.ui.ask needs two labels; neither keeps anything.
const NOT_NOW = 'Not now'
const CANCEL = 'Cancel'
const packed = atom({ plugin: 'binnacle-hud', key: 'scene' } as const, 0, { shape: 'scene-2' })
const typed = atom({ plugin: 'binnacle-hud', key: 'typed' } as const, '')
const kept = atom({ plugin: 'binnacle-hud', key: 'log' } as const, [] as Thought[])
const failed = atom({ plugin: 'binnacle-hud', key: 'failed' } as const, '')
// Counts the field's edits, so a keep clears the field only when nobody typed
// while it saved. Text equality cannot tell a retyped draft from an untouched one.
let edits = 0

type Ring = 0 | 1 | 2 // 0 no element, 1 the thought field, 2 a button
type View = { scene: number; diff: boolean; expand: number; ring: Ring; armed: boolean }
const unpack = (v: number): View => ({
  scene: v % 10,
  diff: Math.floor(v / 10) % 10 === 1,
  expand: Math.floor(v / 100) % 10,
  ring: (Math.floor(v / 1000) % 10) as Ring,
  armed: Math.floor(v / 10000) % 10 === 1,
})
const pack = (s: View): number =>
  s.scene + (s.diff ? 10 : 0) + s.expand * 100 + s.ring * 1000 + (s.armed ? 10000 : 0)

type Line = { who: 'you' | 'claude'; text: string; changed?: boolean }
type Finding = { text: string; why: string; source: string; age: string; settled?: string }
type Scene = {
  name: string
  claude: string
  memory: { status: string; tone?: 'remember' | 'warning'; lines: Line[]; action?: string; empty?: string }
  watch: { status: string; items: Finding[]; empty?: string }
}

const MEMORY: Line[] = [
  { who: 'claude', text: 'Ship slice 1 of the continuity pane' },
  { who: 'you', text: 'Probe step 2 decides the design' },
]
const EDITED: Line[] = [
  MEMORY[0]!,
  { who: 'you', text: 'Probe step 2 decides the design; step 3 is the focus probe', changed: true },
  { who: 'claude', text: 'Model slice 2 before building it', changed: true },
]
const DIFF = [
  '@@ -1,2 +1,3 @@',
  ' Ship slice 1 of the continuity pane',
  '-Probe step 2 decides the design',
  '+Probe step 2 decides the design; step 3 is the focus probe',
  '+Model slice 2 before building it',
].join('\n')
const FINDING: Finding = {
  text: 'Tests were skipped in the last run',
  why: 'The test step printed "skipped: 12" and exited 0, so the green result covers only 3 of 15 tests. The skip came from a missing fixture file, not a marker.',
  source: 'ysk',
  age: '1m',
}

const SCENES: Scene[] = [
  { name: 'idle', claude: 'waiting for you',
    memory: { status: 'nothing sent', lines: [], empty: 'Nothing sent. After compaction Claude keeps only its summary.' },
    watch: { status: 'quiet', items: [], empty: 'Nothing reported.' } },
  { name: 'busy', claude: 'working · 2m',
    memory: { status: 'sent 14:02', tone: 'remember', lines: MEMORY },
    watch: { status: 'quiet', items: [], empty: 'Nothing reported.' } },
  { name: 'finding', claude: 'working · 4m',
    memory: { status: 'sent 14:02', tone: 'remember', lines: MEMORY },
    watch: { status: '1 new', items: [FINDING] } },
  { name: 'edited', claude: 'waiting for you',
    memory: { status: '2 lines changed since Send', lines: EDITED, action: 'send' },
    watch: { status: 'quiet', items: [{ ...FINDING, settled: 'answered on phone 14:07' }] } },
  { name: 'failed', claude: 'waiting for you',
    memory: { status: 'not attached · compaction 14:20', tone: 'warning', lines: MEMORY, action: 'send again' },
    watch: { status: 'quiet', items: [], empty: 'Nothing reported.' } },
]

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

// Appends in one update, so two quick keeps cannot overwrite each other.
async function keep($: EngineInterface, text: string, from: Thought['from']): Promise<boolean> {
  if (!text.trim()) return false
  await update($, kept, items => [...items, { text, at: new Date().toISOString(), from }])
  return true
}

// Clears the field after a keep, unless typing went on while the keep was
// saving. A keep that fails leaves the field alone and records the text it did
// not keep, so newer typing never hides the loss.
async function submit($: EngineInterface, text: string): Promise<void> {
  const at = edits
  const isKept = await keep($, text, 'terminal').catch(() => null)
  if (isKept === null) return void (await update($, failed, () => text).catch(() => undefined))
  if (!isKept) return
  await update($, failed, () => '').catch(() => undefined)
  await update($, typed, now => edits === at ? '' : now).catch(() => undefined)
}

export const register: Register = (on, options) => {
  const noDock = narrowOf(options.narrow)
  // rows is the inline height alone; a docked pane ignores it.
  const pane = { id: PANE, title: 'Binnacle', columns: 46, rows: noDock === 'hide' ? 1 : 8 }

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
    return { text: await keep($, answer, from) ? 'Kept in the Log.' : 'Nothing kept.' }
  })

  // Where the ring stands decides the key line. Any move but onto the send
  // button itself disarms a pending send, so leaving and coming back never
  // finds it armed: the site taking the keys again moves the ring to the field.
  on('ui.focus', async ($, e, next) => {
    if (e.component === 'Pane' && e.requestId === PANE) {
      const ring: Ring = e.element === undefined ? 0 : e.element === 'thought' ? 1 : 2
      const keep = e.element === SEND
      void update($, packed, v => { const u = unpack(v); return pack({ ...u, ring, armed: keep && u.armed }) }).catch(() => undefined)
    }
    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button, Input, Code } = $.ui.resolve(e)
    const st = unpack(await read($, packed))
    const now = await read($, typed)
    const lost = await read($, failed)
    const thoughts = await read($, kept)
    const s = SCENES[st.scene % SCENES.length] ?? SCENES[0]!
    const set = (patch: Partial<View>) => void update($, packed, v => pack({ ...unpack(v), ...patch }))

    const focused = e.props.isFocused
    const inline = e.props.placement === 'inline'
    const cols = e.props.bodyColumns
    const w = Math.max(20, cols - 2) // paddingX 1
    const narrow = w < 36
    // Buttons draw whenever the pane holds the keys: a hotkey whose button is
    // absent falls through to the main prompt. They fire only off the field.
    const armed = focused && st.armed

    // --- vocabulary -------------------------------------------------------
    const seg = Math.max(1, Math.floor(w * 0.08))
    const hairline = (
      <Box flexDirection="row">
        {MARK.map((c, i) => <Text key={`hl-${i}`} color={c}>{'─'.repeat(seg)}</Text>)}
        <Text dimColor>{'─'.repeat(Math.max(0, w - MARK.length * seg))}</Text>
      </Box>
    )
    const masthead = (
      <Box flexDirection="row" justifyContent="space-between">
        <Text bold><Text color={MARK[0]}>◆</Text> Binnacle <Text color={TONE.warning}>preview</Text></Text>
        <Text dimColor>{narrow ? s.claude.split(' ')[0] : s.claude}</Text>
      </Box>
    )
    const header = (label: string, status: string, tone?: 'remember' | 'warning' | 'claude') => (
      <Box flexDirection="row" justifyContent="space-between" marginTop={1}>
        <Text bold>{label}</Text>
        <Text color={tone && TONE[tone]} dimColor={!tone} wrap="truncate-start">{status}</Text>
      </Box>
    )
    const quiet = (t?: string) => (t ? <Text dimColor wrap="wrap">{t}</Text> : null)
    const key = (k: string, label: string, onPress: () => void, primary?: boolean) => (
      <Button key={`k-${k}`} hotkey={k} plain={primary ? undefined : true} dimColor={!primary}
        variant={primary ? 'primary' : undefined} onPress={onPress}>{label}</Button>
    )

    // --- memory ------------------------------------------------------------
    const memoryLine = (l: Line, i: number) => (
      <Box key={`mem-${i}`} flexDirection="row" justifyContent="space-between">
        <Text wrap="truncate-end">
          <Text dimColor>{l.changed ? '~ ' : '  '}</Text>{l.text}
        </Text>
        <Box display="none" hover={{ display: 'flex' }}><Text dimColor> {l.who}</Text></Box>
      </Box>
    )
    const memory = (
      <Box flexDirection="column">
        {header('Memory', s.memory.status, s.memory.tone)}
        {s.memory.tone === 'warning' && (
          <Box flexDirection="row"><Text color={TONE.warning}>▎</Text><Text dimColor wrap="wrap">Claude is working from the summary alone.</Text></Box>
        )}
        {st.diff && s.memory.action === 'send'
          ? <Code format="diff" source={DIFF} wrap="truncate-end" />
          : s.memory.lines.map(memoryLine)}
        {quiet(s.memory.empty)}
      </Box>
    )

    // --- watch -------------------------------------------------------------
    const finding = (f: Finding, i: number) => (
      <Box key={`watch-${i}`} flexDirection="column">
        <Box flexDirection="row">
          <Text color={f.settled ? undefined : LIGHT} dimColor={!!f.settled}>▎</Text>
          <Text wrap="truncate-end" dimColor={!!f.settled} hover={{ bold: true }}>{f.text}</Text>
        </Box>
        <Text dimColor>▎{f.source} · {f.age}{f.settled ? ` · ${f.settled}` : ''}</Text>
        <Box position="absolute" top={2} left={1} width={w - 2} display="none" hover={{ display: 'flex' }}
          borderStyle="round" borderDimColor paddingX={1} flexDirection="column">
          <Text wrap="wrap">{f.why}</Text>
          <Text dimColor>quote puts this in your prompt as data · nothing is sent</Text>
        </Box>
      </Box>
    )
    const watch = (
      <Box flexDirection="column">
        {header('Watch', s.watch.status, s.watch.items.some(f => !f.settled) ? 'claude' : undefined)}
        {s.watch.items.map(finding)}
        {quiet(s.watch.empty)}
      </Box>
    )

    // --- log ---------------------------------------------------------------
    const thought = (t: Thought, i: number) => (
      <Box key={`log-${i}`} flexDirection="row" justifyContent="space-between">
        <Text wrap={inline ? 'truncate-end' : 'wrap'}><Text dimColor>{narrow ? '' : new Date(t.at).toTimeString().slice(0, 5)}{t.from === 'phone' ? ' phone' : ''}  </Text>{t.text}</Text>
      </Box>
    )
    const shown = w - 12 // the field's width less its frame, label and Enter hint
    const field = (
      <Box flexDirection="column">
        {now.length > shown && <Text dimColor wrap="wrap">{now}</Text>}
        <Box borderStyle="round" borderColor={focused ? LIGHT : DRAB} paddingX={1}>
          <Input key="thought" label="›" placeholder="a thought for later" submitLabel="keep"
            value={now} autoFocus onSubmit={v => void submit($, v)}
            onInput={v => { edits += 1; void update($, typed, () => v).catch(() => undefined) }} />
        </Box>
      </Box>
    )
    const log = (
      <Box flexDirection="column" flexGrow={1} justifyContent="flex-end">
        {header('Log', thoughts.length ? `${thoughts.length} kept` : 'empty')}
        {thoughts.length === 0 && quiet('Nothing kept yet. The mod does not send the Log to Claude.')}
        {thoughts.map(thought)}
        {typeof lost === 'string' && lost && <Text color="warning" wrap="wrap">Not kept, the save failed: {lost}</Text>}
        {field}
      </Box>
    )

    // --- actions: one list, built from what is on screen -----------------
    // The row that shows a key is the row that holds its button. It follows
    // the field: a click hands the ring to the first focusable element drawn,
    // not to autoFocus (native, 2026-11-08). With no field shown it stays near
    // the top, inside the scroll window.
    type Act = { k: string; label: string; run: () => void; primary?: boolean }
    const live = s.watch.items.find(f => !f.settled)
    const showsMemory = !inline || st.expand === 1
    const showsFinding = live && (!inline || st.expand === 2 || st.expand === 0)
    const toggle = (n: number): Act => ({ k: 'mwl'[n - 1]!, label: ['memory', 'watch', 'log'][n - 1]!,
      run: () => set({ expand: st.expand === n ? 0 : n }) })
    const acts: Act[] = [
      ...(inline ? [toggle(1), toggle(2), toggle(3)] : []),
      ...(showsMemory && s.memory.action
        ? [armed ? { k: 's', label: 'yes, send', run: () => set({ armed: false, scene: 1, diff: false }), primary: true }
                 : { k: 's', label: s.memory.action, run: () => set({ armed: true }), primary: true }]
        : []),
      ...(showsMemory && s.memory.action === 'send' && !armed ? [{ k: 'v', label: st.diff ? 'lines' : 'diff', run: () => set({ diff: !st.diff }) }] : []),
      ...(showsFinding && !armed ? [{ k: 'q', label: 'quote', run: () => set({ scene: 1 }) }, { k: 'd', label: 'dismiss', run: () => set({ scene: 1 }) }] : []),
    ]
    const rail = focused && (
      <Box flexDirection="row" flexWrap="wrap" gap={1}>
        {armed && <Text color={LIGHT}>send this memory?</Text>}
        {acts.map(a => key(a.k, a.label, a.run, a.primary))}
        <Text dimColor>{armed ? 'esc no' : 'esc prompt'}</Text>
      </Box>
    )
    const hint = !focused ? '/hud or a click to write' : st.ring === 1 ? 'enter keeps it · tab to the actions' : undefined
    const keyline = hint && <Text dimColor wrap="truncate-end">{hint}</Text>
    const scenes = focused && (
      <Box flexDirection="row" flexWrap="wrap" gap={1} marginTop={1}>
        <Text dimColor>preview scene</Text>
        {SCENES.map((one, i) => (
          <Button key={`scene-${i}`} hotkey={String(i + 1)} plain dimColor={st.scene !== i}
            onPress={() => set({ scene: i, diff: false, armed: false })}>{one.name}</Button>
        ))}
      </Box>
    )

    // --- inline, hide: one line saying how to get the side panel ----------
    const why = inline && noDock === 'hide' ? whyNoDock(e.viewport?.isFullscreen, e.viewport?.columns) ?? 'is not available here' : undefined
    if (why) {
      return (
        <Box paddingX={1}>
          <Text wrap="truncate-end"><Text bold><Text color={MARK[0]}>◆</Text> Binnacle</Text><Text dimColor>  side panel {why} · or /hud narrow strip</Text></Text>
        </Box>
      )
    }

    // --- inline: summary, actions, the one thing that wants you, the field --
    if (inline) {
      const parts = [`memory ${s.memory.status}`, `watch ${s.watch.status}`, `log ${thoughts.length}`]
      const section = st.expand === 1 ? memory : st.expand === 2 ? watch : st.expand === 3 ? log : null
      const hasField = !section || st.expand === 3
      return (
        <Box flexDirection="column" paddingX={1}>
          <Box flexDirection="row" justifyContent="space-between">
            <Text wrap="truncate-end"><Text bold><Text color={MARK[0]}>◆</Text> Binnacle <Text color={TONE.warning}>preview</Text></Text><Text dimColor>  {parts.join(' · ')}</Text></Text>
            <Text dimColor> {s.claude}</Text>
          </Box>
          {!hasField && rail}
          {section ?? (live && finding(live, 0))}
          {!section && field}
          {hasField && rail}
          {keyline}
        </Box>
      )
    }

    // --- dock ---------------------------------------------------------------
    return (
      <Box flexDirection="column" paddingX={1} height={e.props.scroll.bodyRows}>
        {masthead}
        {hairline}
        {memory}
        {watch}
        {log}
        {rail}
        {keyline}
        {scenes}
      </Box>
    )
  })
}
