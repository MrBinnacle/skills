import { expect, mock, test } from 'claude-code/testing'

// A gap from the integration review: failed keeps had no dismiss key.

const NOW = Date.UTC(2026, 10, 9, 14, 2)
const pane = {
  plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: { title: 'Binnacle', isFocused: true, bodyColumns: 46, placement: 'dock', scroll: { offset: 0, bodyRows: 32 }, view: {} },
} as const

type Store = Record<string, any>
const start = async ($: any, on: any, store: Store, deny: string[] = []) => {
  const versions: Record<string, number> = {}
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.focus', () => ({ value: {} }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: { key: string }) => ({ value: { value: store[e.key], version: versions[e.key] ?? 0 } }))
  on('state.set', (_: unknown, e: { key: string; value: unknown }) => {
    if (deny.includes(e.key)) return { deny: 'injected state write failure' }
    store[e.key] = e.value
    versions[e.key] = (versions[e.key] ?? 0) + 1
    return { value: { isSet: true, version: versions[e.key] } }
  })
  on('tool.call', (_: unknown, e: any) => ({ result: { answers: { [e.questions[0].question]: 'Send' } } }))
  mock.clock(on, { now: NOW })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
}
const shown = async ($: any) => {
  const ui = await $.ui.mount(pane)
  const text = JSON.stringify(await ui.drawn())
  await ui.unmount()
  return text
}

test('d dismisses the failed keeps on screen and keeps one that failed since', async ($, on) => {
  const store: Store = { failed: ['first lost', 'second lost'] }
  await start($, on, store)
  const ui = await $.ui.mount(pane)
  store.failed = [...store.failed, 'failed after the draw']
  await ui.press({ key: 'k-d' })
  await ui.unmount()
  expect(store.failed.map((e: any) => e.text ?? e)).toEqual(['failed after the draw'])
})

test('no d key when nothing failed', async ($, on) => {
  await start($, on, { failed: [] })
  expect(await shown($)).not.toContain('dismiss failed')
})
