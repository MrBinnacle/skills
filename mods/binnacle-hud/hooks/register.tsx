import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

// Binnacle HUD, design 2 (Pi session, 2026-11-08). A drop-in replacement for
// mods/binnacle-hud/hooks/register.tsx: fixed sample data, nothing saved or
// sent. What is real in this mock: the pane's placement (dock or inline), its
// width, whether it holds the keys, where the focus ring stands, hover.
//
// Keys inside the pane (after ctrl+x tab or a click, then Tab off the field):
//   1-5 scenes · s send (press twice) · v diff · q quote · d dismiss
//   m / w / l expand a section while the pane sits inline above the prompt
//
// State lives under the one key CC's types/index.d.ts declares (`scene`, a
// number), packed as digits, so this file replaces register.tsx alone. The
// real mod declares its own keys.
const PANE = 'binnacle-hud'
const packed = atom({ plugin: 'binnacle-hud', key: 'scene' } as const, 0, { shape: 'scene-2' })

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
type Thought = { at: string; text: string }
type Scene = {
  name: string
  claude: string
  memory: { status: string; tone?: 'remember' | 'warning'; lines: Line[]; action?: string; empty?: string }
  watch: { status: string; items: Finding[]; empty?: string }
  log: { items: Thought[]; typing?: string }
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
const LOG: Thought[] = [
  { at: '14:01', text: 'Check ctrl+x tab over a draft' },
  { at: '14:05', text: 'Ask config where $.store lives on disk' },
  { at: '14:09', text: 'Rerun the naive config before slice 2' },
]
const FINDING: Finding = {
  text: 'Tests were skipped in the last run',
  why: 'The test step printed "skipped: 12" and exited 0, so the green result covers only 3 of 15 tests. The skip came from a missing fixture file, not a marker.',
  source: 'ysk',
  age: '1m',
}

const SCENES: Scene[] = [
  { name: 'idle', claude: 'waiting for you',
    memory: { status: 'nothing sent', lines: [], empty: 'Nothing sent. After compaction Claude keeps only its summary.' },
    watch: { status: 'quiet', items: [], empty: 'Nothing reported.' },
    log: { items: [] } },
  { name: 'busy', claude: 'working · 2m',
    memory: { status: 'sent 14:02', tone: 'remember', lines: MEMORY },
    watch: { status: 'quiet', items: [], empty: 'Nothing reported.' },
    log: { items: LOG, typing: 'remember to rerun the naive con' } },
  { name: 'finding', claude: 'working · 4m',
    memory: { status: 'sent 14:02', tone: 'remember', lines: MEMORY },
    watch: { status: '1 new', items: [FINDING] },
    log: { items: LOG } },
  { name: 'edited', claude: 'waiting for you',
    memory: { status: '2 lines changed since Send', lines: EDITED, action: 'send' },
    watch: { status: 'quiet', items: [{ ...FINDING, settled: 'answered on phone 14:07' }] },
    log: { items: LOG } },
  { name: 'failed', claude: 'waiting for you',
    memory: { status: 'not attached · compaction 14:20', tone: 'warning', lines: MEMORY, action: 'send again' },
    watch: { status: 'quiet', items: [], empty: 'Nothing reported.' },
    log: { items: LOG } },
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

export const register: Register = (on, options) => {
  const noDock = narrowOf(options.narrow)
  // rows is the inline height alone; a docked pane ignores it.
  const pane = { id: PANE, title: 'Binnacle', columns: 46, rows: noDock === 'hide' ? 1 : 7 }

  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'hud', description: 'Open the Binnacle HUD. /hud narrow hide|strip sets what it does without room to dock' })
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

  // Where the ring stands decides which keys the key line shows.
  on('ui.focus', async ($, e, next) => {
    if (e.component === 'Pane' && e.requestId === PANE) {
      const ring: Ring = e.element === undefined ? 0 : e.element === 'thought' ? 1 : 2
      void update($, packed, v => pack({ ...unpack(v), ring })).catch(() => undefined)
    }
    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button, Input, Code } = $.ui.resolve(e)
    const st = unpack(await read($, packed))
    const s = SCENES[st.scene % SCENES.length] ?? SCENES[0]!
    const set = (patch: Partial<View>) => void update($, packed, v => pack({ ...unpack(v), ...patch }))

    const focused = e.props.isFocused
    const inline = e.props.placement === 'inline'
    const cols = e.props.bodyColumns
    const w = Math.max(20, cols - 2) // paddingX 1
    const narrow = w < 36
    const hot = focused && st.ring === 2 // hotkeys fire only off the field (d.ts 5712-5714)

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
        <Text bold><Text color={MARK[0]}>◆</Text> Binnacle</Text>
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
        {hot && s.memory.action && (
          <Box flexDirection="row" gap={2}>
            {st.armed
              ? <Box flexDirection="row" gap={1}><Text color={LIGHT}>send?</Text>{key('s', 'yes', () => set({ armed: false, scene: 1, diff: false }), true)}<Text dimColor>esc: no</Text></Box>
              : key('s', s.memory.action, () => set({ armed: true }), true)}
            {s.memory.action === 'send' && key('v', st.diff ? 'lines' : 'diff', () => set({ diff: !st.diff }))}
          </Box>
        )}
      </Box>
    )

    // --- watch -------------------------------------------------------------
    const finding = (f: Finding, i: number) => (
      <Box key={`watch-${i}`} flexDirection="column">
        <Box flexDirection="row">
          <Text color={f.settled ? undefined : LIGHT} dimColor={!!f.settled}>▎</Text>
          <Text wrap="truncate-end" dimColor={!!f.settled} hover={{ bold: true }}>{f.text}</Text>
        </Box>
        <Box flexDirection="row" justifyContent="space-between">
          <Text dimColor>▎{f.source} · {f.age}{f.settled ? ` · ${f.settled}` : ''}</Text>
          {hot && !f.settled && (
            <Box flexDirection="row" gap={1}>
              {key('q', 'quote', () => set({ scene: 1 }))}
              {key('d', 'dismiss', () => set({ scene: 1 }))}
            </Box>
          )}
        </Box>
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
        <Text wrap="truncate-end">{narrow ? '  ' : <Text dimColor>{t.at}  </Text>}{t.text}</Text>
        <Box display="none" hover={{ display: 'flex' }} flexDirection="row" gap={1}>
          <Button key={`log-quote-${i}`} plain dimColor onPress={() => {}}>quote</Button>
          <Button key={`log-done-${i}`} plain dimColor onPress={() => {}}>done</Button>
        </Box>
      </Box>
    )
    const field = (
      <Box borderStyle="round" borderColor={focused ? LIGHT : DRAB} paddingX={1}>
        <Input key="thought" label="›" placeholder="a thought" submitLabel="save" value={s.log.typing} autoFocus
          onSubmit={() => {}} />
      </Box>
    )
    const log = (
      <Box flexDirection="column" flexGrow={1} justifyContent="flex-end">
        {header('Log', s.log.items.length ? `${s.log.items.length} saved` : 'empty')}
        {s.log.items.length === 0 && quiet('Type below; Enter saves here. Nothing in the log reaches Claude.')}
        {s.log.items.map(thought)}
        {field}
      </Box>
    )

    // --- key line: only the keys that can fire now -------------------------
    const keyline = (
      <Text dimColor wrap="truncate-end">
        {!focused ? '/hud or a click to write'
          : st.ring === 1 ? 'enter saves · tab actions · esc prompt'
          : inline ? 'm w l expand · esc prompt'
          : 's send · v diff · q quote · d dismiss · esc prompt'}
      </Text>
    )
    const scenes = (
      <Box flexDirection="row" gap={1}>
        <Text dimColor>mock</Text>
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

    // --- inline: one summary row, the one thing that wants you, the field ---
    if (inline) {
      const parts = [`memory ${s.memory.status}`, `watch ${s.watch.status}`, `log ${s.log.items.length}`]
      const section = st.expand === 1 ? memory : st.expand === 2 ? watch : st.expand === 3 ? log : null
      const live = s.watch.items.find(f => !f.settled)
      return (
        <Box flexDirection="column" paddingX={1}>
          <Box flexDirection="row" justifyContent="space-between">
            <Text wrap="truncate-end"><Text bold><Text color={MARK[0]}>◆</Text> Binnacle</Text><Text dimColor>  {parts.join(' · ')}</Text></Text>
            <Text dimColor> {s.claude}</Text>
          </Box>
          {section ?? (live && finding(live, 0))}
          {!section && field}
          <Box flexDirection="row" justifyContent="space-between">
            {keyline}
            {hot && (
              <Box flexDirection="row" gap={1}>
                {key('m', 'memory', () => set({ expand: st.expand === 1 ? 0 : 1 }))}
                {key('w', 'watch', () => set({ expand: st.expand === 2 ? 0 : 2 }))}
                {key('l', 'log', () => set({ expand: st.expand === 3 ? 0 : 3 }))}
              </Box>
            )}
          </Box>
          {hot && scenes}
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
        <Box flexDirection="row" justifyContent="space-between" marginTop={1}>
          {keyline}
          {hot && scenes}
        </Box>
      </Box>
    )
  })
}
