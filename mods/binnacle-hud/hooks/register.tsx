import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

// Design mock for sdlc/hud-design.md. Fixed sample data; nothing is saved or sent.
const PANE = 'binnacle-hud'
const scene = atom({ plugin: 'binnacle-hud', key: 'scene' } as const, 0, { shape: 'scene-1' })

type Item = { who: string; text: string; age: string; mark?: string }
type Scene = {
  name: string
  claude: string
  heading: { status: string; tone?: 'accent' | 'warning'; lines: Item[]; action?: string; empty?: string }
  watch: { status: string; items: Item[]; empty?: string }
  log: { status: string; items: Item[]; empty?: string; typing?: string }
}

const HEAD: Item[] = [
  { who: 'claude', text: 'Ship slice 1 of the continuity pane', age: '' },
  { who: 'you', text: 'Probe step 2 decides the design', age: '' },
]
const LOGGED: Item[] = [
  { who: 'you', text: 'Ask config where $.store lives on disk', age: '14:05' },
  { who: 'you', text: 'Check ctrl+x tab over a draft', age: '14:01' },
]

const SCENES: Scene[] = [
  { name: 'idle', claude: 'waiting for you',
    heading: { status: 'nothing sent', lines: [], empty: 'No heading sent. After compaction Claude keeps only the summary.' },
    watch: { status: 'quiet', items: [], empty: 'Nothing reported.' },
    log: { status: 'empty', items: [], empty: 'Type below; Enter saves. Nothing here reaches Claude.' } },
  { name: 'busy capture', claude: 'working · 2m',
    heading: { status: 'sent 14:02', lines: HEAD },
    watch: { status: 'quiet', items: [], empty: 'Nothing reported.' },
    log: { status: '2 saved', items: LOGGED, typing: 'remember to rerun the naive con' } },
  { name: 'finding', claude: 'working · 4m',
    heading: { status: 'sent 14:02', lines: HEAD },
    watch: { status: '1 new', items: [{ who: 'ysk', text: 'Tests were skipped in the last run', age: '1m' }] },
    log: { status: '2 saved', items: LOGGED } },
  { name: 'unsent edit', claude: 'waiting for you',
    heading: { status: '2 edits not sent', tone: 'accent', action: 'send',
      lines: [...HEAD, { who: 'claude', text: 'Model slice 2 before building it', age: '', mark: '~' }] },
    watch: { status: 'quiet', items: [], empty: 'Nothing reported.' },
    log: { status: '2 saved', items: LOGGED } },
  { name: 'replay failed', claude: 'waiting for you',
    heading: { status: 'not attached after 14:20 compaction', tone: 'warning', action: 'send again', lines: HEAD },
    watch: { status: 'quiet', items: [], empty: 'Nothing reported.' },
    log: { status: '2 saved', items: LOGGED } },
]

const WHO_SHORT: Record<string, string> = { you: 'y', claude: 'c', ysk: 'k', helper: 'h' }

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'hud', description: 'Design mock: open the Binnacle HUD' })
    return next(e)
  })

  on('command.run', { command: 'hud' }, async $ => {
    await $.ui.open({ id: PANE, title: 'Binnacle' })
    return { text: 'Binnacle HUD mock opened. Click it or press ctrl+x tab, then 1-5 to switch states.' }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button, Input } = $.ui.resolve(e)
    const s = SCENES[(await read($, scene)) % SCENES.length]
    const narrow = (e.viewport?.columns ?? 60) < 40

    const who = (w: string) => <Text dimColor>{(narrow ? WHO_SHORT[w] : w).padEnd(narrow ? 2 : 7)}</Text>
    const row = (it: Item) => (
      <Box flexDirection="row" justifyContent="space-between">
        <Text wrap="truncate-end">
          <Text color="warning">{it.mark ?? ' '}</Text>{who(it.who)}{it.text}
        </Text>
        {it.age !== '' && <Text dimColor> {it.age}</Text>}
      </Box>
    )
    const head = (name: string, status: string, tone?: 'accent' | 'warning') => (
      <Box flexDirection="row" justifyContent="space-between">
        <Text bold>{name}</Text>
        <Text color={tone === 'warning' ? 'warning' : tone === 'accent' ? 'claude' : undefined} dimColor={!tone}>
          {status}
        </Text>
      </Box>
    )
    const rule = <Text dimColor>{'─'.repeat(Math.max(10, (e.viewport?.columns ?? 44) - 4))}</Text>
    const empty = (t?: string) => t && <Text dimColor italic wrap="wrap">  {t}</Text>

    return (
      <Box flexDirection="column" paddingX={1}>
        <Box flexDirection="row" justifyContent="space-between">
          <Text bold color="claude">◆ BINNACLE</Text>
          <Text dimColor>Claude {s.claude}</Text>
        </Box>
        {rule}
        {head('HEADING', s.heading.status, s.heading.tone)}
        {s.heading.lines.map(row)}
        {empty(s.heading.empty)}
        {s.heading.action && (
          <Box flexDirection="row" gap={1}>
            <Button key="send" hotkey="s" variant="primary" onPress={() => {}}>{s.heading.action}</Button>
            <Button key="view" hotkey="v" plain dimColor onPress={() => {}}>view diff</Button>
          </Box>
        )}
        {rule}
        {head('WATCH', s.watch.status, s.watch.items.length ? 'accent' : undefined)}
        {s.watch.items.map(row)}
        {empty(s.watch.empty)}
        {s.watch.items.length > 0 && (
          <Box flexDirection="row" gap={1}>
            <Button key="quote" hotkey="q" plain onPress={() => {}}>quote</Button>
            <Button key="dismiss" hotkey="d" plain dimColor onPress={() => {}}>dismiss</Button>
          </Box>
        )}
        {rule}
        {head('LOG', s.log.status)}
        {s.log.items.map(row)}
        {empty(s.log.empty)}
        {rule}
        <Input key="thought" label="›" placeholder="a thought · Enter saves" value={s.log.typing ?? ''}
          onSubmit={() => {}} />
        <Box flexDirection="row" gap={1} marginTop={1}>
          {SCENES.map((one, i) => (
            <Button key={`scene-${i}`} hotkey={String(i + 1)} plain dimColor
              onPress={() => void update($, scene, () => i)}>{one.name}</Button>
          ))}
        </Box>
      </Box>
    )
  })
}
