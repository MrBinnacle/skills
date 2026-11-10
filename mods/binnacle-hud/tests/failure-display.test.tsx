import { expect, mock, test } from 'claude-code/testing'

// Regression probes from the #658 review. The backend implements ifVersion
// and the real SDK update retries.
const deferred = () => {
  let resolve = () => {}
  const promise = new Promise<void>(r => { resolve = r })
  return { promise, resolve }
}
const mount = async ($: any, on: any, denied: string[], placement = 'dock', expand = 0) => {
  const clock = mock.clock(on)
  const state: Record<string, { value: any; version: number }> = {
    view: { value: { ring: 1, expand, failed: '' }, version: 1 },
    typed: { value: 'first capture', version: 1 },
    log: { value: [], version: 1 }, failed: { value: [], version: 1 },
  }
  const entered = [deferred(), deferred()]
  const release = [deferred(), deferred()]
  let writes = 0
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: unknown, e: any) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: any) => ({ value: { ...state[e.key] } }))
  on('state.set', async (_: unknown, e: any) => {
    if (e.key === 'log') {
      const i = writes++
      if (i < 2) { entered[i]!.resolve(); await release[i]!.promise }
      if (denied.includes(e.value.at(-1).text)) return { deny: 'reviewer injected keep failure' }
    }
    if (e.ifVersion !== undefined && e.ifVersion !== state[e.key]!.version) {
      return { value: { isSet: false, version: state[e.key]!.version } }
    }
    const version = state[e.key]!.version + 1
    state[e.key] = { value: e.value, version }
    return { value: { isSet: true, version } }
  })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  const pane = { plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
    viewport: { columns: placement === 'dock' ? 160 : 96, rows: 40, isFullscreen: true },
    props: { title: 'Binnacle', isFocused: true, bodyColumns: placement === 'dock' ? 46 : 90,
      placement, scroll: { offset: 0, bodyRows: placement === 'dock' ? 32 : 8 }, view: {} } }
  let ui = await $.ui.mount(pane)
  const input = (text: string, change = false) => $.ui.input({ plugin: 'binnacle-hud', key: 'thought', text,
    ...(change ? { kind: 'change' } : {}) })
  // Mock state hooks do not prove live redraw subscriptions. Remount to require
  // the actual production render tree to SHOW the label and complete failed text.
  const failureText = async () => {
    await clock.settle()
    await ui.unmount()
    ui = await $.ui.mount(pane)
    return (await ui.findAll({ type: 'Text', text: /Not kept, the save failed:/ })).map((n: any) => n.text).join('\n')
  }
  return { state, entered, release, input, failureText, settle: clock.settle }
}
const containsFailure = (shown: string, text: string) => {
  expect(shown).toContain('Not kept, the save failed:')
  expect(shown).toContain(text)
}

for (const newer of [false, true]) {
  test(`review display: denied keep, newer typing=${newer}, shows the full failed text`, async ($, on) => {
    const p = await mount($, on, ['first capture'])
    const saving = p.input('first capture') // No test-side catch to hide a rejection.
    await p.entered[0]!.promise
    if (newer) await p.input('newer draft', true)
    p.release[0]!.resolve()
    await saving
    await p.settle()
    expect(p.state.log!.value).toEqual([])
    expect(p.state.typed!.value).toBe(newer ? 'newer draft' : 'first capture')
    expect(p.state.failed!.value.map((e: any) => e.text)).toEqual(['first capture'])
    containsFailure(await p.failureText(), 'first capture')
  })
}

for (const expand of [0, 3]) {
  test(`review display: inline strip expand=${expand} shows a denied keep after newer typing`,
    { options: { narrow: 'strip' } }, async ($, on) => {
      const p = await mount($, on, ['first capture'], 'inline', expand)
      const saving = p.input('first capture')
      await p.entered[0]!.promise
      await p.input('newer draft', true)
      p.release[0]!.resolve()
      await saving
      await p.settle()
      expect(p.state.log!.value).toEqual([])
      expect(p.state.typed!.value).toBe('newer draft')
      expect(p.state.failed!.value.map((e: any) => e.text)).toEqual(['first capture'])
      containsFailure(await p.failureText(), 'first capture')
    })
}

test('review retention: an unrelated later success does not discard a failed thought', async ($, on) => {
  const p = await mount($, on, ['first capture'])
  const first = p.input('first capture')
  await p.entered[0]!.promise
  await p.input('second capture', true)
  p.release[0]!.resolve()
  await first
  containsFailure(await p.failureText(), 'first capture')
  const second = p.input('second capture')
  await p.entered[1]!.promise
  p.release[1]!.resolve()
  await second
  await p.settle()
  expect(p.state.log!.value.map((t: any) => t.text)).toEqual(['second capture'])
  expect(p.state.typed!.value).toBe('')
  containsFailure(await p.failureText(), 'first capture')
})

for (const denied of [['first capture'], ['second capture'], ['first capture', 'second capture']]) {
  for (const order of [[0, 1], [1, 0]]) {
    test(`review retention: denied=${denied.join('+')}; overlapping completion=${order.join(',')}`, async ($, on) => {
      const p = await mount($, on, denied)
      const first = p.input('first capture')
      await p.entered[0]!.promise
      await p.input('second capture', true)
      const second = p.input('second capture')
      await p.entered[1]!.promise
      await p.input('third draft', true)
      p.release[order[0]!]!.resolve()
      await (order[0] === 0 ? first : second)
      await p.settle()
      p.release[order[1]!]!.resolve()
      await Promise.all([first, second])
      await p.settle()
      expect(p.state.log!.value.map((t: any) => t.text).sort())
        .toEqual(['first capture', 'second capture'].filter(t => !denied.includes(t)))
      expect(p.state.typed!.value).toBe('third draft')
      const shown = await p.failureText()
      for (const text of denied) containsFailure(shown, text)
    })
  }
}
