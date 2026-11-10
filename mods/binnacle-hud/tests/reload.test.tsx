import { expect, mock, test } from 'claude-code/testing'

// A cleared draft outlives a reload in session state, while the module's
// event numbers start again. Its own file, so the module loads fresh.

test('after a reload, a submit cannot drop a cleared draft stored before it', async ($, on) => {
  mock.clock(on)
  const state: Record<string, { value: any; version: number }> = {
    lost: { value: { text: 'kept before the reload', at: 0, moves: 1 }, version: 1 },
  }
  const cell = (k: string) => state[k] ?? { value: undefined, version: 0 }
  let box = ''
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: unknown, e: any) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: any) => ({ value: { ...cell(e.key) } }))
  on('state.set', (_: unknown, e: any) => {
    const now = cell(e.key)
    if (e.ifVersion !== undefined && e.ifVersion !== now.version) return { value: { isSet: false, version: now.version } }
    state[e.key] = { value: e.value, version: now.version + 1 }
    return { value: { isSet: true, version: now.version + 1 } }
  })
  on('prompt.edit', (_: unknown, e: any) => {
    box = e.text.slice(0, e.start) + e.inputText + e.text.slice(e.end)
    return { text: box, cursor: box.length }
  })
  on('prompt.change', (_: unknown, e: any) => ({ text: e.text }))
  on('prompt.submit', (_: unknown, e: any) => ({ text: e.text }))
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.prompt.edit({ origin: { kind: 'composer' }, text: '', cursor: 0, start: 0, end: 0, inputText: 'x' })
  await $.prompt.submit({ text: box, wait: false, origin: { kind: 'composer' } })
  expect(cell('lost').value?.text).toBe('kept before the reload')
})
