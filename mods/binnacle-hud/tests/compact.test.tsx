import { expect, mock, test } from 'claude-code/testing'

// M2: after a main-conversation compaction Claude gets the approved snapshot
// again, and the HUD claims only what the stored rows showed.

const NOW = Date.UTC(2026, 10, 11, 14, 2)
const LATER = NOW + 60 * 60_000
const hhmm = (ms: number) => new Date(ms).toTimeString().slice(0, 5)
const SNAP = { lines: ['ship slice 1', 'probe step 2 decides'], at: NOW }
const ROW = `Memory the operator approved at ${hhmm(NOW)}:\nship slice 1\nprobe step 2 decides`
const SUMMARY = { role: 'user' as const, text: 'Summary of the conversation so far.', toolUses: [] }

const pane = () => ({
  plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: {
    title: 'Binnacle', isFocused: true, bodyColumns: 46,
    placement: 'dock', scroll: { offset: 0, bodyRows: 32 }, view: {},
  },
}) as const

type Store = Record<string, any>
type Core = (e: any) => any

const start = async ($: any, on: any, store: Store, core: Core = () => ({ messages: [SUMMARY] })) => {
  const versions: Record<string, number> = {}
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: { key: string }) => ({ value: { value: store[e.key], version: versions[e.key] ?? 0 } }))
  on('state.set', (_: unknown, e: { key: string; value: unknown }) => {
    store[e.key] = e.value
    versions[e.key] = (versions[e.key] ?? 0) + 1
    return { value: { isSet: true, version: versions[e.key] } }
  })
  on('ui.focus', () => ({ value: {} }))
  on('session.compact', (_: unknown, e: any) => core(e))
  on('tool.call', async (_: unknown, e: any) => ({ result: { answers: { [e.questions[0].question]: 'Send' } } }))
  mock.clock(on, { now: LATER })
  mock.session(on)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
}

const compact = ($: any, extra: Record<string, unknown> = {}) =>
  $.session.compact({ trigger: 'manual', messages: [SUMMARY], ...extra })

let n = 0
const stored = ($: any, message: any, door: string, agentId?: string) =>
  $.session.append({ message, door, origin: { kind: 'model', model: 'test' }, uuid: `row-${++n}`, ...(agentId ? { agentId } : {}) })
const boundary = ($: any, agentId?: string) =>
  stored($, { type: 'system', name: 'compact_boundary', content: [{ type: 'text', text: 'Conversation compacted' }] }, 'compaction', agentId)
const userRow = ($: any, text: string, door: string, agentId?: string) =>
  stored($, { type: 'user', role: 'user', content: [{ type: 'text', text }] }, door, agentId)
const replies = ($: any) =>
  stored($, { type: 'assistant', role: 'assistant', content: [{ type: 'text', text: 'Step 2 decides the probe.' }] }, 'response')

const memoryRows = (out: any) => out.messages.filter((m: any) => m.text === ROW)
const mounted = new WeakMap<object, any>()
const drawn = async ($: any) => {
  if (!mounted.has($)) mounted.set($, await $.ui.mount(pane()))
  return mounted.get($).drawn()
}
const shown = async ($: any) => JSON.stringify(await drawn($))
// The colour of the drawn Text whose words start with `words`.
const colourOf = async ($: any, words: string) => {
  const find = (n: any): any => n?.type === 'Text' && typeof n.children?.[0] === 'string' && n.children[0].startsWith(words) ? n
    : (Array.isArray(n?.children) ? n.children : []).map(find).find(Boolean)
  return find(await drawn($))?.props.color
}

test('a main compaction with a snapshot adds exactly one Memory row, built whole', async ($, on) => {
  const store: Store = { approved: SNAP }
  await start($, on, store)
  const out = await compact($)
  expect(memoryRows(out)).toHaveLength(1)
  expect(out.messages.at(-1)).toEqual({ role: 'user', text: ROW, toolUses: [] })
})

test('the row stored after the boundary shows Re-attached with the compaction time', async ($, on) => {
  const store: Store = { approved: SNAP, memory: SNAP.lines }
  await start($, on, store)
  await compact($)
  await boundary($)
  await userRow($, SUMMARY.text, 'compaction')
  await userRow($, ROW, 'note')
  expect(store.attached.state).toBe('found')
  expect(await shown($)).toContain(`Re-attached after the compaction at ${hhmm(LATER)}.`)
  expect(await colourOf($, 'Re-attached')).toBe('success')
})

for (const extra of [{ agentId: 'sub-1' }, { trigger: 'precompute' }]) {
  test(`a compaction with ${JSON.stringify(extra)} adds nothing and records nothing`, async ($, on) => {
    const store: Store = { approved: SNAP }
    await start($, on, store)
    const out = await compact($, extra)
    expect(memoryRows(out)).toHaveLength(0)
    expect(store.attached ?? null).toBeNull()
  })
}

test('no snapshot adds nothing', async ($, on) => {
  const store: Store = { memory: ['never sent'] }
  await start($, on, store)
  const out = await compact($)
  expect(out.messages).toEqual([SUMMARY])
  expect(store.attached ?? null).toBeNull()
})

test('a skipped compaction adds nothing', async ($, on) => {
  const store: Store = { approved: SNAP }
  await start($, on, store, () => ({ skip: 'a hook said no' }))
  const out = await compact($)
  expect(out).toEqual({ skip: 'a hook said no' })
  expect(store.attached ?? null).toBeNull()
})

test('a Send that lands while the summary runs is the snapshot replayed', async ($, on) => {
  const store: Store = { approved: SNAP }
  const newer = { lines: ['model slice 2 first'], at: NOW + 5 * 60_000 }
  await start($, on, store, () => { store.approved = newer; return { messages: [SUMMARY] } })
  const out = await compact($)
  expect(out.messages.at(-1).text).toBe(`Memory the operator approved at ${hhmm(newer.at)}:\nmodel slice 2 first`)
  expect(memoryRows(out)).toHaveLength(0)
})

test('a draft edited after Send replays the snapshot, not the draft', async ($, on) => {
  const store: Store = { approved: SNAP, memory: ['edited, never sent'] }
  await start($, on, store)
  const out = await compact($)
  expect(out.messages.at(-1).text).toBe(ROW)
  expect(out.messages.some((m: any) => m.text.includes('edited, never sent'))).toBe(false)
})

test('a row the compaction already kept is not added twice', async ($, on) => {
  const store: Store = { approved: SNAP }
  const kept = { role: 'user' as const, text: ROW, toolUses: [] }
  await start($, on, store, () => ({ messages: [SUMMARY, kept] }))
  const out = await compact($)
  expect(memoryRows(out)).toHaveLength(1)
})

test('two compactions in a row each hand up one Memory row', async ($, on) => {
  const store: Store = { approved: SNAP }
  await start($, on, store)
  for (let i = 0; i < 2; i++) {
    expect(memoryRows(await compact($))).toHaveLength(1)
    await boundary($)
    await userRow($, ROW, 'note')
    expect(store.attached.state).toBe('found')
  }
})

test('a row dropped above shows Not in Claude\'s context and offers Send again', async ($, on) => {
  const store: Store = { approved: SNAP, memory: SNAP.lines }
  await start($, on, store)
  await compact($)
  await boundary($)
  await userRow($, SUMMARY.text, 'compaction')
  await replies($)
  expect(store.attached.state).toBe('missing')
  const drawn = await shown($)
  expect(drawn).toContain(`Not in Claude's context after the compaction at ${hhmm(LATER)}. Send again to restore it.`)
  expect(drawn).toContain('k-s')
})

test('with no boundary stored, the status claims nothing about delivery', async ($, on) => {
  const store: Store = { approved: SNAP, memory: SNAP.lines }
  await start($, on, store)
  await compact($)
  await replies($)
  expect(store.attached.state).toBe('waiting')
  expect(await shown($)).toContain(`Approved ${hhmm(NOW)}. Not checked after the compaction at ${hhmm(LATER)}.`)
  expect(await colourOf($, 'Approved')).toBe('#e2e0ae')
})

test('a Send Claude has is drawn in the success colour', async ($, on) => {
  await start($, on, { approved: SNAP, memory: SNAP.lines })
  expect(await colourOf($, "In Claude's context")).toBe('success')
})

test('another notice is not the boundary', async ($, on) => {
  const store: Store = { approved: SNAP }
  await start($, on, store)
  await compact($)
  await stored($, { type: 'system', name: 'local_command', content: [{ type: 'text', text: '/context' }] }, 'notice')
  await replies($)
  expect(store.attached.state).toBe('waiting')
})

test('a subagent\'s boundary and rows do not move the check', async ($, on) => {
  const store: Store = { approved: SNAP }
  await start($, on, store)
  await compact($)
  await boundary($, 'sub-1')
  await userRow($, ROW, 'note', 'sub-1')
  expect(store.attached.state).toBe('waiting')
})

test('a replay record for an older Send does not speak for a newer one', async ($, on) => {
  const newer = { lines: ['model slice 2 first'], at: NOW + 5 * 60_000 }
  const store: Store = { approved: newer, memory: newer.lines, attached: { at: LATER, approvedAt: NOW, text: ROW, state: 'found' } }
  await start($, on, store)
  const drawn = await shown($)
  expect(drawn).not.toContain('Re-attached')
  expect(drawn).toContain(`In Claude's context since ${hhmm(newer.at)}.`)
})
