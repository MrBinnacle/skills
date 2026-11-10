import { expect, mock, test } from 'claude-code/testing'

// The interleaving sweep. Each HUD action is started, held at one awaited host
// call, raced by one newer event that makes a record with the same text, then
// released. The invariant: nothing made after the action arrived is gone or
// changed, and the action changed no record but the one it targeted. Cases are
// generated from ACTIONS x hold points x newer events; the trace test for each
// action fails when the action reaches a host call its hold list lacks.

type D = { promise: Promise<void>; resolve: () => void }
const deferred = (): D => { let resolve!: () => void; const promise = new Promise<void>(r => { resolve = r }); return { promise, resolve } }
const pane = { plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: { title: 'Binnacle', isFocused: true, bodyColumns: 46, placement: 'dock', scroll: { offset: 0, bodyRows: 32 }, view: {} } } as const
const T0 = Date.UTC(2026, 10, 9, 12, 0)

async function begin($: any, on: any, seed: Record<string, unknown> = {}) {
  const cells: Record<string, { value: any; version: number }> = Object.fromEntries(Object.entries(seed).map(([k, value]) => [k, { value, version: 1 }]))
  const cell = (k: string) => cells[k] ?? { value: undefined, version: 0 }
  let box = '', denied = false
  let gate: { call: string; nth: number; seen: number; entered: D; release: D } | null = null
  let trace: string[] | null = null
  // Every awaited host call a hold can stop: state.get and state.set by key, clock.now, ui.copy.
  const hit = async (call: string) => {
    trace?.push(call)
    const g = gate
    if (!g || g.call !== call || ++g.seen !== g.nth) return
    gate = null
    g.entered.resolve()
    await g.release.promise
  }
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.focus', () => ({ value: {} }))
  on('session.start', (_: any, e: any) => ({ cwd: e.cwd }))
  // An event takes one hook, so the kit's clock.now hook is wrapped to make it holdable.
  const clock = mock.clock(((event: string, ...rest: any[]) => {
    const hook = rest.pop()
    return on(event, ...rest, event === 'clock.now' ? async (...args: any[]) => { await hit('clock.now'); return hook(...args) } : hook)
  }) as any, { now: T0 })
  on('ui.copy', async () => { await hit('ui.copy'); return { value: { isCopied: true } } })
  // The value is read after the hold, as a backend snapshots it when the call reaches it.
  on('state.get', async (_: any, e: any) => { await hit(`state.get ${e.key}`); return { value: { ...cell(e.key) } } })
  on('state.set', async (_: any, e: any) => {
    await hit(`state.set ${e.key}`)
    if (denied && e.key === 'log') return { deny: 'injected keep failure' }
    const old = cell(e.key)
    if (e.ifVersion !== undefined && e.ifVersion !== old.version) return { value: { isSet: false, version: old.version } }
    cells[e.key] = { value: e.value, version: old.version + 1 }
    return { value: { isSet: true, version: old.version + 1 } }
  })
  // The hook chain is a hold point too: the mod awaits these as `next(e)` before it applies the event.
  on('prompt.edit', async (_: any, e: any) => {
    const text = box = e.text.slice(0, e.start) + e.inputText + e.text.slice(e.end)
    await hit('prompt.edit')
    return { text, cursor: text.length }
  })
  on('prompt.change', async (_: any, e: any) => { await hit('prompt.change'); return { text: e.text } })
  on('prompt.submit', (_: any, e: any) => ({ text: e.text }))
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  return {
    cell, settle: clock.settle, deny: () => { denied = true },
    hold: (point: string) => {
      const [call, nth] = point.split(' #')
      const g = { call: call!, nth: Number(nth), seen: 0, entered: deferred(), release: deferred() }
      gate = g
      return g
    },
    record: () => { trace = [] },
    stop: () => {
      const n: Record<string, number> = {}
      const points = (trace ?? []).map(call => `${call} #${n[call] = (n[call] ?? 0) + 1}`)
      trace = null
      return points
    },
    type: (text: string) => $.prompt.edit({ origin: { kind: 'composer' }, text: box, cursor: box.length, start: 0, end: box.length, inputText: text }),
    change: (kind: string, text = '') => { box = text; return $.prompt.change({ text, cursor: text.length, origin: { kind } }) },
    submit: () => $.prompt.submit({ text: box, wait: false, origin: { kind: 'composer' } }),
    mount: (surface: 'terminal' | 'desktop' = 'terminal') => $.ui.mount({ ...pane, surface }),
  }
}

type Fx = Awaited<ReturnType<typeof begin>>
type Ctx = { s: Fx; ui?: any; text: string; targets: string[] }

// Each record by its identity, mapped to its content.
const records = (s: Fx) => {
  const m = new Map<string, string>()
  const lost = s.cell('lost').value
  if (lost) m.set(`lost ${lost.load}:${lost.moves}`, JSON.stringify(lost))
  for (const e of s.cell('memory').value ?? []) m.set(`memory ${e.id}`, JSON.stringify(e))
  for (const e of s.cell('failed').value ?? []) m.set(`failed ${e.id}`, JSON.stringify(e))
  ;(s.cell('log').value ?? []).forEach((t: any, i: number) => m.set(`log #${i + 1}`, JSON.stringify(t)))
  return m
}

// before: as the action arrived. mid: after the newer event. end: once all settled.
// A record the newer event itself replaced (a clear replaces `lost`) is the newer event's doing.
const violations = (before: Map<string, string>, mid: Map<string, string>, end: Map<string, string>, targets: string[]) => {
  const out: string[] = []
  for (const [k, v] of mid) {
    if (end.get(k) === v) continue
    const state = end.has(k) ? 'changed' : 'gone'
    if (!before.has(k)) out.push(`${k}, made after the action arrived, is ${state}`)
    else if (!targets.includes(k)) out.push(`${k}, not the action's target, is ${state}`)
  }
  return out
}

// The action's own drawing holds the terminal, so a newer event acts on a second surface.
const fresh = async (c: Ctx, act: (n: any) => Promise<unknown>) => { const n = await c.s.mount('desktop'); await act(n); await n.unmount() }
const NEWER: Record<string, (c: Ctx) => Promise<unknown>> = {
  'clear of the same draft': async c => { await c.s.type(c.text); await c.s.change('clear') },
  'failed keep of the same text': c => { c.s.deny(); return fresh(c, n => n.input({ key: 'thought', text: c.text })) },
  'Log thought of the same text': c => fresh(c, n => n.input({ key: 'thought', text: c.text })),
  // Makes no record, so a late event whose own record never lands is visible.
  'edit of other text': c => c.s.type('other text'),
  'Memory line of the same text': async c => {
    await fresh(c, n => n.input({ key: 'thought', text: c.text, kind: 'change' }))
    await fresh(c, n => n.press({ key: 'k-a' }))
  },
}

const DRAFT = 'same draft', LINE = 'same line', THOUGHT = 'same thought'
const lostKey = (s: Fx) => `lost ${s.cell('lost').value.load}:${s.cell('lost').value.moves}`
const cleared = async (c: Ctx) => { await c.s.type(c.text); await c.s.change('clear'); c.targets = [lostKey(c.s)] }
const drawn = async (c: Ctx) => { c.ui = await c.s.mount() }
const seeded = (texts: string[]) => texts.map((text, i) => ({ id: `seed-${i + 1}`, text }))
const press = (k: string) => (c: Ctx) => c.ui.press({ key: `k-${k}` })

type Action = { name: string; text: string; seed?: Record<string, unknown>; targets?: string[]
  // A draft the action must leave recoverable as the cleared draft.
  keeps?: string
  holds: string[]; newer: string[]; setup?: (c: Ctx) => Promise<void>; run: (c: Ctx) => Promise<unknown>; after?: (c: Ctx) => Promise<unknown> }

const LOST_CAS = ['state.get lost #1', 'state.set lost #1']
const ACTIONS: Action[] = [
  ...['history', 'plugin', 'undo'].map((kind): Action => ({
    name: `restore (${kind})`, text: DRAFT, holds: ['prompt.change #1', 'state.get lost #1', 'state.get lost #2', 'state.set lost #1'],
    newer: ['clear of the same draft'], setup: cleared, run: c => c.s.change(kind, c.text) })),
  { name: 'paste of the copied draft', text: DRAFT, holds: ['prompt.edit #1', ...LOST_CAS], newer: ['clear of the same draft'],
    setup: async c => { await cleared(c); await drawn(c); await press('c')(c) }, run: c => c.s.type(c.text) },
  { name: 'submit from the composer after its clear', text: DRAFT, holds: LOST_CAS, newer: ['clear of the same draft'],
    setup: cleared, run: c => c.s.submit() },
  { name: 'submit from the composer before its clear', text: DRAFT, holds: LOST_CAS, newer: ['clear of the same draft'],
    setup: async c => { await c.s.type(c.text) }, run: c => c.s.submit() },
  // A copy changes no record; the paste after it is where the copied record is used.
  { name: 'c (copy draft), then paste', text: DRAFT, holds: ['ui.copy #1', 'state.get view #1', 'state.set view #1'],
    newer: ['clear of the same draft'], setup: async c => { await cleared(c); await drawn(c) }, run: press('c'), after: c => c.s.type(c.text) },
  { name: 'x (forget draft)', text: DRAFT, holds: [...LOST_CAS, 'state.get view #1', 'state.set view #1'],
    newer: ['clear of the same draft'], setup: async c => { await cleared(c); await drawn(c) }, run: press('x') },
  { name: 'd (dismiss failed)', text: THOUGHT, holds: ['state.get failed #1', 'state.set failed #1'], newer: ['failed keep of the same text'],
    setup: async c => {
      c.s.deny(); await fresh(c, n => n.input({ key: 'thought', text: c.text }))
      c.targets = (c.s.cell('failed').value ?? []).map((e: any) => `failed ${e.id}`); await drawn(c)
    }, run: press('d') },
  { name: 'remove key 1', text: LINE, seed: { memory: seeded([LINE, 'other line']) }, targets: ['memory seed-1'],
    holds: ['state.get memory #1', 'state.set memory #1'], newer: ['Memory line of the same text'], setup: drawn, run: press('1') },
  { name: 'remove key 0', text: LINE, seed: { memory: seeded([...Array.from({ length: 9 }, (_, i) => `line ${i + 1}`), LINE]) }, targets: ['memory seed-10'],
    holds: ['state.get memory #1', 'state.set memory #1'], newer: ['Memory line of the same text'], setup: drawn, run: press('0') },
  { name: 'p (last thought to memory)', text: THOUGHT, seed: { log: [{ text: THOUGHT, at: new Date(T0).toISOString(), from: 'terminal' }] },
    holds: ['state.get memory #1', 'state.set memory #1'], newer: ['Memory line of the same text', 'Log thought of the same text'],
    setup: drawn, run: press('p') },
  { name: 'a (to memory)', text: LINE, seed: { typed: LINE },
    holds: ['state.get typed #1', 'state.get memory #1', 'state.set memory #1', 'state.get typed #2', 'state.set typed #1'],
    newer: ['Memory line of the same text'], setup: drawn, run: press('a') },
  { name: 'Enter keep', text: THOUGHT, holds: ['state.get log #1', 'state.set log #1', 'state.get typed #1', 'state.set typed #1'],
    newer: ['Log thought of the same text'], setup: drawn, run: c => c.ui.input({ key: 'thought', text: c.text }) },
  { name: 'failed keep', text: THOUGHT, holds: ['state.get log #1', 'state.set log #1', 'state.get failed #1', 'state.set failed #1'],
    newer: ['failed keep of the same text'], setup: async c => { c.s.deny(); await drawn(c) }, run: c => c.ui.input({ key: 'thought', text: c.text }) },
  // Beyond the brief's list: the one action that awaits clock.now.
  { name: 'clear of a typed draft', text: DRAFT, holds: ['prompt.change #1', 'clock.now #1', ...LOST_CAS], keeps: DRAFT,
    newer: ['clear of the same draft', 'edit of other text'],
    setup: async c => { await c.s.type(c.text) }, run: c => c.s.change('clear') },
]

const prepare = async ($: any, on: any, a: Action) => {
  const c: Ctx = { s: await begin($, on, a.seed), text: a.text, targets: a.targets ?? [] }
  await a.setup?.(c)
  return c
}

for (const a of ACTIONS) {
  test(`sweep trace: ${a.name} awaits exactly its hold points, and alone keeps the invariant`, async ($, on) => {
    const c = await prepare($, on, a)
    const before = records(c.s)
    c.s.record()
    await a.run(c)
    await c.s.settle()
    const points = c.s.stop()
    await a.after?.(c)
    await c.s.settle()
    expect(violations(before, before, records(c.s), c.targets)).toEqual([])
    expect(c.targets.filter(t => records(c.s).has(t))).toEqual([])
    if (a.keeps) expect(c.s.cell('lost').value?.text).toBe(a.keeps)
    expect(points).toEqual(a.holds)
    await c.ui?.unmount()
  })
  for (const point of a.holds) for (const n of a.newer) {
    test(`sweep: ${a.name} | held at ${point} | then a newer ${n}`, async ($, on) => {
      const c = await prepare($, on, a)
      const before = records(c.s)
      const g = c.s.hold(point)
      const running = Promise.resolve(a.run(c))
      const reached = await Promise.race([g.entered.promise.then(() => true), running.then(() => false)])
      expect(reached ? point : `${point} never reached`).toBe(point)
      const held = records(c.s)
      await NEWER[n]!(c)
      const mid = records(c.s)
      expect([...mid.keys()].filter(k => !held.has(k)).length).toBe(n === 'edit of other text' ? 0 : 1)
      g.release.resolve()
      await running
      await c.s.settle()
      await a.after?.(c)
      await c.s.settle()
      expect(violations(before, mid, records(c.s), c.targets)).toEqual([])
      expect(c.targets.filter(t => records(c.s).has(t))).toEqual([])
      if (a.keeps) expect(c.s.cell('lost').value?.text).toBe(a.keeps)
      await c.ui?.unmount()
    })
  }
}
