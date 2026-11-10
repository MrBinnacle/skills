import { expect, mock, test } from 'claude-code/testing'
const deferred = () => { let resolve!: () => void; const promise = new Promise<void>(r => { resolve = r }); return { promise, resolve } }

test('parent: an old restore whose read starts late cannot consume a newer clear', async ($, on) => {
  const cells: Record<string, {value: any; version: number}> = {}
  const cell = (key: string) => cells[key] ?? { value: undefined, version: 0 }
  let box = '', holdRead = false
  const entered = deferred(), release = deferred()
  const trace: any[] = []
  mock.clock(on)
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.focus', () => ({ value: {} }))
  on('session.start', (_: any, e: any) => ({ cwd: e.cwd }))
  on('state.get', async (_: any, e: any) => {
    if (holdRead && e.key === 'lost') {
      holdRead = false
      entered.resolve()
      await release.promise
    }
    return { value: { ...cell(e.key) } }
  })
  on('state.set', (_: any, e: any) => {
    const old = cell(e.key)
    if (e.ifVersion !== undefined && e.ifVersion !== old.version)
      return { value: { isSet: false, version: old.version } }
    cells[e.key] = { value: e.value, version: old.version + 1 }
    if (e.key === 'lost') trace.push(e.value)
    return { value: { isSet: true, version: old.version + 1 } }
  })
  on('prompt.edit', (_: any, e: any) => {
    box = e.text.slice(0, e.start) + e.inputText + e.text.slice(e.end)
    return { text: box, cursor: box.length }
  })
  on('prompt.change', (_: any, e: any) => ({ text: e.text }))
  const change = (kind: string, text = '') => { box = text; return $.prompt.change({ text, cursor: text.length, origin: { kind } } as any) }
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.prompt.edit({ origin: { kind: 'composer' }, text: '', cursor: 0, start: 0, end: 0, inputText: 'same draft' })
  await change('clear')
  const first = cell('lost').value
  holdRead = true
  const oldRestore = change('history', 'same draft')
  await entered.promise
  await change('clear')
  const fresh = cell('lost').value
  expect(fresh.moves).not.toBe(first.moves)
  release.resolve()
  await oldRestore
  console.log(JSON.stringify({ first, fresh, after: cell('lost').value, trace }))
  expect(cell('lost').value).toEqual(fresh)
})
