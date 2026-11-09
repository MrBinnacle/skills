import { expect, test } from 'claude-code/testing'

// The action row: every key the pane shows has a drawn button behind it, so
// no hotkey falls through to the main prompt; and a pending send never
// survives the ring moving away from it.

const ARMED = 10000
const RING = (r: 0 | 1 | 2) => r * 1000

const pane = (placement: 'dock' | 'inline', isFocused: boolean) => ({
  plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: {
    title: 'Binnacle', isFocused, bodyColumns: placement === 'dock' ? 46 : 90,
    placement, scroll: { offset: 0, bodyRows: placement === 'dock' ? 32 : 8 }, view: {},
  },
}) as const

const start = async ($: any, on: any, value: number, writes: number[] = [], typed = '', sets: Record<string, unknown[]> = {}) => {
  on('command.register', () => ({ value: { command: 'hud' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: { key: string }) => ({ value: e.key === 'typed' ? { value: typed, version: 1 }
    : e.key === 'log' ? { value: [], version: 1 }
    : { value: { shape: 'scene-2', value }, version: 1 } }))
  on('state.set', (_: unknown, e: { key: string; value: any }) => {
    if (e.key === 'scene') writes.push(e.value.value)
    ;(sets[e.key] ??= []).push(e.value)
    return { value: { isSet: true, version: 2 } }
  })
  on('ui.focus', () => ({ value: {} }))
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
}

const keys = async (ui: any) =>
  (await ui.findAll({ type: 'Button' })).map((b: { key?: string }) => b.key).filter((k: string) => k.startsWith('k-')).sort()

test('strip, ring on an engine stop: m w l are drawn, not just named', { options: { narrow: 'strip' } }, async ($, on) => {
  await start($, on, RING(0))
  const ui = await $.ui.mount(pane('inline', true))
  expect(await keys(ui)).toEqual(['k-l', 'k-m', 'k-w'])
})

test('dock, idle: no send key is drawn or named', async ($, on) => {
  await start($, on, RING(2))
  const ui = await $.ui.mount(pane('dock', true))
  expect(await keys(ui)).toEqual([])
  expect(JSON.stringify(await ui.drawn())).not.toMatch(/\bs send\b/)
})

test('dock, edited memory: send and diff are drawn', async ($, on) => {
  await start($, on, 3 + RING(2))
  const ui = await $.ui.mount(pane('dock', true))
  expect(await keys(ui)).toEqual(['k-s', 'k-v'])
})

test('dock, finding: quote and dismiss are drawn', async ($, on) => {
  await start($, on, 2 + RING(2))
  const ui = await $.ui.mount(pane('dock', true))
  expect(await keys(ui)).toEqual(['k-d', 'k-q'])
})

test('unfocused: no buttons, so no hotkeys to fall through', async ($, on) => {
  await start($, on, 3 + RING(2))
  const ui = await $.ui.mount(pane('dock', false))
  expect(await keys(ui)).toEqual([])
})

test('the field says Enter keeps the thought while it holds the keys', async ($, on) => {
  await start($, on, RING(1))
  const ui = await $.ui.mount(pane('dock', true))
  expect(JSON.stringify(await ui.drawn())).toContain('enter keeps it')
})

test('Enter in the field keeps the thought in the log and clears the field', async ($, on) => {
  const sets: Record<string, unknown[]> = {}
  await start($, on, RING(1), [], 'rerun the naive config', sets)
  await $.ui.mount(pane('dock', true))
  await $.ui.input({ plugin: 'binnacle-hud', key: 'thought', text: 'rerun the naive config' })
  const logged = sets.log as { text: string; from: string }[][]
  expect(logged).toHaveLength(1)
  expect(logged[0]!.map(t => [t.text, t.from])).toEqual([['rerun the naive config', 'terminal']])
  expect(sets.typed?.at(-1)).toBe('')
})

test('Enter on an empty field keeps nothing', async ($, on) => {
  const sets: Record<string, unknown[]> = {}
  await start($, on, RING(1), [], '', sets)
  await $.ui.mount(pane('dock', true))
  await $.ui.input({ plugin: 'binnacle-hud', key: 'thought', text: '   ' })
  expect(sets.log).toBeUndefined()
})

test('armed shows the question only while focused', async ($, on) => {
  await start($, on, 3 + RING(2) + ARMED)
  const focused = await $.ui.mount(pane('dock', true))
  expect(JSON.stringify(await focused.drawn())).toContain('send this memory?')
  await focused.unmount()
  const away = await $.ui.mount(pane('dock', false))
  expect(JSON.stringify(await away.drawn())).not.toContain('send this memory?')
})

const focusOn = (element: string | undefined) =>
  ({ component: 'Pane', requestId: 'binnacle-hud', plugin: element && 'binnacle-hud', element, origin: { kind: 'person' } }) as any

test('the ring moving to the field disarms a pending send', async ($, on) => {
  const writes: number[] = []
  await start($, on, 3 + RING(2) + ARMED, writes)
  await $.ui.focus(focusOn('thought'))
  expect(writes).toHaveLength(1)
  expect(writes[0]! >= ARMED).toBe(false)
})

test('the ring staying on send keeps it armed', async ($, on) => {
  const writes: number[] = []
  await start($, on, 3 + RING(2) + ARMED, writes)
  await $.ui.focus(focusOn('k-s'))
  expect(writes).toHaveLength(1)
  expect(writes[0]! >= ARMED).toBe(true)
})

// A click hands the ring to the first focusable element drawn, not to the
// autoFocus field (native, 2026-11-08), so the field must come before every key.
const fieldFirst = async (ui: any) => {
  const tree = JSON.stringify(await ui.drawn())
  const field = tree.indexOf('"thought"')
  const firstKey = tree.search(/"k-[a-z]"/)
  return field >= 0 && firstKey > field
}

test('strip: the field comes before the action keys', { options: { narrow: 'strip' } }, async ($, on) => {
  await start($, on, RING(0))
  expect(await fieldFirst(await $.ui.mount(pane('inline', true)))).toBe(true)
})

test('strip, log expanded: the field still comes first', { options: { narrow: 'strip' } }, async ($, on) => {
  await start($, on, 300 + RING(0))
  expect(await fieldFirst(await $.ui.mount(pane('inline', true)))).toBe(true)
})

test('dock, edited memory: the field comes before send and diff', async ($, on) => {
  await start($, on, 3 + RING(0))
  expect(await fieldFirst(await $.ui.mount(pane('dock', true)))).toBe(true)
})

const LONG = 'the quick brown fox jumps over the lazy dog and keeps running past the edge'
// The field holds the text as its value, so an echo is a second copy.
const echoed = async (ui: any, text: string) => JSON.stringify(await ui.drawn()).split(`"${text}"`).length > 2

test('dock: a thought too long for the field is shown whole above it', async ($, on) => {
  await start($, on, RING(1), [], LONG)
  expect(await echoed(await $.ui.mount(pane('dock', true)), LONG)).toBe(true)
})

test('dock: a short thought is not echoed', async ($, on) => {
  await start($, on, RING(1), [], 'short')
  expect(await echoed(await $.ui.mount(pane('dock', true)), 'short')).toBe(false)
})
