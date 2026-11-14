import { expect, mock, test } from 'claude-code/testing'

// Memory: the draft and the approved snapshot are two values, and only a
// confirmed Send gives Claude the lines. Claude reads the snapshot.

const NOW = Date.UTC(2026, 10, 9, 14, 2)
const hhmm = (ms: number) => new Date(ms).toTimeString().slice(0, 5)

const pane = (placement: 'dock' | 'inline' = 'dock') => ({
  plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: {
    title: 'Binnacle', isFocused: true, bodyColumns: placement === 'dock' ? 46 : 90,
    placement, scroll: { offset: 0, bodyRows: 32 }, view: {},
  },
}) as const

type Store = Record<string, any>
type Ask = (question: string) => string | Promise<string>

const start = async ($: any, on: any, store: Store, ask: Ask = () => 'Send', asked: string[] = [], refusal = '') => {
  const versions: Record<string, number> = {}
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: { key: string }) => ({ value: { value: store[e.key], version: versions[e.key] ?? 0 } }))
  on('state.set', (_: unknown, e: { key: string; value: unknown }) => {
    if (refusal && e.key === 'approved') return { deny: refusal }
    store[e.key] = e.value
    versions[e.key] = (versions[e.key] ?? 0) + 1
    return { value: { isSet: true, version: versions[e.key] } }
  })
  on('ui.focus', () => ({ value: {} }))
  on('tool.call', async (_: unknown, e: any) => {
    const question = e.questions[0].question
    asked.push(question)
    return { result: { answers: { [question]: await ask(question) } } }
  })
  mock.clock(on, { now: NOW })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
}

const shown = async (ui: any) => JSON.stringify(await ui.drawn())
// The kit redraws on its own state, not on this file's store, so a test
// reads a change by drawing the pane again.
const redraw = async ($: any, ui: any, placement: 'dock' | 'inline' = 'dock') => { await ui.unmount(); return $.ui.mount(pane(placement)) }
// Lets a held press reach the question before the test answers it.
const until = async (ui: any, ok: () => boolean) => { for (let i = 0; i < 50 && !ok(); i++) await ui.drawn() }

for (const answer of ['Not now', 'yes please']) {
  test(`Send answered "${answer}" approves nothing`, async ($, on) => {
    const store: Store = { memory: ['ship slice 1', 'probe step 2 decides'] }
    await start($, on, store, () => answer)
    const ui = await $.ui.mount(pane())
    await ui.press({ key: 'k-s' })
    expect(store.approved ?? null).toBeNull()
    expect(await shown(ui)).toContain('Not sent.')
  })
}

test('Send and yes approves exactly the draft lines, and adds no conversation row', async ($, on) => {
  const store: Store = { memory: ['ship slice 1', 'probe step 2 decides'] }
  const session = mock.session(on)
  const asked: string[] = []
  await start($, on, store, () => 'Send', asked)
  const ui = await $.ui.mount(pane())
  await ui.press({ key: 'k-s' })
  expect(asked[0]).toContain('ship slice 1')
  expect(session.appended()).toHaveLength(0)
  expect(store.approved).toEqual({ lines: ['ship slice 1', 'probe step 2 decides'], at: NOW })
  expect(await shown(await redraw($, ui))).toContain(`Sent at ${hhmm(NOW)}. Not yet in Claude's instructions.`)
})

test('an edit after Send leaves the approved snapshot and says the lines changed', async ($, on) => {
  const store: Store = { memory: ['ship slice 1', 'probe step 2 decides'] }
  await start($, on, store)
  let ui = await $.ui.mount(pane())
  await ui.press({ key: 'k-s' })
  ui = await redraw($, ui)
  await ui.press({ key: 'k-1' })
  store.typed = 'model slice 2 first'
  ui = await redraw($, ui)
  await ui.press({ key: 'k-a' })
  expect(store.memory.map((e: any) => e.text)).toEqual(['probe step 2 decides', 'model slice 2 first'])
  expect(store.approved).toEqual({ lines: ['ship slice 1', 'probe step 2 decides'], at: NOW })
  expect(await shown(await redraw($, ui))).toContain(`Changed since Send. The ${hhmm(NOW)} version is not yet in Claude's instructions.`)
})

test('an edit during the confirmation does not change what is sent', async ($, on) => {
  const store: Store = { memory: ['ship slice 1'] }
  const asked: string[] = []
  let release = (_: string) => {}
  await start($, on, store, () => new Promise<string>(r => { release = r }), asked)
  const ui = await $.ui.mount(pane())
  const sending = ui.press({ key: 'k-s' })
  await until(ui, () => asked.length > 0)
  expect(asked[0]).toContain('- ship slice 1')
  store.memory = ['ship slice 1', 'added while asked']
  release('Send')
  await sending
  expect(store.approved).toEqual({ lines: ['ship slice 1'], at: NOW })
  expect(await shown(await redraw($, ui))).toContain('Changed since Send.')
})

test('a second Send while the confirmation is open asks nothing more', async ($, on) => {
  const store: Store = { memory: ['ship slice 1'] }
  const asked: string[] = []
  const releases: ((answer: string) => void)[] = []
  await start($, on, store, () => new Promise<string>(r => { releases.push(r) }), asked)
  const ui = await $.ui.mount(pane())
  const first = ui.press({ key: 'k-s' })
  await until(ui, () => asked.length > 0)
  const second = ui.press({ key: 'k-s' })
  await until(ui, () => asked.length > 1)
  releases.forEach(release => release('Send'))
  await Promise.all([first, second])
  expect(asked).toHaveLength(1)
  expect(store.approved).toEqual({ lines: ['ship slice 1'], at: NOW })
})

test('a refused Send keeps the earlier snapshot and says why in words', async ($, on) => {
  const earlier = { lines: ['ship slice 1'], at: NOW - 3_600_000 }
  const store: Store = { memory: ['ship slice 1', 'new line'], approved: earlier }
  await start($, on, store, () => 'Send', [], 'policy says no')
  const ui = await $.ui.mount(pane())
  await ui.press({ key: 'k-s' })
  expect(store.approved).toEqual(earlier)
  const text = await shown(await redraw($, ui))
  expect(text).toContain('policy says no')
  expect(text).toContain(`Changed since Send. The ${hhmm(earlier.at)} version is not yet in Claude's instructions.`)
})

test('a refused Send with nothing approved before approves nothing', async ($, on) => {
  const store: Store = { memory: ['ship slice 1'] }
  await start($, on, store, () => 'Send', [], 'policy says no')
  const ui = await $.ui.mount(pane())
  await ui.press({ key: 'k-s' })
  expect(store.approved ?? null).toBeNull()
  expect(await shown(await redraw($, ui))).toContain('policy says no')
})

test('a Log keep never touches Memory', async ($, on) => {
  const approved = { lines: ['ship slice 1'], at: NOW }
  const store: Store = { memory: ['ship slice 1'], approved }
  await start($, on, store)
  const memory = store.memory
  await $.ui.mount(pane())
  await $.ui.input({ plugin: 'binnacle-hud', key: 'thought', text: 'call the venue' })
  expect(store.log.map((t: { text: string }) => t.text)).toEqual(['call the venue'])
  expect(store.memory).toEqual(memory)
  expect(store.approved).toEqual(approved)
})

test('nothing sent yet reads Not sent., and the strip says it in words too', { options: { narrow: 'strip' } }, async ($, on) => {
  await start($, on, { memory: ['ship slice 1'] })
  expect(await shown(await $.ui.mount(pane('inline')))).toContain('Not sent.')
})

test('a is offered only with text in the field, and adds it as a line', async ($, on) => {
  const store: Store = { memory: [] }
  await start($, on, store)
  const ui = await $.ui.mount(pane())
  expect(await ui.find({ key: 'k-a' })).toBeUndefined()
  await ui.unmount()
  store.typed = 'ship slice 1'
  const again = await $.ui.mount(pane())
  await again.press({ key: 'k-a' })
  expect(store.memory.map((e: any) => e.text)).toEqual(['ship slice 1'])
  expect(store.typed).toBe('')
})

// Enter keeps a thought in the Log, so a Memory line typed by habit lands
// there. p copies the newest Log thought into Memory, so nothing is retyped.
const thought = (text: string) => ({ text, at: '2026-11-09T14:00:00.000Z', from: 'terminal' })

test('p copies the newest Log thought into Memory and keeps it in the Log', async ($, on) => {
  const store: Store = { memory: [], log: [thought('older'), thought('ship slice 1')], typed: '' }
  await start($, on, store)
  const ui = await $.ui.mount(pane())
  await ui.press({ key: 'k-p' })
  expect(store.memory.map((e: any) => e.text)).toEqual(['ship slice 1'])
  expect(store.log.map((t: any) => t.text)).toEqual(['older', 'ship slice 1'])
  expect(store.approved).toBeUndefined()
})

test('p is not offered when the newest Log thought is already a Memory line', async ($, on) => {
  const store: Store = { memory: ['ship slice 1'], log: [thought('ship slice 1')], typed: '' }
  await start($, on, store)
  const ui = await $.ui.mount(pane())
  expect(await shown(ui)).not.toContain('"k-p"')
})

