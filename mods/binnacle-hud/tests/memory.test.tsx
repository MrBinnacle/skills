import { expect, mock, test } from 'claude-code/testing'

// Memory: the draft and the approved snapshot are two values, and only a
// confirmed Send gives Claude the lines. A snapshot means its append landed.

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

const start = async ($: any, on: any, store: Store, ask: Ask = () => 'Send', asked: string[] = []) => {
  const versions: Record<string, number> = {}
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: { key: string }) => ({ value: { value: store[e.key], version: versions[e.key] ?? 0 } }))
  on('state.set', (_: unknown, e: { key: string; value: unknown }) => {
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
const rowText = (row: any) => row.message.content[0].text as string

for (const answer of ['Not now', 'yes please']) {
  test(`Send answered "${answer}" approves nothing and appends nothing`, async ($, on) => {
    const store: Store = { memory: ['ship slice 1', 'probe step 2 decides'] }
    const session = mock.session(on)
    await start($, on, store, () => answer)
    const ui = await $.ui.mount(pane())
    await ui.press({ key: 'k-s' })
    expect(store.approved ?? null).toBeNull()
    expect(session.appended()).toHaveLength(0)
    expect(await shown(ui)).toContain('Not sent.')
  })
}

test('Send and yes appends one row of exactly the draft lines, then approves them', async ($, on) => {
  const store: Store = { memory: ['ship slice 1', 'probe step 2 decides'] }
  const session = mock.session(on)
  const asked: string[] = []
  await start($, on, store, () => 'Send', asked)
  const ui = await $.ui.mount(pane())
  await ui.press({ key: 'k-s' })
  expect(asked[0]).toContain('ship slice 1')
  expect(session.appended()).toHaveLength(1)
  expect(rowText(session.appended()[0])).toBe(`Memory the operator approved at ${hhmm(NOW)}:\nship slice 1\nprobe step 2 decides`)
  expect(store.approved).toEqual({ lines: ['ship slice 1', 'probe step 2 decides'], at: NOW })
  expect(await shown(await redraw($, ui))).toContain(`In Claude's context since ${hhmm(NOW)}.`)
})

test('an edit after Send leaves the approved snapshot and says Claude has the old version', async ($, on) => {
  const store: Store = { memory: ['ship slice 1', 'probe step 2 decides'] }
  mock.session(on)
  await start($, on, store)
  let ui = await $.ui.mount(pane())
  await ui.press({ key: 'k-s' })
  ui = await redraw($, ui)
  await ui.press({ key: 'k-1' })
  store.typed = 'model slice 2 first'
  ui = await redraw($, ui)
  await ui.press({ key: 'k-a' })
  expect(store.memory).toEqual(['probe step 2 decides', 'model slice 2 first'])
  expect(store.approved).toEqual({ lines: ['ship slice 1', 'probe step 2 decides'], at: NOW })
  expect(await shown(await redraw($, ui))).toContain(`Changed since Send. Claude has the ${hhmm(NOW)} version.`)
})

test('an edit during the confirmation does not change what is sent', async ($, on) => {
  const store: Store = { memory: ['ship slice 1'] }
  const session = mock.session(on)
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
  expect(session.appended()).toHaveLength(1)
  expect(rowText(session.appended()[0])).toBe(`Memory the operator approved at ${hhmm(NOW)}:\nship slice 1`)
  expect(store.approved).toEqual({ lines: ['ship slice 1'], at: NOW })
  expect(await shown(await redraw($, ui))).toContain('Changed since Send.')
})

test('a second Send while the confirmation is open asks nothing more', async ($, on) => {
  const store: Store = { memory: ['ship slice 1'] }
  const session = mock.session(on)
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
  expect(session.appended()).toHaveLength(1)
})

test('a refused append keeps the earlier snapshot and says why in words', async ($, on) => {
  const earlier = { lines: ['ship slice 1'], at: NOW - 3_600_000 }
  const store: Store = { memory: ['ship slice 1', 'new line'], approved: earlier }
  on('session.append', { door: 'note' }, () => ({ deny: 'policy says no' }))
  await start($, on, store)
  const ui = await $.ui.mount(pane())
  await ui.press({ key: 'k-s' })
  expect(store.approved).toEqual(earlier)
  expect(await shown(await redraw($, ui))).toContain('Not sent. policy says no')
})

test('a refused append with nothing approved before approves nothing', async ($, on) => {
  const store: Store = { memory: ['ship slice 1'] }
  on('session.append', { door: 'note' }, () => ({ deny: 'policy says no' }))
  await start($, on, store)
  const ui = await $.ui.mount(pane())
  await ui.press({ key: 'k-s' })
  expect(store.approved ?? null).toBeNull()
  expect(await shown(await redraw($, ui))).toContain('Not sent. policy says no')
})

test('a Log keep never touches Memory and never appends', async ($, on) => {
  const approved = { lines: ['ship slice 1'], at: NOW }
  const store: Store = { memory: ['ship slice 1'], approved }
  const session = mock.session(on)
  await start($, on, store)
  await $.ui.mount(pane())
  await $.ui.input({ plugin: 'binnacle-hud', key: 'thought', text: 'call the venue' })
  expect(store.log.map((t: { text: string }) => t.text)).toEqual(['call the venue'])
  expect(store.memory).toEqual(['ship slice 1'])
  expect(store.approved).toEqual(approved)
  expect(session.appended()).toHaveLength(0)
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
  expect(store.memory).toEqual(['ship slice 1'])
  expect(store.typed).toBe('')
})
