import { expect, mock, test } from 'claude-code/testing'

// Regression probes from the #660 review, through the drawn handlers.
const NOW = Date.UTC(2026, 10, 9, 14, 2)
const pane = () => ({
  plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: { title: 'Binnacle', isFocused: true, bodyColumns: 46, placement: 'dock', scroll: { offset: 0, bodyRows: 32 }, view: {} },
}) as const
const deferred = () => { let resolve: (v?: any) => void = () => {}; const promise = new Promise<any>(r => { resolve = r }); return { promise, resolve } }
const tick = async (ui: any, ok: () => boolean) => { for (let i = 0; i < 100 && !ok(); i++) await ui.drawn(); expect(ok()).toBe(true) }
const redraw = async ($: any, ui: any) => { await ui.unmount(); return $.ui.mount(pane()) }
const focus = ($: any, element: string) => $.ui.focus({ component: 'Pane', requestId: 'binnacle-hud', plugin: 'binnacle-hud', element, origin: { kind: 'person' } })
const text = (row: any) => row.message.content[0].text
async function start($: any, on: any, store: any, options: any = {}) {
  const versions: Record<string, number> = {}
  const events = { asked: [] as string[], prompt: [] as string[], writes: [] as string[] }
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: any, e: any) => ({ cwd: e.cwd }))
  on('ui.focus', { plugin: '*' }, () => ({ value: {} }))
  on('state.get', (_: any, e: any) => ({ value: { value: store[e.key], version: versions[e.key] ?? 0 } }))
  on('state.set', async (_: any, e: any) => {
    if (options.beforeSet) await options.beforeSet(e)
    if (e.ifVersion !== undefined && e.ifVersion !== (versions[e.key] ?? 0)) return { value: { isSet: false, version: versions[e.key] ?? 0 } }
    store[e.key] = e.value
    versions[e.key] = (versions[e.key] ?? 0) + 1
    events.writes.push(e.key)
    return { value: { isSet: true, version: versions[e.key] } }
  })
  for (const op of ['prompt.fill', 'prompt.submit', 'prompt.context', 'prompt.paint']) on(op as any, () => { events.prompt.push(op); return {} as any })
  on('tool.call', async (_: any, e: any) => {
    const q = e.questions[0].question
    events.asked.push(q)
    const answer = options.ask ? await options.ask(q) : 'Send'
    return answer === undefined ? { deny: 'reviewer dismissed dialog' } : { result: { answers: { [q]: answer } } }
  })
  mock.clock(on, { now: NOW })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  return events
}

test('REVIEW shared Input change -> focus actions -> a; Enter -> p; empty and ninth-line removal never send or touch prompt', async ($, on) => {
  const store: any = {}
  const session = mock.session(on)
  const events = await start($, on, store)
  let ui = await $.ui.mount(pane())
  await focus($, 'thought')
  await ui.input({ key: 'thought', text: 'private decision', kind: 'change' })
  expect(store.typed).toBe('private decision')
  expect(store.memory).toBeUndefined()
  await focus($, 'k-a') // SDK focus event for Tab; not native keyboard simulation.
  ui = await redraw($, ui)
  await ui.press({ key: 'k-a' })
  expect(store.memory.map((e: any) => e.text)).toEqual(['private decision'])
  expect(store.typed).toBe('')
  expect(store.log).toBeUndefined()
  await focus($, 'thought')
  ui = await redraw($, ui)
  await ui.input({ key: 'thought', text: 'log decision', kind: 'change' })
  await ui.input({ key: 'thought', text: 'log decision' })
  expect(store.memory.map((e: any) => e.text)).toEqual(['private decision'])
  expect(store.log.map((t: any) => t.text)).toEqual(['log decision'])
  await focus($, 'k-p')
  ui = await redraw($, ui)
  await ui.press({ key: 'k-p' })
  expect(store.memory.map((e: any) => e.text)).toEqual(['private decision', 'log decision'])
  expect(store.log.map((t: any) => t.text)).toEqual(['log decision'])
  for (let n = 3; n <= 10; n++) {
    await ui.input({ key: 'thought', text: `decision ${n}`, kind: 'change' })
    ui = await redraw($, ui)
    await ui.press({ key: 'k-a' })
  }
  expect(store.memory).toHaveLength(10)
  ui = await redraw($, ui)
  await ui.press({ key: 'k-9' })
  expect(store.memory).toHaveLength(9)
  expect(store.memory.map((e: any) => e.text).slice(-2)).toEqual(['decision 8', 'decision 10'])
  await ui.input({ key: 'thought', text: '   ', kind: 'change' })
  ui = await redraw($, ui)
  expect(await ui.find({ key: 'k-a' })).toBeUndefined()
  await ui.input({ key: 'thought', text: '   ' })
  expect(store.log).toHaveLength(1)
  expect(store.memory).toHaveLength(9)
  expect(store.approved).toBeUndefined()
  expect(session.appended()).toHaveLength(0)
  expect(events.prompt).toEqual([])
  expect(events.asked).toEqual([])
})

test('REVIEW pending Send freezes candidate through actual remove action; approve waits for append; double Send stays single', async ($, on) => {
  const earlier = { lines: ['previous approved'], at: 0 }
  const store: any = { memory: ['candidate A', 'candidate B'], approved: earlier }
  const ask = deferred(), append = deferred()
  let appending = false
  const session = mock.session(on)
  on('session.append', { door: 'note' }, async (_: any, e: any, next: any) => { appending = true; await append.promise; return next(e) })
  const events = await start($, on, store, { ask: () => ask.promise })
  const ui = await $.ui.mount(pane())
  const sending = ui.press({ key: 'k-s' })
  await tick(ui, () => events.asked.length === 1)
  const removing = ui.press({ key: 'k-2' })
  await tick(ui, () => store.memory.length === 1)
  const second = ui.press({ key: 'k-s' })
  ask.resolve('Send')
  await tick(ui, () => appending)
  expect(store.approved).toEqual(earlier)
  expect(session.appended()).toHaveLength(0)
  append.resolve()
  await Promise.all([sending, removing, second])
  expect(events.asked).toHaveLength(1)
  expect(events.asked[0]).toContain('- candidate A\n- candidate B')
  expect(session.appended()).toHaveLength(1)
  expect(text(session.appended()[0]).split('\n').slice(1)).toEqual(['candidate A', 'candidate B'])
  expect(store.approved.lines).toEqual(['candidate A', 'candidate B'])
  expect(store.memory.map((e: any) => e.text)).toEqual(['candidate A'])
  expect(JSON.stringify(await (await redraw($, ui)).drawn())).toContain('Changed since Send.')
})

test('REVIEW dismissed ask and refused append keep previous approval and allow a later retry', async ($, on) => {
  const earlier = { lines: ['old'], at: 0 }
  const store: any = { memory: ['new'], approved: earlier }
  let rejectAppend = true
  const session = mock.session(on)
  on('session.append', { door: 'note' }, async (_: any, e: any, next: any) => rejectAppend ? { deny: 'append offline' } : next(e))
  const events = await start($, on, store, { ask: (() => { let first = true; return () => { if (first) { first = false; return undefined } return 'Send' } })() })
  let ui = await $.ui.mount(pane())
  await ui.press({ key: 'k-s' })
  expect(store.approved).toEqual(earlier)
  expect(session.appended()).toHaveLength(0)
  await ui.press({ key: 'k-s' })
  expect(store.approved).toEqual(earlier)
  expect(session.appended()).toHaveLength(0)
  ui = await redraw($, ui)
  expect(JSON.stringify(await ui.drawn())).toContain('Not sent. append offline')
  rejectAppend = false
  await ui.press({ key: 'k-s' })
  expect(store.approved.lines).toEqual(['new'])
  expect(session.appended()).toHaveLength(1)
  expect(events.asked).toHaveLength(3)
  expect(store.view.failed).toBe('')
})

for (const action of ['keep', 'add']) {
  test(`${action}: an ABA edit during the clear write survives its CAS retry`, async ($, on) => {
    const raw = '  first line  '
    const store: any = {}
    const gate = deferred()
    let blocked = false
    const session = mock.session(on)
    const events = await start($, on, store, { beforeSet: async (e: any) => {
      if (e.key === 'typed' && e.value === '' && !blocked) { blocked = true; await gate.promise }
    } })
    let ui = await $.ui.mount(pane())
    await ui.input({ key: 'thought', text: raw, kind: 'change' })
    ui = await redraw($, ui)
    const saving = action === 'keep' ? ui.input({ key: 'thought', text: raw }) : ui.press({ key: 'k-a' })
    await tick(ui, () => blocked)
    await ui.input({ key: 'thought', text: '', kind: 'change' })
    await ui.input({ key: 'thought', text: raw, kind: 'change' })
    gate.resolve()
    await saving
    expect(store.typed).toBe(raw)
    if (action === 'keep') expect(store.log.map((t: any) => t.text)).toEqual([raw])
    else expect(store.memory.map((e: any) => e.text)).toEqual(['first line'])
    expect(session.appended()).toHaveLength(0)
    expect(events.prompt).toEqual([])
  })
}

for (const later of [['unfinished second line'], ['', '  first line  '], [], ['']]) {
  test(`shared-field edits ${JSON.stringify(later)} during Add preserve draft identity`, async ($, on) => {
    const store: any = {}
    const gate = deferred()
    let blocked = false
    const session = mock.session(on)
    const events = await start($, on, store, { beforeSet: async (e: any) => { if (e.key === 'memory' && !blocked) { blocked = true; await gate.promise } } })
    let ui = await $.ui.mount(pane())
    await ui.input({ key: 'thought', text: '  first line  ', kind: 'change' })
    await focus($, 'k-a')
    ui = await redraw($, ui)
    const adding = ui.press({ key: 'k-a' })
    await tick(ui, () => blocked)
    await focus($, 'thought')
    for (const text of later) {
      await ui.input({ key: 'thought', text, kind: 'change' })
      await tick(ui, () => store.typed === text)
    }
    gate.resolve()
    await adding
    expect(store.memory.map((e: any) => e.text)).toEqual(['first line'])
    expect(session.appended()).toHaveLength(0)
    expect(events.prompt).toEqual([])
    expect(store.typed).toBe(later.at(-1) ?? '')
  })
}
