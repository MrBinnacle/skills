import { expect, mock, test } from 'claude-code/testing'

// Regression probes from the #658 review, using the SDK's CAS contract.
const deferred = () => {
  let resolve = () => {}
  const promise = new Promise<void>(r => { resolve = r })
  return { promise, resolve }
}
const mount = async ($: any, on: any, fail = false) => {
  const clock = mock.clock(on)
  const state: Record<string, { value: any; version: number }> = {
    view: { value: { ring: 1, expand: 0, failed: '' }, version: 1 },
    typed: { value: 'first capture', version: 1 }, log: { value: [], version: 1 },
    failed: { value: [], version: 1 },
  }
  const entered = [deferred(), deferred()]
  const release = [deferred(), deferred()]
  let writes = 0
  let misses = 0
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: unknown, e: any) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: any) => ({ value: { ...state[e.key] } }))
  on('state.set', async (_: unknown, e: any) => {
    if (e.key === 'log') {
      const i = writes++
      if (i < 2) { entered[i]!.resolve(); await release[i]!.promise }
      if (fail) return { deny: 'reviewer injected keep failure' }
    }
    if (e.ifVersion !== undefined && e.ifVersion !== state[e.key]!.version) {
      misses++
      return { value: { isSet: false, version: state[e.key]!.version } }
    }
    const version = state[e.key]!.version + 1
    state[e.key] = { value: e.value, version }
    return { value: { isSet: true, version } }
  })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.ui.mount({ plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
    viewport: { columns: 160, rows: 40, isFullscreen: true },
    props: { title: 'Binnacle', isFocused: true, bodyColumns: 46, placement: 'dock',
      scroll: { offset: 0, bodyRows: 32 }, view: {} } })
  const input = (text: string, change = false) => $.ui.input({ plugin: 'binnacle-hud', key: 'thought', text,
    ...(change ? { kind: 'change' } : {}) })
  return { state, entered, release, input, settle: clock.settle, misses: () => misses }
}

test('review: a retyped identical draft must survive the earlier save', async ($, on) => {
  const p = await mount($, on)
  const saving = p.input('first capture')
  await p.entered[0]!.promise
  await p.input('', true)
  await p.input('first capture', true)
  p.release[0]!.resolve()
  await saving
  await p.settle()
  expect(p.state.log!.value.map((t: any) => t.text)).toEqual(['first capture'])
  expect(p.state.typed!.value).toBe('first capture')
})

test('review: emptying the field during a save stays empty', async ($, on) => {
  const p = await mount($, on)
  const saving = p.input('first capture')
  await p.entered[0]!.promise
  await p.input('', true)
  p.release[0]!.resolve()
  await saving
  await p.settle()
  expect(p.state.log!.value.map((t: any) => t.text)).toEqual(['first capture'])
  expect(p.state.typed!.value).toBe('')
})

for (const order of [[0, 1], [1, 0]]) {
  test(`review: overlapping keeps complete ${order.join(',')} without losing either`, async ($, on) => {
    const p = await mount($, on)
    const first = p.input('first capture')
    await p.entered[0]!.promise
    await p.input('second capture', true)
    const second = p.input('second capture')
    await p.entered[1]!.promise
    p.release[order[0]!]!.resolve()
    await (order[0] === 0 ? first : second)
    await p.settle()
    p.release[order[1]!]!.resolve()
    await Promise.all([first, second])
    await p.settle()
    expect(p.state.log!.value.map((t: any) => t.text).sort()).toEqual(['first capture', 'second capture'])
    expect(p.state.typed!.value).toBe('')
    expect(p.misses()).toBe(1)
  })
}

test('review: a failed keep does not clear a newer draft', async ($, on) => {
  const p = await mount($, on, true)
  const saving = p.input('first capture').catch(() => undefined)
  await p.entered[0]!.promise
  await p.input('newer draft', true)
  p.release[0]!.resolve()
  await saving
  await p.settle()
  expect(p.state.log!.value).toEqual([])
  expect(p.state.typed!.value).toBe('newer draft')
})

test('review: a failed keep leaves the submitted draft available for retry', async ($, on) => {
  const p = await mount($, on, true)
  const saving = p.input('first capture').catch(() => undefined)
  await p.entered[0]!.promise
  p.release[0]!.resolve()
  await saving
  await p.settle()
  expect(p.state.log!.value).toEqual([])
  expect(p.state.typed!.value).toBe('first capture')
})
