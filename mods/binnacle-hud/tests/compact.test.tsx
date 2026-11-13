import { expect, mock, test } from 'claude-code/testing'

// After a main-conversation compaction Claude gets the approved snapshot
// again, and the HUD claims only what the stored rows showed.

const NOW = Date.UTC(2026, 10, 11, 14, 2)
const LATER = NOW + 60 * 60_000
const hhmm = (ms: number) => new Date(ms).toTimeString().slice(0, 5)
const SNAP = { lines: ['ship slice 1', 'probe step 2 decides'], at: NOW }
const ROW = `Memory the operator approved at ${hhmm(NOW)}:\nship slice 1\nprobe step 2 decides`
const SUMMARY = { role: 'user' as const, text: 'Summary of the conversation so far.', toolUses: [] }
const LIGHT = '#e2e0ae'
const WARNING = '#d0493a'

const pane = () => ({
  plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: {
    title: 'Binnacle', isFocused: true, bodyColumns: 46,
    placement: 'dock', scroll: { offset: 0, bodyRows: 32 }, view: {},
  },
}) as const

type Store = Record<string, any>
type Opts = { core?: (e: any) => any; beneath?: (on: any) => void; failRead?: (key: string) => boolean }

const start = async ($: any, on: any, store: Store, opts: Opts = {}) => {
  const core = opts.core ?? (() => ({ messages: [SUMMARY] }))
  const versions: Record<string, number> = {}
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: { key: string }) => {
    if (opts.failRead?.(e.key)) throw new Error('state.get failed')
    return { value: { value: store[e.key], version: versions[e.key] ?? 0 } }
  })
  on('state.set', (_: unknown, e: { key: string; value: unknown }) => {
    store[e.key] = e.value
    versions[e.key] = (versions[e.key] ?? 0) + 1
    return { value: { isSet: true, version: versions[e.key] } }
  })
  on('ui.focus', { plugin: '*' }, () => ({ value: {} }))
  on('session.compact', (_: unknown, e: any) => core(e))
  on('tool.call', async (_: unknown, e: any) => ({ result: { answers: { [e.questions[0].question]: 'Send' } } }))
  mock.clock(on, { now: LATER })
  opts.beneath?.(on)
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
const installed = async ($: any) => {
  await boundary($)
  await userRow($, SUMMARY.text, 'compaction')
}

const memoryRows = (out: any) => out.messages.filter((m: any) => m.text === ROW)
const mounted = new WeakMap<object, any>()
const drawn = async ($: any) => {
  if (!mounted.has($)) mounted.set($, await $.ui.mount(pane()))
  return mounted.get($).drawn()
}
const shown = async ($: any) => JSON.stringify(await drawn($))
const statusNode = async ($: any, words: string) => {
  const find = (n: any): any => n?.type === 'Text' && typeof n.children?.[0] === 'string' && n.children[0].startsWith(words) ? n
    : (Array.isArray(n?.children) ? n.children : []).map(find).find(Boolean)
  return find(await drawn($))?.props
}

test('a main compaction with a snapshot adds exactly one Memory row, built whole', async ($, on) => {
  await start($, on, { approved: SNAP })
  const out = await compact($)
  expect(memoryRows(out)).toHaveLength(1)
  expect(out.messages.at(-1)).toEqual({ role: 'user', text: ROW, toolUses: [] })
})

test('the row stored after the boundary shows Re-attached in the success colour, with no Send', async ($, on) => {
  const store: Store = { approved: SNAP, memory: SNAP.lines }
  await start($, on, store)
  await compact($)
  await installed($)
  await userRow($, ROW, 'note')
  await replies($)
  expect(store.attached.state).toBe('found')
  const text = await shown($)
  expect(text).toContain(`Re-attached after the compaction at ${hhmm(LATER)}.`)
  expect(text).not.toContain('k-s')
  expect((await statusNode($, 'Re-attached')).color).toBe('success')
})

for (const extra of [{ agentId: 'sub-1' }, { trigger: 'precompute' }]) {
  test(`a compaction with ${JSON.stringify(extra)} adds nothing`, async ($, on) => {
    await start($, on, { approved: SNAP })
    expect(memoryRows(await compact($, extra))).toHaveLength(0)
  })
}

test('no snapshot adds nothing', async ($, on) => {
  await start($, on, { memory: ['never sent'] })
  expect((await compact($)).messages).toEqual([SUMMARY])
})

test('a skipped compaction adds nothing', async ($, on) => {
  await start($, on, { approved: SNAP }, { core: () => ({ skip: 'a hook said no' }) })
  expect(await compact($)).toEqual({ skip: 'a hook said no' })
})

test('a Send that lands while the summary runs is the snapshot replayed', async ($, on) => {
  const store: Store = { approved: SNAP }
  const newer = { lines: ['model slice 2 first'], at: NOW + 5 * 60_000 }
  await start($, on, store, { core: () => { store.approved = newer; return { messages: [SUMMARY] } } })
  const out = await compact($)
  expect(out.messages.at(-1).text).toBe(`Memory the operator approved at ${hhmm(newer.at)}:\nmodel slice 2 first`)
})

test('a draft edited after Send replays the snapshot, not the draft', async ($, on) => {
  await start($, on, { approved: SNAP, memory: ['edited, never sent'] })
  const out = await compact($)
  expect(out.messages.at(-1).text).toBe(ROW)
  expect(out.messages.some((m: any) => m.text.includes('edited, never sent'))).toBe(false)
})

test('the row is added even when the summary kept one, so the check can see it stored', async ($, on) => {
  const kept = { role: 'user' as const, text: ROW, toolUses: [] }
  await start($, on, { approved: SNAP }, { core: () => ({ messages: [SUMMARY, kept] }) })
  const out = await compact($)
  expect(memoryRows(out)).toHaveLength(2)
  expect(out.messages.at(-1).text).toBe(ROW)
})

test('two compactions in a row are each checked', async ($, on) => {
  const store: Store = { approved: SNAP }
  await start($, on, store)
  for (let i = 0; i < 2; i++) {
    expect(memoryRows(await compact($))).toHaveLength(1)
    await boundary($)
    expect(store.attached.state).toBe('checking')
    await userRow($, ROW, 'note')
    expect(store.attached.state).toBe('found')
  }
})

test('a row dropped above shows Not in Claude\'s context in the warning colour and offers Send', async ($, on) => {
  const store: Store = { approved: SNAP, memory: SNAP.lines }
  await start($, on, store)
  await compact($)
  await installed($)
  await replies($)
  expect(store.attached.state).toBe('missing')
  const text = await shown($)
  expect(text).toContain(`Not in Claude's context after the compaction at ${hhmm(LATER)}. Send again to give Claude these lines.`)
  expect(text).toContain('k-s')
  expect((await statusNode($, "Not in Claude's context")).color).toBe(WARNING)
})

test('a prompt stored before the row also means the row never arrived', async ($, on) => {
  const store: Store = { approved: SNAP }
  await start($, on, store)
  await compact($)
  await installed($)
  await userRow($, 'what does step 2 decide?', 'prompt')
  expect(store.attached.state).toBe('missing')
})

test('an older Memory row kept by the summary does not count as the replay', async ($, on) => {
  const store: Store = { approved: SNAP }
  await start($, on, store)
  await compact($)
  await boundary($)
  await userRow($, `Memory the operator approved at ${hhmm(NOW - 60_000)}:\nold line`, 'compaction')
  await replies($)
  expect(store.attached.state).toBe('missing')
})

test('between the boundary and the row the status claims nothing, quietly, with no Send', async ($, on) => {
  const store: Store = { approved: SNAP, memory: SNAP.lines }
  await start($, on, store)
  await compact($)
  await boundary($)
  const text = await shown($)
  expect(text).toContain(`Approved ${hhmm(NOW)}. Not checked after the compaction at ${hhmm(LATER)}.`)
  expect(text).not.toContain('k-s')
  const props = await statusNode($, 'Approved')
  expect(props.color).toBeUndefined()
  expect(props.dimColor).toBe(true)
})

test('lines edited before the check ends still claim nothing about Claude, and offer Send', async ($, on) => {
  const store: Store = { approved: SNAP, memory: SNAP.lines }
  await start($, on, store)
  await compact($)
  await boundary($)
  store.memory = [...SNAP.lines, 'a third line']
  const text = await shown($)
  expect(text).toContain(`Approved ${hhmm(NOW)}. Not checked after the compaction at ${hhmm(LATER)}.`)
  expect(text).not.toContain('Claude has the')
  expect(text).toContain('k-s')
})

test('another notice is not the boundary', async ($, on) => {
  const store: Store = { approved: SNAP }
  await start($, on, store)
  await compact($)
  await stored($, { type: 'system', name: 'local_command', content: [{ type: 'text', text: '/context' }] }, 'notice')
  await replies($)
  expect(store.attached ?? null).toBeNull()
})

test('a subagent\'s boundary and rows do not start a check', async ($, on) => {
  const store: Store = { approved: SNAP }
  await start($, on, store)
  await compact($)
  await boundary($, 'sub-1')
  await userRow($, ROW, 'note', 'sub-1')
  expect(store.attached ?? null).toBeNull()
})

test('a replay record for an older Send does not speak for a newer one', async ($, on) => {
  const newer = { lines: ['model slice 2 first'], at: NOW + 5 * 60_000 }
  await start($, on, { approved: newer, memory: newer.lines, attached: { at: NOW + 60_000, approvedAt: NOW, text: ROW, state: 'found' } })
  const text = await shown($)
  expect(text).not.toContain('Re-attached')
  expect(text).toContain(`In Claude's context since ${hhmm(newer.at)}.`)
})

test('a row rewritten by a hook beneath is checked as stored, not as it arrived', async ($, on) => {
  const store: Store = { approved: SNAP, memory: SNAP.lines }
  await start($, on, store, {
    beneath: (under: any) => under('session.append', { door: 'note' }, (_: unknown, e: any, next: any) =>
      next({ ...e, message: { ...e.message, content: [{ type: 'text', text: '[scrubbed]' }] } })),
  })
  await compact($)
  await installed($)
  await userRow($, ROW, 'note')
  expect(store.attached.state).toBe('checking')
  await replies($)
  expect(store.attached.state).toBe('missing')
})

test('a compact hook that cannot read the Send record still ends in Not in Claude\'s context', async ($, on) => {
  const store: Store = { approved: SNAP, memory: SNAP.lines }
  let compacting = false
  await start($, on, store, {
    core: () => { compacting = true; return { messages: [SUMMARY] } },
    failRead: key => compacting && key === 'approved',
  })
  const out = await compact($)
  compacting = false
  expect(memoryRows(out)).toHaveLength(0)
  await installed($)
  await replies($)
  expect(await shown($)).toContain("Not in Claude's context after the compaction")
})

test('lines edited after a found replay say Changed since Send, and offer Send', async ($, on) => {
  const store: Store = { approved: SNAP, memory: SNAP.lines }
  await start($, on, store)
  await compact($)
  await installed($)
  await userRow($, ROW, 'note')
  store.memory = [...SNAP.lines, 'a third line']
  const text = await shown($)
  expect(text).toContain(`Changed since Send. Claude has the ${hhmm(NOW)} version.`)
  expect(text).toContain('k-s')
  expect((await statusNode($, 'Changed since Send')).color).toBe(LIGHT)
})

test('a refused Send after a lost replay draws the refusal', async ($, on) => {
  await start($, on, {
    approved: SNAP, memory: SNAP.lines,
    attached: { at: LATER, approvedAt: NOW, text: ROW, state: 'missing' },
    view: { ring: 0, expand: 0, failed: 'policy says no', refusedLines: SNAP.lines },
  })
  expect(await shown($)).toContain('Not sent. policy says no')
})

test('a Send the HUD could not record is not replaced by an older replay', async ($, on) => {
  const store: Store = { approved: SNAP, memory: ['newer line'], view: { ring: 0, expand: 0, failed: '', unrecorded: NOW + 10 * 60_000 } }
  await start($, on, store)
  const out = await compact($)
  expect(memoryRows(out)).toHaveLength(0)
  await installed($)
  await replies($)
  expect(store.view.unrecorded).toBe(0)
  const text = await shown($)
  expect(text).not.toContain('Claude has the lines sent at')
  expect(text).toContain("Not in Claude's context after the compaction")
})

test('Not sent is drawn quietly', async ($, on) => {
  await start($, on, { memory: ['never sent'] })
  const props = await statusNode($, 'Not sent.')
  expect(props.color).toBeUndefined()
  expect(props.dimColor).toBe(true)
})

test('a Send Claude has is drawn in the success colour', async ($, on) => {
  await start($, on, { approved: SNAP, memory: SNAP.lines })
  expect((await statusNode($, "In Claude's context")).color).toBe('success')
})

// Found by an independent verifier: Send B's row is stored before the boundary,
// and B's record lands after the compact hook and the boundary read Send A.
test('a Send recorded after the compaction replayed an older Send is not claimed in context', async ($, on) => {
  const newer = { lines: ['model slice 2 first'], at: NOW + 5 * 60_000 }
  const store: Store = { approved: SNAP, memory: newer.lines }
  await start($, on, store)
  await userRow($, `Memory the operator approved at ${hhmm(newer.at)}:\nmodel slice 2 first`, 'note')
  const out = await compact($)
  expect(out.messages.at(-1).text).toBe(ROW)
  await installed($)
  await userRow($, ROW, 'note')
  store.approved = newer
  await replies($)
  const text = await shown($)
  expect(text).not.toContain("In Claude's context since")
  expect(text).toContain("Not in Claude's context after the compaction")
  expect(text).toContain('k-s')
})

test('a Send in the same millisecond as a compaction that replayed an older Send is not claimed', async ($, on) => {
  const newer = { lines: ['model slice 2 first'], at: LATER }
  await start($, on, { approved: newer, memory: newer.lines, attached: { at: LATER, approvedAt: NOW, text: ROW, state: 'found' } })
  const text = await shown($)
  expect(text).not.toContain("In Claude's context since")
  expect(text).toContain("Not in Claude's context after the compaction")
})

// A re-Send after a compaction that missed the lines lands, but its record
// fails. Claude read that Send, so its notice outranks the missing replay.
test('a re-Send whose record failed after a missed replay says Claude has the lines', async ($, on) => {
  const resent = LATER + 5 * 60_000
  await start($, on, {
    approved: SNAP, memory: SNAP.lines,
    attached: { at: LATER, approvedAt: NOW, text: ROW, state: 'missing' },
    view: { ring: 0, expand: 0, failed: '', unrecorded: resent },
  })
  const text = await shown($)
  expect(text).toContain(`Claude has the lines sent at ${hhmm(resent)}. The HUD could not record that Send.`)
  expect(text).not.toContain("Not in Claude's context")
})

// The Send record cannot be read across the compaction and its boundary, so
// nothing is replayed and the boundary saw no Send. The HUD saw nothing stored
// after the compaction, so it must not claim the lines are in context.
test('a Send record unreadable at the boundary is not claimed in context', async ($, on) => {
  const store: Store = { approved: SNAP, memory: SNAP.lines }
  let failing = false
  await start($, on, store, { failRead: key => failing && key === 'approved' })
  failing = true
  const out = await compact($)
  await boundary($)
  failing = false
  expect(memoryRows(out)).toHaveLength(0)
  await userRow($, SUMMARY.text, 'compaction')
  await replies($)
  const text = await shown($)
  expect(text).not.toContain("In Claude's context since")
  expect(text).toContain("Not in Claude's context after the compaction")
})

test('a compaction with no Send at all still says Not sent.', async ($, on) => {
  await start($, on, { memory: SNAP.lines })
  await compact($)
  await installed($)
  await replies($)
  const text = await shown($)
  expect(text).toContain('Not sent.')
  expect(text).not.toContain("Not in Claude's context")
})
