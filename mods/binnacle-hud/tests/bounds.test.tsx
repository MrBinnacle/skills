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
type Start = { refuse?: string; openFails?: boolean; deny?: string[]; answer?: string; version?: string }
const start = async ($: any, on: any, store: Store, how: Start = {}) => {
  const seen = { registered: [] as string[], toasts: [] as string[], opened: 0 }
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
  if (how.version) on('session.version', () => ({ value: { version: how.version, base: how.version } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: { key: string }) => ({ value: { value: store[e.key], version: versions[e.key] ?? 0 } }))
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

test('one thought is kept to its first 2000 characters, counted by code point', async ($, on) => {
  const store: Store = { log: [], typed: '' }
  await start($, on, store)
  const ui = await $.ui.mount(pane())
  await ui.input({ key: 'thought', text: '\u{1F9ED}'.repeat(2500) })
  await ui.unmount()
  expect(Array.from(store.log[0].text)).toHaveLength(2000)
  expect(store.log[0].text).toBe('\u{1F9ED}'.repeat(2000))
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
  expect(idle).toContain('Memory holds 20 lines, the most it keeps. Remove one to add another.')
  store.typed = 'one more decision'
  const writing = await drawn($)
  expect(writing).not.toContain('to memory')
})

test('Memory below the cap still offers both add keys', async ($, on) => {
  const store: Store = { memory: lines(19), log: thoughts(1), typed: '' }
  await start($, on, store)
  const idle = await drawn($)
  expect(idle).toContain('last thought to memory')
  expect(idle).not.toContain('the most it keeps')
})

test('a docked Log thought and Memory line stop at three lines; the strip truncates to one', { options: { narrow: 'strip' } }, async ($, on) => {
  const long = 'word '.repeat(400)
  await start($, on, { log: [{ text: long, at: '2026-11-17T09:00:00.000Z', from: 'terminal' }], memory: [{ id: 'm', text: long }], typed: '', view: { ring: 0, expand: 2, failed: '' } }, { version: '2.1.326' })
  const dock = await $.ui.mount(pane())
  const tree = JSON.stringify(await dock.drawn())
  expect(tree.split('"maxLines":3').length - 1).toBe(2)
  await dock.unmount()
  const strip = await $.ui.mount({ ...pane('inline'), props: { ...pane('inline').props, bodyColumns: 90 } })
  const row = await strip.find({ type: 'Text', text: /word word/ })
  expect(row?.props.wrap).toBe('truncate-end')
  expect(row?.props.maxLines).toBeUndefined()
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
