import { expect, mock, test } from 'claude-code/testing'

// Exercise real SDK update retries: an older edit must not replace newer typing.
const pane = () => ({
  plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: { title: 'Binnacle', isFocused: true, bodyColumns: 46, placement: 'dock', scroll: { offset: 0, bodyRows: 32 }, view: {} },
}) as const
const deferred = () => {
  let resolve = () => {}
  const promise = new Promise<void>(r => { resolve = r })
  return { promise, resolve }
}

async function start($: any, on: any, store: any, hold?: { gate: Promise<void>; entered: () => void }) {
  const versions: Record<string, number> = {}
  const writes: { key: string; value: unknown; isSet: boolean }[] = []
  let held = false
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: any, e: any) => ({ cwd: e.cwd }))
  on('ui.focus', () => ({ value: {} }))
  on('state.get', (_: any, e: any) => ({ value: { value: store[e.key], version: versions[e.key] ?? 0 } }))
  on('state.set', async (_: any, e: any) => {
    if (hold && e.key === 'typed' && !held) { held = true; hold.entered(); await hold.gate }
    const miss = e.ifVersion !== undefined && e.ifVersion !== (versions[e.key] ?? 0)
    writes.push({ key: e.key, value: e.value, isSet: !miss })
    if (miss) return { value: { isSet: false, version: versions[e.key] ?? 0 } }
    store[e.key] = e.value
    versions[e.key] = (versions[e.key] ?? 0) + 1
    return { value: { isSet: true, version: versions[e.key] } }
  })
  const clock = mock.clock(on)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  return { clock, writes }
}

test('three overlapping edits leave the newest text in the shared field', async ($, on) => {
  const store: any = {}
  const { clock } = await start($, on, store)
  const ui = await $.ui.mount(pane())
  await Promise.all(['a', 'ab', 'abc'].map(text => ui.input({ key: 'thought', text, kind: 'change' })))
  await clock.settle()
  expect(store.typed).toBe('abc')
})

test('an older input write retried after later edits preserves the newest text', async ($, on) => {
  const store: any = {}
  const gate = deferred(), entered = deferred()
  const { clock, writes } = await start($, on, store, { gate: gate.promise, entered: entered.resolve })
  const ui = await $.ui.mount(pane())
  const first = ui.input({ key: 'thought', text: 'a', kind: 'change' })
  await entered.promise
  await ui.input({ key: 'thought', text: 'ab', kind: 'change' })
  await ui.input({ key: 'thought', text: 'abc', kind: 'change' })
  expect(store.typed).toBe('abc')
  gate.resolve()
  await first
  await clock.settle()
  expect(writes.some(w => w.key === 'typed' && !w.isSet)).toBe(true)
  expect(store.typed).toBe('abc')
})
