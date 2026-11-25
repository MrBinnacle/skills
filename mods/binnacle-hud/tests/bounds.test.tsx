import { expect, mock, test } from 'claude-code/testing'
import { takesMaxLines } from '../hooks/register'

// Findings Wk1, Wk2 and H2 of the 2026-11-12 review: a refused command name
// or a failed open must not stop the HUD from starting, and the Log, the
// failed list and Memory stay bounded.

const NOW = Date.UTC(2026, 10, 17, 9, 30)
const pane = (placement: 'dock' | 'inline' = 'dock') => ({
  plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: { title: 'Binnacle', isFocused: true, bodyColumns: 46, placement,
    scroll: { offset: 0, bodyRows: 32 }, view: {} },
}) as const

type Store = Record<string, any>
type Start = { refuse?: string; openFails?: boolean; deny?: string[]; unreadable?: string; answer?: string; version?: string; base?: string }
const start = async ($: any, on: any, store: Store, how: Start = {}) => {
  const seen = { registered: [] as string[], toasts: [] as string[], opened: 0, versionReads: 0 }
  const versions: Record<string, number> = {}
  on('command.register', (_: unknown, e: { name: string }) => {
    if (e.name === how.refuse) return { deny: 'a built-in holds the name' }
    seen.registered.push(e.name)
    return { value: { command: e.name } }
  })
  on('ui.open', () => {
    seen.opened++
    return how.openFails ? { deny: 'no room for a pane' } : { value: { isPlaced: true } }
  })
  on('ui.toast', (_: unknown, e: { text: string }) => {
    seen.toasts.push(e.text)
    return { value: undefined }
  })
  on('ui.focus', () => ({ value: {} }))
  if (how.version) on('session.version', () => (seen.versionReads++, { value: { version: how.version, base: how.base ?? how.version } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: { key: string }) => e.key === how.unreadable
    ? { deny: 'injected state read failure' }
    : { value: { value: store[e.key], version: versions[e.key] ?? 0 } })
  on('state.set', (_: unknown, e: { key: string; value: unknown }) => {
    if (how.deny?.includes(e.key)) return { deny: 'injected state write failure' }
    store[e.key] = e.value
    versions[e.key] = (versions[e.key] ?? 0) + 1
    return { value: { isSet: true, version: versions[e.key] } }
  })
  on('tool.call', (_: unknown, e: any) => ({ result: { answers: { [e.questions[0].question]: how.answer ?? 'Send' } } }))
  mock.clock(on, { now: NOW })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  return seen
}

const drawn = async ($: any) => {
  const ui = await $.ui.mount(pane())
  const text = JSON.stringify(await ui.drawn())
  await ui.unmount()
  return text
}
const thoughts = (n: number) => Array.from({ length: n }, (_, i) => ({ text: `thought ${i}`, at: '2026-11-17T09:00:00.000Z', from: 'terminal' }))
const lines = (n: number) => Array.from({ length: n }, (_, i) => ({ id: `id-${i}`, text: `line ${i}` }))

test('a refused /log still opens the pane, migrates old state, registers /hud and says which name failed', async ($, on) => {
  const store: Store = { memory: ['a bare 4.1.0 line'] }
  const seen = await start($, on, store, { refuse: 'log' })
  expect(seen.opened).toBe(1)
  expect(store.memory[0].id).toBeDefined()
  expect(seen.registered).toEqual(['hud'])
  expect(seen.toasts).toEqual(['binnacle-hud could not register /log: Claude Code refused the name.'])
})

test('a refused /hud does not stop /log from registering', async ($, on) => {
  const seen = await start($, on, {}, { refuse: 'hud' })
  expect(seen.registered).toEqual(['log'])
  expect(seen.toasts.join(' ')).toContain('/hud')
})

test('an open that rejects is reported in a toast, and the session start goes on', async ($, on) => {
  const store: Store = { failed: ['a bare 4.1.0 miss'] }
  const seen = await start($, on, store, { openFails: true })
  expect(seen.registered).toEqual(['hud', 'log'])
  expect(store.failed[0].id).toBeDefined()
  expect(seen.toasts.join(' ')).toContain('could not open the HUD')
})

test('the Log keeps the newest 100 thoughts', async ($, on) => {
  const store: Store = { log: thoughts(100), typed: '' }
  await start($, on, store)
  const ui = await $.ui.mount(pane())
  await ui.input({ key: 'thought', text: 'the newest one' })
  await ui.unmount()
  expect(store.log).toHaveLength(100)
  expect(store.log.at(-1).text).toBe('the newest one')
  expect(store.log[0].text).toBe('thought 1')
})

test('the failed list keeps the newest 100 misses', async ($, on) => {
  const store: Store = { log: [], failed: lines(100), typed: '' }
  await start($, on, store, { deny: ['log'] })
  const ui = await $.ui.mount(pane())
  await ui.input({ key: 'thought', text: 'lost while the disk was full' })
  await ui.unmount()
  expect(store.failed).toHaveLength(100)
  expect(store.failed.at(-1).text).toBe('lost while the disk was full')
  expect(store.failed[0].text).toBe('line 1')
})

test('one thought is kept to its first 2000 characters, counted by code point, and a toast says so', async ($, on) => {
  const store: Store = { log: [], typed: '' }
  const seen = await start($, on, store)
  const ui = await $.ui.mount(pane())
  await ui.input({ key: 'thought', text: '\u{1F9ED}'.repeat(2500) })
  await ui.unmount()
  expect(Array.from(store.log[0].text)).toHaveLength(2000)
  expect(store.log[0].text).toBe('\u{1F9ED}'.repeat(2000))
  expect(seen.toasts).toEqual(['binnacle-hud kept the first 2000 characters. The rest was dropped.'])
})

test('a thought of exactly 2000 characters is kept whole, with no toast', async ($, on) => {
  const store: Store = { log: [], typed: '' }
  const seen = await start($, on, store)
  const ui = await $.ui.mount(pane())
  await ui.input({ key: 'thought', text: 'x'.repeat(2000) })
  await ui.unmount()
  expect(store.log[0].text).toHaveLength(2000)
  expect(seen.toasts).toEqual([])
})

test('a failed keep records only the first 2000 characters', async ($, on) => {
  const store: Store = { log: [], failed: [], typed: '' }
  await start($, on, store, { deny: ['log'] })
  const ui = await $.ui.mount(pane())
  await ui.input({ key: 'thought', text: 'f'.repeat(2600) })
  await ui.unmount()
  expect(store.failed[0].text).toBe('f'.repeat(2000))
})

test('a failed keep of a long thought shows no cut toast, since nothing was kept', async ($, on) => {
  const store: Store = { log: [], failed: [], typed: '' }
  const seen = await start($, on, store, { deny: ['log'] })
  const ui = await $.ui.mount(pane())
  await ui.input({ key: 'thought', text: 'f'.repeat(2600) })
  await ui.unmount()
  expect(store.failed).toHaveLength(1)
  expect(seen.toasts).toEqual([])
})

for (const key of ['memory', 'failed']) {
  test(`an unreadable ${key} at start still registers both commands and reads the version`, async ($, on) => {
    const seen = await start($, on, { log: thoughts(1), typed: '' }, { unreadable: key, version: '2.1.326' })
    expect(seen.registered).toEqual(['hud', 'log'])
    expect(seen.versionReads).toBe(1)
  })
}

test('a Memory line from the field keeps its first 2000 characters, and a toast says so', async ($, on) => {
  const store: Store = { memory: [], log: [], typed: 'm'.repeat(3000) }
  const seen = await start($, on, store)
  const ui = await $.ui.mount(pane())
  await ui.press({ key: 'k-a' })
  await ui.unmount()
  expect(store.memory[0].text).toBe('m'.repeat(2000))
  expect(store.typed).toBe('')
  expect(seen.toasts).toEqual(['binnacle-hud kept the first 2000 characters. The rest was dropped.'])
})

test('a Log thought longer than 2000 characters reaches Memory clipped', async ($, on) => {
  const store: Store = { memory: [], log: [{ text: 'y'.repeat(3000), at: '2026-11-17T09:00:00.000Z', from: 'terminal' }], typed: '' }
  await start($, on, store)
  const ui = await $.ui.mount(pane())
  await ui.press({ key: 'k-p' })
  await ui.unmount()
  expect(store.memory[0].text).toBe('y'.repeat(2000))
})

test('/log says when it cut a long thought, without repeating it', async ($, on) => {
  const store: Store = { log: [] }
  await start($, on, store, { answer: 'x'.repeat(2400) })
  const out = await ($ as any).command.run({ command: 'log', args: '', origin: { kind: 'bridge' } })
  expect(out.text).toBe('Kept in the Log. Only its first 2000 characters were kept.')
  expect(store.log[0].text).toHaveLength(2000)
})

test('a full Memory offers no key that adds a line, and says how to make room', async ($, on) => {
  const store: Store = { memory: lines(20), log: thoughts(1), typed: '' }
  await start($, on, store)
  const idle = await drawn($)
  expect(idle).not.toContain('last thought to memory')
  expect(idle).toContain('Memory holds 20 lines and keeps at most 20. Remove one to add another.')
  store.typed = 'one more decision'
  const writing = await drawn($)
  expect(writing).not.toContain('to memory')
})

test('Memory left over 20 lines by old state is drawn whole, gives its real count and offers no add key', async ($, on) => {
  const store: Store = { memory: lines(25), log: thoughts(1), typed: '' }
  await start($, on, store)
  const idle = await drawn($)
  expect(idle).toContain('Memory holds 25 lines and keeps at most 20. Remove one to add another.')
  expect(idle).toContain('line 24')
  expect(idle).not.toContain('last thought to memory')
  expect(store.memory).toHaveLength(25)
})

test('Memory below the cap still offers both add keys', async ($, on) => {
  const store: Store = { memory: lines(19), log: thoughts(1), typed: '' }
  await start($, on, store)
  const idle = await drawn($)
  expect(idle).toContain('last thought to memory')
  expect(idle).not.toContain('keeps at most')
})

test('a docked Log thought and Memory line stop at three lines; the strip truncates to one', { options: { narrow: 'strip' } }, async ($, on) => {
  const at = '2026-11-17T09:00:00.000Z'
  const store: Store = { log: [{ text: 'logword '.repeat(400), at, from: 'terminal' }], memory: [{ id: 'm', text: 'memword '.repeat(400) }], typed: '', view: { ring: 0, expand: 2, failed: '' } }
  await start($, on, store, { version: '2.1.326' })
  const rows = { 1: /memword memword/, 2: /logword logword/ }
  const dock = await $.ui.mount(pane())
  for (const text of Object.values(rows)) {
    const row = await dock.find({ type: 'Text', text })
    expect(row).toBeDefined()
    expect(row?.props.maxLines).toBe(3)
  }
  await dock.unmount()
  // The strip shows one section at a time: expand 1 is Memory, 2 is the Log.
  for (const [expand, text] of Object.entries(rows)) {
    store.view = { ring: 0, expand: Number(expand), failed: '' }
    const strip = await $.ui.mount({ ...pane('inline'), props: { ...pane('inline').props, bodyColumns: 90 } })
    const row = await strip.find({ type: 'Text', text })
    expect(row).toBeDefined()
    expect(row?.props.wrap).toBe('truncate-end')
    expect(row?.props.maxLines).toBeUndefined()
    await strip.unmount()
  }
})

test('a pane drawn before the version is known redraws capped once it is', async ($, on) => {
  let release!: () => void
  const gate = new Promise<void>(r => { release = r })
  on('command.register', (_: unknown, e: { name: string }) => ({ value: { command: e.name } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.toast', () => ({ value: undefined }))
  on('state.get', (_: unknown, e: { key: string }) => ({ value: { value: e.key === 'log' ? [{ text: 'word '.repeat(400), at: '2026-11-17T09:00:00.000Z', from: 'terminal' }] : undefined, version: 0 } }))
  on('session.version', async () => { await gate; return { value: { version: '2.1.326', base: '2.1.326' } } })
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  const started = $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  const ui = await $.ui.mount(pane())
  const before = JSON.stringify(await ui.drawn())
  release()
  await started
  expect(before).not.toContain('maxLines')
  expect(JSON.stringify(await ui.drawn())).toContain('"maxLines":3')
})

test('the release base, not the spelled version, decides maxLines', async ($, on) => {
  await start($, on, { log: thoughts(1), memory: lines(1), typed: '' }, { version: '9.9.9-fork', base: '2.1.325' })
  expect(await drawn($)).not.toContain('maxLines')
})

test('opened docked heads-up details stop at three lines; the strip, which hides the field, shows them whole', { options: { narrow: 'strip' } }, async ($, on) => {
  const long = 'detail '.repeat(280)
  const note = { key: '00000000-0000-4000-8000-000000000001', line: 'A note.', explanation: long, at: NOW, how: 'own turn' }
  await start($, on, { notes: { list: [note], free: false }, typed: '', view: { ring: 0, expand: 4, failed: '' } }, { version: '2.1.326' })
  const dock = await $.ui.mount(pane())
  const docked = await dock.find({ type: 'Text', text: /detail detail/ })
  expect(docked?.props.maxLines).toBe(3)
  await dock.unmount()
  const strip = await $.ui.mount({ ...pane('inline'), props: { ...pane('inline').props, bodyColumns: 90 } })
  const whole = await strip.find({ type: 'Text', text: /detail detail/ })
  expect(whole?.props.wrap).toBe('wrap')
  expect(whole?.props.maxLines).toBeUndefined()
})

for (const version of ['2.1.325', undefined]) {
  test(`an engine at ${version ?? 'an unknown version'} gets no maxLines, which it would refuse`, async ($, on) => {
    await start($, on, { log: thoughts(1), memory: lines(1), typed: '' }, { version })
    expect(await drawn($)).not.toContain('maxLines')
  })
}

test('maxLines waits for 2.1.326', () => {
  expect(['2.1.326', '2.1.326-dev', '2.1.400', '2.2.0', '3.0.0'].map(takesMaxLines)).toEqual([true, true, true, true, true])
  expect(['2.1.325', '2.1.99', '2.0.999', '1.9.999', 'unknown'].map(takesMaxLines)).toEqual([false, false, false, false, false])
})

// Another write fills Memory between the draw and the add, so the key is on
// screen and only the guard inside the update can refuse the line.
const racing = async ($: any, on: any, initial: Store) => {
  const clock = mock.clock(on)
  const cells: Record<string, { value: any; version: number }> = Object.fromEntries(Object.entries(initial).map(([k, value]) => [k, { value, version: 1 }]))
  const cell = (k: string) => cells[k] ?? { value: undefined, version: 0 }
  let fill = false
  on('command.register', (_: unknown, e: { name: string }) => ({ value: { command: e.name } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.focus', () => ({ value: {} }))
  on('ui.toast', () => ({ value: undefined }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: { key: string }) => ({ value: { ...cell(e.key) } }))
  on('state.set', (_: unknown, e: { key: string; value: unknown; ifVersion?: number }) => {
    if (e.key === 'memory' && fill) { fill = false; cells.memory = { value: lines(20), version: cell('memory').version + 1 } }
    const old = cell(e.key)
    if (e.ifVersion !== undefined && e.ifVersion !== old.version) return { value: { isSet: false, version: old.version } }
    cells[e.key] = { value: e.value, version: old.version + 1 }
    return { value: { isSet: true, version: old.version + 1 } }
  })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  return { clock, cell, fillNext: () => { fill = true } }
}

test('an add refused by a Memory that filled meanwhile keeps the field text', async ($, on) => {
  const s = await racing($, on, { memory: lines(19), typed: 'typed one', log: [] })
  const ui = await $.ui.mount(pane())
  s.fillNext()
  await ui.press({ key: 'k-a' })
  await s.clock.settle()
  await ui.unmount()
  expect(s.cell('memory').value).toHaveLength(20)
  expect(s.cell('typed').value).toBe('typed one')
})

test('p refused by a Memory that filled meanwhile adds nothing', async ($, on) => {
  const s = await racing($, on, { memory: lines(19), typed: '', log: thoughts(1) })
  const ui = await $.ui.mount(pane())
  s.fillNext()
  await ui.press({ key: 'k-p' })
  await s.clock.settle()
  await ui.unmount()
  expect(s.cell('memory').value).toHaveLength(20)
})
