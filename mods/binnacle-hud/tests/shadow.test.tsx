import { expect, mock, test } from 'claude-code/testing'

// The draft shadow. Event orders and shapes follow the live measurements on
// 2.1.319: an edit carries the draft before and the splice; submit, Ctrl+C,
// /clear and a stash each raise prompt.change with kind 'clear' and an empty
// box; Up and Down raise kind 'history'.

const pane = {
  plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: { title: 'Binnacle', isFocused: true, bodyColumns: 46, placement: 'dock', scroll: { offset: 0, bodyRows: 32 }, view: {} },
} as const

const deferred = () => {
  let resolve = () => {}
  const promise = new Promise<void>(r => { resolve = r })
  return { promise, resolve }
}

const start = async ($: any, on: any, opts: { holdFirstLost?: { promise: Promise<void> }; entered?: () => void; refuseCopy?: boolean; holdEdit?: { promise: Promise<void> }; holdClock?: { promise: Promise<void> } } = {}) => {
  const clock = opts.holdClock ? { settle: async () => { for (let i = 0; i < 20; i++) await new Promise(r => setTimeout(r, 2)) } } : mock.clock(on)
  if (opts.holdClock) on('clock.now', async () => { opts.entered?.(); await opts.holdClock!.promise; return { value: 0 } })
  const state: Record<string, { value: any; version: number }> = {}
  const cell = (k: string) => state[k] ?? { value: undefined, version: 0 }
  const host = { box: '', fills: [] as unknown[], copies: [] as string[], submits: 0 }
  let lostWrites = 0
  const sets: string[] = []
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.focus', () => ({ value: {} }))
  on('session.start', (_: unknown, e: any) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: any) => ({ value: { ...cell(e.key) } }))
  on('state.set', async (_: unknown, e: any) => {
    if (e.key === 'lost' && e.value && opts.holdFirstLost && lostWrites++ === 0) { opts.entered?.(); await opts.holdFirstLost.promise }
    const now = cell(e.key)
    if (e.ifVersion !== undefined && e.ifVersion !== now.version) return { value: { isSet: false, version: now.version } }
    sets.push(e.key)
    state[e.key] = { value: e.value, version: now.version + 1 }
    return { value: { isSet: true, version: now.version + 1 } }
  })
  let editsHeld = 0
  on('prompt.edit', async (_: unknown, e: any) => {
    host.box = e.text.slice(0, e.start) + e.inputText + e.text.slice(e.end)
    const out = { text: host.box, cursor: e.start + e.inputText.length }
    if (opts.holdEdit && editsHeld++ === 0) { opts.entered?.(); await opts.holdEdit.promise }
    return out
  })
  on('prompt.change', (_: unknown, e: any) => ({ text: e.text }))
  on('prompt.submit', (_: unknown, e: any) => { host.submits += 1; return { text: e.text } })
  on('prompt.fill', (_: unknown, e: any) => { host.fills.push(e); return { isFilled: false, text: host.box, cursor: host.box.length } })
  on('ui.copy', (_: unknown, e: any) => {
    if (opts.refuseCopy) return { value: { isCopied: false, reason: 'no-clipboard' } }
    host.copies.push(e.text)
    return { value: { isCopied: true } }
  })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  const type = (text: string) => $.prompt.edit({ origin: { kind: 'composer' }, text: host.box, cursor: host.box.length,
    start: host.box.length, end: host.box.length, inputText: text })
  const change = (kind: string, text = '') => { host.box = text; return $.prompt.change({ text, cursor: text.length, origin: { kind } }) }
  const submit = () => $.prompt.submit({ text: host.box, wait: false, origin: { kind: 'composer' } })
  const lost = () => cell('lost').value ?? null
  const shown = async () => {
    await clock.settle()
    const ui = await $.ui.mount(pane)
    const text = JSON.stringify(await ui.drawn())
    await ui.unmount()
    return text
  }
  const press = async (k: string) => {
    const ui = await $.ui.mount(pane)
    await ui.press({ key: `k-${k}` })
    await clock.settle()
    await ui.unmount()
  }
  const writes = () => sets.filter(k => k !== 'view')
  return { host, writes, type, change, submit, lost, shown, press, settle: clock.settle }
}

test('Ctrl+C on a draft keeps it as lost, and the Log row says so', async ($, on) => {
  const s = await start($, on)
  await s.type('a long careful prompt')
  await s.change('clear')
  expect(s.lost()?.text).toBe('a long careful prompt')
  expect(await s.shown()).toContain('Last cleared draft')
})

test('a submit whose clear comes after it records nothing', async ($, on) => {
  const s = await start($, on)
  await s.type('send this')
  await s.submit()
  await s.change('clear')
  expect(s.lost()).toBe(null)
  expect(await s.shown()).not.toContain('Last cleared draft')
})

test('a submit whose clear comes before it records nothing', async ($, on) => {
  const s = await start($, on)
  await s.type('send this')
  await s.change('clear')
  await s.submit()
  expect(s.lost()).toBe(null)
})

test('a recalled entry after a Ctrl+C, then submitted, leaves the lost draft', async ($, on) => {
  const s = await start($, on)
  await s.type('my draft')
  await s.change('clear')
  await s.change('history', 'an older prompt')
  await s.submit()
  await s.change('clear')
  expect(s.lost()?.text).toBe('my draft')
})

test('Up then Down records nothing', async ($, on) => {
  const s = await start($, on)
  await s.type('arrow-draft')
  await s.change('history', 'Reply ACK')
  await s.change('history', 'arrow-draft')
  expect(s.lost()).toBe(null)
})

test('a cleared slash command is not a lost draft', async ($, on) => {
  const s = await start($, on)
  await s.type('/clear')
  await s.change('clear')
  expect(s.lost()).toBe(null)
})

test('a stash put back drops the lost draft', async ($, on) => {
  const s = await start($, on)
  await s.type('stash-draft')
  await s.change('clear')
  expect(s.lost()?.text).toBe('stash-draft')
  await s.change('engine', 'stash-draft')
  expect(s.lost()).toBe(null)
})

test('c copies the cleared draft, never touches the prompt box, and never submits', async ($, on) => {
  const s = await start($, on)
  await s.type('bring me back')
  await s.change('clear')
  await s.type('new text')
  const before = s.host.submits
  await s.press('c')
  expect(s.host.copies).toEqual(['bring me back'])
  expect(s.host.fills).toEqual([])
  expect(s.host.box).toBe('new text')
  expect(s.host.submits).toBe(before)
  expect(s.lost()?.text).toBe('bring me back')
  expect(await s.shown()).toContain('Copied. Paste it into the prompt with Ctrl+V.')
})

test('a refused copy keeps the cleared draft and says why', async ($, on) => {
  const s = await start($, on, { refuseCopy: true })
  await s.type('keep me')
  await s.change('clear')
  await s.press('c')
  expect(s.lost()?.text).toBe('keep me')
  expect(await s.shown()).toContain('Not copied')
})

test('x forgets the lost draft', async ($, on) => {
  const s = await start($, on)
  await s.type('private words')
  await s.change('clear')
  await s.press('x')
  expect(s.lost()).toBe(null)
  expect(await s.shown()).not.toContain('Last cleared draft')
})

test('a submit that lands while its clear is still writing records nothing', async ($, on) => {
  const hold = deferred()
  const entered = deferred()
  const s = await start($, on, { holdFirstLost: hold, entered: entered.resolve })
  await s.type('send this')
  const clearing = s.change('clear')
  await entered.promise
  const submitting = s.submit()
  // Let the submit run as far as it can before the clear's write lands.
  for (let i = 0; i < 20; i++) await new Promise(r => setTimeout(r, 2))
  hold.resolve()
  await clearing
  await submitting
  await s.settle()
  expect(s.lost()).toBe(null)
})

test('typing writes nothing to session state', async ($, on) => {
  const s = await start($, on)
  await s.type('a')
  await s.type('b')
  expect(s.lost()).toBe(null)
  expect(s.writes()).toEqual([])
})

// From the review of d372767: a late event or a retried write must not undo a newer one.
test('an edit that finishes late does not replace the newer box text', async ($, on) => {
  const hold = deferred()
  const entered = deferred()
  const s = await start($, on, { holdEdit: hold, entered: entered.resolve })
  const first = s.type('first')
  await entered.promise
  await s.type(' second')
  hold.resolve()
  await first
  await s.change('clear')
  expect(s.lost()?.text).toBe('first second')
})

test('an older clear whose write retries does not replace a newer cleared draft', async ($, on) => {
  const hold = deferred()
  const entered = deferred()
  const s = await start($, on, { holdFirstLost: hold, entered: entered.resolve })
  await s.type('old draft')
  const first = s.change('clear')
  await entered.promise
  await s.type('new draft')
  await s.change('clear')
  expect(s.lost()?.text).toBe('new draft')
  hold.resolve()
  await first
  await s.settle()
  expect(s.lost()?.text).toBe('new draft')
})

// Live order on 2.1.321 (review of fbacf549): the clear arrives, then the
// submit 17 ms later, before the clear's loss write has even started.
test('a submit that arrives right after its clear, before the loss is written, records nothing', async ($, on) => {
  const s = await start($, on)
  await s.type('the submitted question')
  const clearing = s.change('clear')
  const submitting = s.submit()
  await clearing
  await submitting
  await s.settle()
  expect(s.lost()).toBe(null)
})

test('a submit that arrives while the clear reads the clock records nothing', async ($, on) => {
  const hold = deferred()
  const entered = deferred()
  const s = await start($, on, { holdClock: hold, entered: entered.resolve })
  await s.type('the submitted question')
  const clearing = s.change('clear')
  await entered.promise
  const submitting = s.submit()
  await s.settle()
  hold.resolve()
  await clearing
  await submitting
  await s.settle()
  expect(s.lost()).toBe(null)
})

for (const kind of ['history', 'plugin', 'undo']) {
  test(`a ${kind} restore that arrives while the clear reads the clock leaves no row for the restored text`, async ($, on) => {
    const hold = deferred()
    const entered = deferred()
    const s = await start($, on, { holdClock: hold, entered: entered.resolve })
    await s.type('same')
    const clearing = s.change('clear')
    await entered.promise
    const restoring = s.change(kind, 'same')
    await s.settle()
    hold.resolve()
    await clearing
    await restoring
    await s.settle()
    expect(s.lost()).toBe(null)
  })
}

test('pasting the copied draft back drops its row', async ($, on) => {
  const s = await start($, on)
  await s.type('bring me back')
  await s.change('clear')
  await s.press('c')
  await s.type('bring me back')
  expect(s.lost()).toBe(null)
  expect(await s.shown()).not.toContain('Last cleared draft')
})

test('typing the same text without a copy keeps the row', async ($, on) => {
  const s = await start($, on)
  await s.type('same words')
  await s.change('clear')
  await s.type('same words')
  expect(s.lost()?.text).toBe('same words')
})
