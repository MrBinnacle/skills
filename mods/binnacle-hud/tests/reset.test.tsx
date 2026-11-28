import { expect, mock, test } from 'claude-code/testing'

// /clear, /resume and /branch empty every state value and keep the module (Claude Code 2.1.332, seen live
// 2026-11-28). The Log and the Memory draft are the person's own text, so they come back. The Send record
// does not: the new conversation was given nothing.

const pane = () => ({
  plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: { title: 'Binnacle', isFocused: true, bodyColumns: 46, placement: 'dock',
    scroll: { offset: 0, bodyRows: 32 }, view: {} },
}) as const

const start = async ($: any, on: any, store: Record<string, any>) => {
  const versions: Record<string, number> = {}
  on('command.register', (_: unknown, e: { name: string }) => ({ value: { command: e.name } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.toast', () => ({ value: undefined }))
  on('ui.focus', () => ({ value: {} }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('classic.SessionStart', () => ({}))
  on('state.get', (_: unknown, e: { key: string }) => ({ value: { value: store[e.key], version: versions[e.key] ?? 0 } }))
  on('state.set', (_: unknown, e: { key: string; value: unknown }) => {
    store[e.key] = e.value
    versions[e.key] = (versions[e.key] ?? 0) + 1
    return { value: { isSet: true, version: versions[e.key] } }
  })
  on('tool.call', (_: unknown, e: any) => ({ result: { answers: { [e.questions[0].question]: 'Send' } } }))
  mock.clock(on, { now: Date.UTC(2026, 10, 28, 9, 30) })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
}
const wipe = (store: Record<string, any>) => { for (const k of Object.keys(store)) delete store[k] }

test('a /clear keeps the Log and the Memory draft, and drops the Send record', async ($, on) => {
  const store: Record<string, any> = {}
  await start($, on, store)
  const ui = await $.ui.mount(pane())
  await ui.input({ key: 'thought', text: 'check the retry budget' })
  store.typed = 'ship slice 1'
  await ui.unmount()
  const again = await $.ui.mount(pane())
  await again.press({ key: 'k-a' })
  await again.unmount()
  const third = await $.ui.mount(pane())
  await third.press({ key: 'k-s' })
  await third.unmount()
  expect(store.approved.lines).toEqual(['ship slice 1'])

  wipe(store)
  await $.classic.SessionStart({ source: 'clear' })
  expect(store.log.map((t: any) => t.text)).toEqual(['check the retry budget'])
  expect(store.memory.map((l: any) => l.text)).toEqual(['ship slice 1'])
  expect(store.approved).toBeUndefined()
  expect(store.delivered).toBeUndefined()
})

test('a /clear after a reload keeps what was stored before the reload', async ($, on) => {
  const store: Record<string, any> = {
    log: [{ text: 'kept before the reload', at: '2026-11-28T09:00:00.000Z', from: 'terminal' }],
    memory: [{ id: 'id-0', text: 'drafted before the reload' }],
  }
  await start($, on, store)
  wipe(store)
  await $.classic.SessionStart({ source: 'clear' })
  expect(store.log.map((t: any) => t.text)).toEqual(['kept before the reload'])
  expect(store.memory.map((l: any) => l.text)).toEqual(['drafted before the reload'])
})

test('a removed Memory line stays removed after a /clear', async ($, on) => {
  const store: Record<string, any> = { typed: 'ship slice 1' }
  await start($, on, store)
  const ui = await $.ui.mount(pane())
  await ui.press({ key: 'k-a' })
  await ui.unmount()
  const again = await $.ui.mount(pane())
  await again.press({ key: 'k-1' })
  await again.unmount()
  expect(store.memory).toEqual([])
  wipe(store)
  await $.classic.SessionStart({ source: 'clear' })
  expect(store.memory ?? []).toEqual([])
})

test('a session start that emptied nothing leaves a newer Log alone', async ($, on) => {
  const store: Record<string, any> = {}
  await start($, on, store)
  const ui = await $.ui.mount(pane())
  await ui.input({ key: 'thought', text: 'first' })
  await ui.unmount()
  store.log = [...store.log, { text: 'written elsewhere', at: '2026-11-28T09:31:00.000Z', from: 'terminal' }]
  await $.classic.SessionStart({ source: 'compact' })
  expect(store.log.map((t: any) => t.text)).toEqual(['first', 'written elsewhere'])
})
