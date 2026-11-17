import { expect, mock, test } from 'claude-code/testing'

// Memory changes what Claude reads, so three harms are closed here: hidden
// characters riding into the system prompt (G5), a Send whose question hides
// its token cost (G7), and a Send that never reached Claude with no step to
// take (G6). Also the version-gated redraw (review mutant M11).

const NOW = Date.UTC(2026, 10, 17, 19, 0)
const hhmm = (ms: number) => new Date(ms).toTimeString().slice(0, 5)
const pane = () => ({
  plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: { title: 'Binnacle', isFocused: true, bodyColumns: 46, placement: 'dock', scroll: { offset: 0, bodyRows: 32 }, view: {} },
}) as const

type Store = Record<string, any>
async function start($: any, on: any, store: Store, version = '2.1.326') {
  const versions: Record<string, number> = {}
  const seen = { asked: [] as string[], fill: [] as any[], invalidated: [] as string[], toasts: [] as string[] }
  on('command.register', (_: unknown, e: { name: string }) => ({ value: { command: e.name } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.focus', () => ({ value: {} }))
  on('ui.toast', (_: unknown, e: { text: string }) => { seen.toasts.push(e.text); return { value: undefined } })
  on('ui.invalidate', (_: unknown, e: { event: string }) => { seen.invalidated.push(e.event); return { value: undefined } })
  on('session.version', () => ({ value: { version, base: version } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: { key: string }) => ({ value: { value: store[e.key], version: versions[e.key] ?? 0 } }))
  on('state.set', (_: unknown, e: { key: string; value: unknown }) => {
    store[e.key] = e.value
    versions[e.key] = (versions[e.key] ?? 0) + 1
    return { value: { isSet: true, version: versions[e.key] } }
  })
  on('tool.call', (_: unknown, e: any) => { const q = e.questions[0].question; seen.asked.push(q); return { result: { answers: { [q]: 'Send' } } } })
  on('prompt.read', () => ({ value: { text: '', cursor: 0 } }))
  on('prompt.fill', (_: unknown, e: any) => { seen.fill.push(e); return { isFilled: true } })
  on('prompt.section', (_: unknown, e: { text: string | null }) => ({ text: e.text }))
  on('turn.start', (_: unknown, e: { turnId: string }) => ({ turnId: e.turnId }))
  on('turn.complete', (_: unknown, e: { answer: string }) => ({ text: e.answer }))
  const clock = mock.clock(on, { now: NOW })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  return { seen, clock }
}

const mounted = async ($: any, act: (ui: any) => Promise<void>) => { const ui = await $.ui.mount(pane()); await act(ui); await ui.unmount() }
const drawn = async ($: any) => { let t = ''; await mounted($, async ui => { t = JSON.stringify(await ui.drawn()) }); return t }
const press = ($: any, key: string) => mounted($, ui => ui.press({ key }))
const type = ($: any, text: string) => mounted($, ui => ui.input({ key: 'thought', text, kind: 'change' }))
const turn = async ($: any, id: string) => {
  await $.turn.start({ text: 'main', turnId: id })
  await $.turn.complete({ answer: '', durationMs: 1, isAborted: false, reason: 'answer', turnId: id })
}
const HIDDEN = '​‮⁦\u{E0041}'

test('a Memory line added from the field holds no hidden characters', async ($, on) => {
  const store: Store = {}
  await start($, on, store)
  await type($, `ship${HIDDEN} slice 1`)
  await press($, 'k-a')
  expect(store.memory.map((l: any) => l.text)).toEqual(['ship slice 1'])
})

test('a Log thought copied to Memory holds no hidden characters', async ($, on) => {
  const store: Store = { log: [{ text: `probe${HIDDEN} step 2`, at: '2026-11-17T18:00:00.000Z', from: 'phone' }], typed: '' }
  await start($, on, store)
  await press($, 'k-p')
  expect(store.memory.map((l: any) => l.text)).toEqual(['probe step 2'])
})

test('the 2000-character cut counts visible characters, so hidden ones cannot push a line over', async ($, on) => {
  const store: Store = {}
  const s = await start($, on, store)
  const full = 'a'.repeat(2000)
  await type($, `${full}${'​'.repeat(50)}`)
  await press($, 'k-a')
  expect(store.memory[0].text).toBe(full)
  expect(s.seen.toasts).toEqual([])
})

test('a field holding only hidden characters adds no line', async ($, on) => {
  const store: Store = {}
  await start($, on, store)
  await type($, HIDDEN)
  await press($, 'k-a')
  expect(store.memory ?? []).toEqual([])
})

test('the Send question states the prompt cache cost', async ($, on) => {
  const s = await start($, on, { memory: [{ id: 'm1', text: 'ship slice 1' }] })
  await press($, 'k-s')
  expect(s.seen.asked.length).toBe(1)
  expect(s.seen.asked[0]).toContain('prompt cache')
})

test('a Send no turn carried names a next step, and q puts the lines in the prompt box', async ($, on) => {
  const store: Store = { memory: [{ id: 'm1', text: 'ship slice 1' }] }
  const s = await start($, on, store)
  await press($, 'k-s')
  await turn($, 't1') // the turn ran, and no memory section was asked for
  const tree = await drawn($)
  expect(tree).toContain('Press q')
  await press($, 'k-q')
  expect(s.seen.fill.length).toBe(1)
  expect(s.seen.fill[0].mode).toBe('append')
  expect(s.seen.fill[0].text).toContain('ship slice 1')
  expect(s.seen.fill[0].text).toContain(hhmm(NOW))
})

test('a Send the next turn carried shows no next step', async ($, on) => {
  await start($, on, { memory: [{ id: 'm1', text: 'ship slice 1' }] })
  await press($, 'k-s')
  await $.turn.start({ text: 'main', turnId: 't1' })
  await $.prompt.section({ name: 'memory', text: 'core' })
  await $.turn.complete({ answer: '', durationMs: 1, isAborted: false, reason: 'answer', turnId: 't1' })
  const tree = await drawn($)
  expect(tree).not.toContain('Press q')
  expect(tree).not.toContain('k-q')
})

test('a turn that started before the Send does not count as one that missed it', async ($, on) => {
  const s = await start($, on, { memory: [{ id: 'm1', text: 'ship slice 1' }] })
  await $.turn.start({ text: 'main', turnId: 't1' })
  await s.clock.advance(1000)
  await press($, 'k-s')
  await $.turn.complete({ answer: '', durationMs: 1, isAborted: false, reason: 'answer', turnId: 't1' })
  expect(await drawn($)).not.toContain('Press q')
})

test('a subagent turn does not count as one that missed the Send', async ($, on) => {
  await start($, on, { memory: [{ id: 'm1', text: 'ship slice 1' }] })
  await press($, 'k-s')
  await $.turn.start({ text: 'sub', turnId: 's1', agentId: 'a1' })
  await $.turn.complete({ answer: '', durationMs: 1, isAborted: false, reason: 'answer', turnId: 's1', agentId: 'a1' })
  expect(await drawn($)).not.toContain('Press q')
})

test('a subagent that starts after the Send, inside an earlier main turn, does not make it count', async ($, on) => {
  const s = await start($, on, { memory: [{ id: 'm1', text: 'ship slice 1' }] })
  await $.turn.start({ text: 'main', turnId: 't1' })
  await s.clock.advance(1000)
  await press($, 'k-s')
  await $.turn.start({ text: 'sub', turnId: 's1', agentId: 'a1' })
  await $.turn.complete({ answer: '', durationMs: 1, isAborted: false, reason: 'answer', turnId: 's1', agentId: 'a1' })
  await $.turn.complete({ answer: '', durationMs: 1, isAborted: false, reason: 'answer', turnId: 't1' })
  expect(await drawn($)).not.toContain('Press q')
})

test('on 2.1.326 session start redraws the pane once the version allows three-line rows', async ($, on) => {
  const s = await start($, on, {})
  expect(s.seen.invalidated).toContain('ui.render')
})

test('on 2.1.325 session start asks for no redraw', async ($, on) => {
  const s = await start($, on, {}, '2.1.325')
  expect(s.seen.invalidated).not.toContain('ui.render')
})
