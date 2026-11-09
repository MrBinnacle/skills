import { expect, test } from 'claude-code/testing'

// The action row: every key the pane shows has a drawn button behind it, so
// no hotkey falls through to the main prompt; and the key line follows the
// focus ring.

const pane = (placement: 'dock' | 'inline', isFocused: boolean) => ({
  plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: {
    title: 'Binnacle', isFocused, bodyColumns: placement === 'dock' ? 46 : 90,
    placement, scroll: { offset: 0, bodyRows: placement === 'dock' ? 32 : 8 }, view: {},
  },
}) as const

type Store = Record<string, any>
const view = (ring: 0 | 1 | 2, expand = 0) => ({ ring, expand, failed: '' })

const start = async ($: any, on: any, store: Store = {}) => {
  const versions: Record<string, number> = {}
  on('command.register', () => ({ value: { command: 'hud' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: { key: string }) => ({ value: { value: store[e.key], version: versions[e.key] ?? 0 } }))
  on('state.set', (_: unknown, e: { key: string; value: unknown }) => {
    store[e.key] = e.value
    versions[e.key] = (versions[e.key] ?? 0) + 1
    return { value: { isSet: true, version: versions[e.key] } }
  })
  on('ui.focus', () => ({ value: {} }))
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
}

const keys = async (ui: any) =>
  (await ui.findAll({ type: 'Button' })).map((b: { key?: string }) => b.key).filter((k: string) => k.startsWith('k-')).sort()
const shown = async (ui: any) => JSON.stringify(await ui.drawn())

test('strip, ring on an engine stop: m w l are drawn, not just named', { options: { narrow: 'strip' } }, async ($, on) => {
  await start($, on, { view: view(0) })
  const ui = await $.ui.mount(pane('inline', true))
  expect(await keys(ui)).toEqual(['k-l', 'k-m', 'k-w'])
})

test('dock, empty memory: no send key is drawn or named', async ($, on) => {
  await start($, on, { view: view(2) })
  const ui = await $.ui.mount(pane('dock', true))
  expect(await keys(ui)).toEqual([])
  expect(await shown(ui)).not.toMatch(/\bs send\b/)
})

test('dock, unsent memory: send and one remove key per line are drawn', async ($, on) => {
  await start($, on, { view: view(2), memory: ['ship slice 1', 'probe step 2 decides'] })
  const ui = await $.ui.mount(pane('dock', true))
  expect(await keys(ui)).toEqual(['k-1', 'k-2', 'k-s'])
})

test('dock, memory already in Claude\'s context: no send key', async ($, on) => {
  await start($, on, { view: view(2), memory: ['ship slice 1'], approved: { lines: ['ship slice 1'], at: 0 } })
  const ui = await $.ui.mount(pane('dock', true))
  expect(await keys(ui)).toEqual(['k-1'])
})

test('dock, text in the field: a adds it to memory, and no remove key competes', async ($, on) => {
  await start($, on, { view: view(2), memory: ['ship slice 1'], typed: 'model slice 2' })
  const ui = await $.ui.mount(pane('dock', true))
  expect(await keys(ui)).toEqual(['k-a', 'k-s'])
})

test('dock: Watch draws no buttons and says it is a preview', async ($, on) => {
  await start($, on, { view: view(2) })
  const ui = await $.ui.mount(pane('dock', true))
  expect(await keys(ui)).toEqual([])
  expect(await shown(ui)).toContain('Preview. Not connected to an observer yet.')
})

test('unfocused: no buttons, so no hotkeys to fall through', async ($, on) => {
  await start($, on, { view: view(2), memory: ['ship slice 1'] })
  const ui = await $.ui.mount(pane('dock', false))
  expect(await keys(ui)).toEqual([])
})

test('the field says Enter keeps the thought while it holds the keys', async ($, on) => {
  await start($, on, { view: view(1) })
  const ui = await $.ui.mount(pane('dock', true))
  expect(await shown(ui)).toContain('enter keeps it')
})

test('Enter in the field keeps the thought in the log and clears the field', async ($, on) => {
  const store: Store = { view: view(1), typed: 'rerun the naive config' }
  await start($, on, store)
  await $.ui.mount(pane('dock', true))
  await $.ui.input({ plugin: 'binnacle-hud', key: 'thought', text: 'rerun the naive config' })
  expect(store.log.map((t: { text: string; from: string }) => [t.text, t.from])).toEqual([['rerun the naive config', 'terminal']])
  expect(store.typed).toBe('')
})

test('dock: kept thoughts draw in the Log, and only the phone one is marked phone', async ($, on) => {
  const log = [
    { text: 'call the venue about the 14th', at: '2026-11-09T09:00:00.000Z', from: 'phone' },
    { text: 'rerun the naive config', at: '2026-11-09T09:05:00.000Z', from: 'terminal' },
  ]
  await start($, on, { view: view(1), log })
  const tree = await shown(await $.ui.mount(pane('dock', true)))
  expect(tree).toContain('2 kept')
  expect(tree).toContain('"call the venue about the 14th"')
  expect(tree).toContain('"rerun the naive config"')
  expect(tree.split('" phone"').length - 1).toBe(1)
  expect(tree.indexOf('" phone"')).toBeLessThan(tree.indexOf('"call the venue about the 14th"'))
})

test('Enter on an empty field keeps nothing', async ($, on) => {
  const store: Store = { view: view(1) }
  await start($, on, store)
  await $.ui.mount(pane('dock', true))
  await $.ui.input({ plugin: 'binnacle-hud', key: 'thought', text: '   ' })
  expect(store.log).toBeUndefined()
})

const focusOn = (element: string | undefined) =>
  ({ component: 'Pane', requestId: 'binnacle-hud', plugin: element && 'binnacle-hud', element, origin: { kind: 'person' } }) as any

test('the key line follows the ring: the field shows the Enter hint, a button does not', async ($, on) => {
  const store: Store = { memory: ['ship slice 1'] }
  await start($, on, store)
  await $.ui.focus(focusOn('thought'))
  expect(store.view.ring).toBe(1)
  let ui = await $.ui.mount(pane('dock', true))
  expect(await shown(ui)).toContain('enter keeps it')
  await ui.unmount()
  await $.ui.focus(focusOn('k-s'))
  expect(store.view.ring).toBe(2)
  ui = await $.ui.mount(pane('dock', true))
  expect(await shown(ui)).not.toContain('enter keeps it')
})

// A click hands the ring to the first focusable element drawn, not to the
// autoFocus field (native, 2026-11-08), so the field must come before every key.
const fieldFirst = async (ui: any) => {
  const tree = await shown(ui)
  const field = tree.indexOf('"thought"')
  const firstKey = tree.search(/"k-[a-z0-9]"/)
  return field >= 0 && firstKey > field
}

test('strip: the field comes before the action keys', { options: { narrow: 'strip' } }, async ($, on) => {
  await start($, on, { view: view(0) })
  expect(await fieldFirst(await $.ui.mount(pane('inline', true)))).toBe(true)
})

test('strip, log expanded: the field still comes first', { options: { narrow: 'strip' } }, async ($, on) => {
  await start($, on, { view: view(0, 3) })
  expect(await fieldFirst(await $.ui.mount(pane('inline', true)))).toBe(true)
})

test('dock, unsent memory: the field comes before send and the remove keys', async ($, on) => {
  await start($, on, { view: view(0), memory: ['ship slice 1', 'probe step 2 decides'] })
  expect(await fieldFirst(await $.ui.mount(pane('dock', true)))).toBe(true)
})

const LONG = 'the quick brown fox jumps over the lazy dog and keeps running past the edge'
// The field holds the text as its value, so an echo is a second copy.
const echoed = async (ui: any, text: string) => (await shown(ui)).split(`"${text}"`).length > 2

test('dock: a thought too long for the field is shown whole above it', async ($, on) => {
  await start($, on, { view: view(1), typed: LONG })
  expect(await echoed(await $.ui.mount(pane('dock', true)), LONG)).toBe(true)
})

test('dock: a short thought is not echoed', async ($, on) => {
  await start($, on, { view: view(1), typed: 'short' })
  expect(await echoed(await $.ui.mount(pane('dock', true)), 'short')).toBe(false)
})
