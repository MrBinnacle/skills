import { expect, mock, test } from 'claude-code/testing'

// Round 5. The HUD keeps no copy of the prompt box: Claude Code brings a
// cleared draft back with Up. And the pane never says more than the stores
// hold: a refused write leaves the press settled and the words true.

const pane = { plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: { title: 'Binnacle', isFocused: true, bodyColumns: 46, placement: 'dock', scroll: { offset: 0, bodyRows: 32 }, view: {} } } as const

async function start($: any, on: any, seed: Record<string, unknown> = {}, answer = 'Send') {
  const clock = mock.clock(on, { now: Date.UTC(2026, 10, 10, 12, 0) })
  const cells: Record<string, { value: any; version: number }> = Object.fromEntries(Object.entries(seed).map(([k, value]) => [k, { value, version: 1 }]))
  const cell = (k: string) => cells[k] ?? { value: undefined, version: 0 }
  const denied = new Set<string>()
  const sets: string[] = []
  let box = ''
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.focus', () => ({ value: {} }))
  on('session.start', (_: any, e: any) => ({ cwd: e.cwd }))
  on('state.get', (_: any, e: any) => ({ value: { ...cell(e.key) } }))
  on('state.set', (_: any, e: any) => {
    if (denied.has(e.key)) return { deny: `injected ${e.key} failure` }
    const old = cell(e.key)
    if (e.ifVersion !== undefined && e.ifVersion !== old.version) return { value: { isSet: false, version: old.version } }
    sets.push(e.key)
    cells[e.key] = { value: e.value, version: old.version + 1 }
    return { value: { isSet: true, version: old.version + 1 } }
  })
  on('prompt.edit', (_: any, e: any) => { box = e.text.slice(0, e.start) + e.inputText + e.text.slice(e.end); return { text: box, cursor: box.length } })
  on('prompt.change', (_: any, e: any) => ({ text: e.text }))
  on('prompt.submit', (_: any, e: any) => ({ text: e.text }))
  on('tool.call', (_: any, e: any) => ({ result: { answers: { [e.questions[0].question]: answer } } }))
  const session = mock.session(on)
  let deny = ''
  on('session.append', { door: 'note' }, (_: any, e: any, next: any) => deny ? { deny } : next(e))
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  const drawn = async () => { const ui = await $.ui.mount(pane); const d = JSON.stringify(await ui.drawn()); await ui.unmount(); return d }
  const press = async (k: string) => { const ui = await $.ui.mount(pane); await ui.press({ key: `k-${k}` }); await clock.settle(); await ui.unmount() }
  return { cells, cell, denied, sets, session, refuseAppend: (why: string) => { deny = why }, settle: clock.settle, drawn, press,
    type: (text: string) => $.prompt.edit({ origin: { kind: 'composer' }, text: box, cursor: box.length, start: box.length, end: box.length, inputText: text }),
    change: (kind: string, text = '') => { box = text; return $.prompt.change({ text, cursor: text.length, origin: { kind } }) } }
}

const ids = (v: any[]) => v.map(e => typeof e === 'string' ? `bare:${e}` : e.id)

test('round5: a cleared prompt draft is not copied into session state or shown in the pane', async ($, on) => {
  const s = await start($, on)
  await s.type('a long careful prompt')
  await s.change('clear')
  await s.settle()
  expect(s.sets).toEqual([])
  const d = await s.drawn()
  expect(d).not.toContain('a long careful prompt')
  expect(d).not.toContain('Last cleared draft')
})

test('round5: no 0 key is drawn, whatever the line shown last', async ($, on) => {
  const ten = Array.from({ length: 10 }, (_, i) => ({ id: `r${i + 1}`, text: `line ${i + 1}` }))
  const s = await start($, on, { memory: ten })
  // A 4.1.0 module still writing after this one started.
  s.cells.memory = { value: [...ten, 'bare eleventh'], version: 9 }
  expect(await s.drawn()).not.toContain('"k-0"')
  await s.press('0').catch(() => undefined)
  expect(ids(s.cell('memory').value)).toEqual([...ten.map(l => l.id), 'bare:bare eleventh'])
})

test('round5: removing line 1 of ten brings the tenth into reach of 9', async ($, on) => {
  const ten = Array.from({ length: 10 }, (_, i) => ({ id: `r${i + 1}`, text: 'same text' }))
  const s = await start($, on, { memory: ten })
  await s.press('1')
  await s.press('9')
  expect(ids(s.cell('memory').value)).toEqual(ten.slice(1, 9).map(l => l.id))
})

test('round5: a refused Send is not shown once the lines equal what Claude has again', async ($, on) => {
  const s = await start($, on, { memory: [{ id: 'a', text: 'keep tests green' }], view: { ring: 2, expand: 1, failed: '' } })
  await s.press('s')
  s.cells.typed = { value: 'second line', version: 2 }
  await s.press('a')
  s.refuseAppend('the session is read-only')
  await s.press('s')
  expect(await s.drawn()).toContain('Not sent. the session is read-only')
  await s.press('2')
  const d = await s.drawn()
  expect(d).toContain("In Claude's context since")
  expect(d).not.toContain('Not sent.')
})

test('round5: a adds the field text the pane drew, not a newer value the store holds', async ($, on) => {
  const s = await start($, on, { typed: 'milk' })
  const ui = await $.ui.mount(pane)
  s.cells.typed = { value: 'milk!', version: 2 }
  await ui.press({ key: 'k-a' })
  await s.settle()
  await ui.unmount()
  expect(s.cell('memory').value.map((e: any) => e.text)).toEqual(['milk'])
})

test('round5: a whose Memory write is refused settles and leaves the field text', async ($, on) => {
  const s = await start($, on, { typed: 'milk' })
  s.denied.add('memory')
  await s.press('a')
  expect(s.cell('typed').value).toBe('milk')
  expect(s.cell('memory').value ?? []).toEqual([])
})

test('round5: p whose Memory write is refused settles and changes nothing', async ($, on) => {
  const s = await start($, on, { log: [{ text: 'a thought', at: new Date(0).toISOString(), from: 'terminal' }], memory: [{ id: 'm1', text: 'first' }] })
  s.denied.add('memory')
  await s.press('p')
  expect(s.cell('memory').value).toEqual([{ id: 'm1', text: 'first' }])
})

test('round5: a landed Send whose view write fails does not show an older refusal beside it', async ($, on) => {
  const s = await start($, on, { memory: [{ id: 'a', text: 'ship it' }], view: { ring: 2, expand: 0, failed: 'earlier refusal' } })
  s.denied.add('view')
  await s.press('s')
  expect(s.session.appended().length).toBe(1)
  const d = await s.drawn()
  expect(d).toContain("In Claude's context since")
  expect(d).not.toContain('earlier refusal')
})

test('round5: a landed Send whose snapshot and view writes both fail still says Claude has the lines', async ($, on) => {
  const s = await start($, on, { memory: [{ id: 'a', text: 'ship it' }] })
  s.denied.add('approved')
  s.denied.add('view')
  await s.press('s')
  expect(s.session.appended().length).toBe(1)
  const d = await s.drawn()
  expect(d).toContain('Claude has the lines sent at')
  expect(d).not.toContain('Not sent.')
})

test('round5: /log says nothing is shown when the Log write and the failed-keep write are both refused', async ($, on) => {
  const s = await start($, on, {}, 'call the venue')
  s.denied.add('log')
  s.denied.add('failed')
  const out = JSON.stringify(await $.command.run({ command: 'log', args: '', origin: { kind: 'bridge' } }))
  expect(out).not.toContain('shown in the HUD')
  expect(out).toContain('Not kept')
})

test('round5 control: /log with only the Log write refused says the HUD shows it, and it does', async ($, on) => {
  const s = await start($, on, {}, 'call the venue')
  s.denied.add('log')
  const out = JSON.stringify(await $.command.run({ command: 'log', args: '', origin: { kind: 'bridge' } }))
  expect(out).toContain('shown in the HUD')
  expect(s.cell('failed').value.map((e: any) => e.text)).toEqual(['call the venue'])
})
