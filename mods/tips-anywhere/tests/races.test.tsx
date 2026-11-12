import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'
import type { Engine } from 'claude-code/testing'

import { cardText } from '../hooks/register'

// Races between a read and a write of the waiting heads-up.

const SESSION = 'this-session'
const TIP = { line: 'A real note.', explanation: 'real details' }
const tips = ($: Engine, args = '') =>
  $.command.run({ command: 'tips', args, origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 40 } })
const flush = async () => { for (let i = 0; i < 3000; i++) await Promise.resolve() }
const deferred = () => { let resolve = () => {}; const promise = new Promise<void>(r => { resolve = r }); return { promise, resolve } }

async function engine($: Engine, on: On, holdRead = false) {
  const toasts: string[] = []
  let asks = 0
  let store: any = { sessions: [] }
  const demoSleep = deferred()
  const reads: ReturnType<typeof deferred>[] = []
  let hold = holdRead
  on('env.get', (_$, e) => ({ value: e.name === 'USERPROFILE' ? 'C:/Users/me' : undefined }))
  on('fs.list', () => ({ value: [{ name: 'cc-plugin-you-should-know_builtin-1.json', kind: 'file', size: 1, mtimeMs: 0, isLink: false }] }))
  on('fs.read', async () => {
    if (hold) { const d = deferred(); reads.push(d); await d.promise }
    return { value: JSON.stringify(store) }
  })
  on('session.id', () => ({ value: SESSION }))
  on('session.surfaces', () => ({ value: [] }))
  on('command.register', () => ({ value: { command: 'tips' } }))
  on('session.start', (_$, e) => ({ cwd: e.cwd }))
  on('prompt.submit', (_$, e) => ({ text: e.text }))
  on('ui.toast', (_$, e) => { toasts.push(e.text); return { value: undefined } })
  on('tool.call', (_$, e) => { if (e.tool === 'AskUserQuestion') asks += 1; return { result: 'sent' } })
  on('clock.sleep', async (_$, e) => { if (e.ms === 8000) await demoSleep.promise; return { value: undefined } })
  on('clock.now', () => ({ value: 1_000_000_000 }))
  on('turn.start', (_$, e) => ({ turnId: e.turnId }))
  on('turn.complete', (_$, e) => ({ text: e.answer }))
  on('tool.check', () => ({ decision: 'allow' as const }))
  const startHeld = hold
  hold = false
  await $.session.start({ cwd: '/', surface: 'mobile', isInteractive: true })
  hold = startHeld
  const turnEnds = async (id: string) => {
    await $.turn.start({ text: 'main', turnId: id })
    await $.turn.complete({ answer: '', durationMs: 1, isAborted: false, reason: 'answer', turnId: id })
  }
  return { toasts, asks: () => asks, demoSleep, reads, turnEnds, offerNow: (o: any) => { store = { sessions: [{ id: SESSION, view: { kind: 'offer', ...o } }] } } }
}

test('a real heads-up that arrives during the sample delay survives the sample', { options: { deliver: 'computer' } }, async ($, on) => {
  const p = await engine($, on)
  expect((await tips($, 'demo')).text).toContain('sample heads-up arrives')
  p.offerNow(TIP)
  await p.turnEnds('t1')
  await flush()
  expect({ before: (await tips($)).text }).toEqual({ before: cardText(TIP) })
  p.demoSleep.resolve()
  await flush()
  expect((await tips($)).text).toBe(cardText(TIP))
})

test('two scans of one heads-up deliver and ask about it once', { options: { deliver: 'buttons' } }, async ($, on) => {
  const p = await engine($, on, true)
  p.offerNow(TIP)
  await p.turnEnds('t1')
  await p.turnEnds('t2')
  await flush()
  expect(p.reads.length).toBe(2)
  p.reads.forEach(r => r.resolve())
  await flush()
  expect({ toasts: p.toasts.filter(t => t.includes(TIP.line)).length, asks: p.asks() }).toEqual({ toasts: 1, asks: 1 })
})

test('a heads-up skipped while a scan is between its two steps does not come back', { options: { deliver: 'computer' } }, async ($, on) => {
  const store: Record<string, unknown> = {}
  const versions: Record<string, number> = {}
  let pause: ReturnType<typeof deferred> | null = null
  let paused = false
  on('state.get', async (_: unknown, e: { key: string }) => {
    const read = { value: { value: store[e.key], version: versions[e.key] ?? 0 } }
    if (e.key === 'outcomes' && pause && !paused) { paused = true; await pause.promise }
    return read
  })
  on('state.set', (_: unknown, e: { key: string; value: unknown }) => {
    const version = (versions[e.key] ?? 0) + 1
    store[e.key] = e.value
    versions[e.key] = version
    return { value: { isSet: true as const, version } }
  })
  const p = await engine($, on, true)
  p.offerNow(TIP)
  await p.turnEnds('t1')
  await flush()
  p.reads.splice(0).forEach(r => r.resolve())
  await flush()
  expect((await tips($)).text).toBe(cardText(TIP))
  await p.turnEnds('t2')
  await flush()
  expect(p.reads.length).toBe(1)
  pause = deferred()
  p.reads[0]!.resolve()
  await flush()
  expect(paused).toBe(true)
  expect((await tips($, 'skip')).text).toContain('Dismissed')
  pause.resolve()
  await flush()
  expect({ toasts: p.toasts.filter(t => t.includes(TIP.line)).length, waiting: (await tips($)).text === cardText(TIP) })
    .toEqual({ toasts: 1, waiting: false })
})

// The clear after offer()'s re-read removes only the heads-up that scan wrote.
const X = { line: 'Note X.', explanation: 'x' }
const Y = { line: 'Note Y.', explanation: 'y' }

test('a heads-up offered while an older scan re-reads the outcomes survives that scan', { options: { deliver: 'computer' } }, async ($, on) => {
  const state: Record<string, unknown> = {}
  const versions: Record<string, number> = {}
  const pauses: ReturnType<typeof deferred>[] = []
  let armed = 0
  on('state.get', async (_: unknown, e: { key: string }) => {
    const read = { value: { value: state[e.key], version: versions[e.key] ?? 0 } }
    if (e.key === 'outcomes' && armed > 0) { armed -= 1; const d = deferred(); pauses.push(d); await d.promise }
    return read
  })
  on('state.set', (_: unknown, e: { key: string; value: unknown }) => {
    const version = (versions[e.key] ?? 0) + 1
    state[e.key] = e.value
    versions[e.key] = version
    return { value: { isSet: true as const, version } }
  })
  let store: any = { sessions: [] }
  const reads: ReturnType<typeof deferred>[] = []
  let hold = false
  on('env.get', (_$, e) => ({ value: e.name === 'USERPROFILE' ? 'C:/Users/me' : undefined }))
  on('fs.list', () => ({ value: [{ name: 'cc-plugin-you-should-know_builtin-1.json', kind: 'file', size: 1, mtimeMs: 0, isLink: false }] }))
  on('fs.read', async () => {
    if (hold) { const d = deferred(); reads.push(d); await d.promise }
    return { value: JSON.stringify(store) }
  })
  on('session.id', () => ({ value: SESSION }))
  on('session.surfaces', () => ({ value: [] }))
  on('command.register', () => ({ value: { command: 'tips' } }))
  on('session.start', (_$, e) => ({ cwd: e.cwd }))
  on('prompt.submit', (_$, e) => ({ text: e.text }))
  on('ui.toast', () => ({ value: undefined }))
  on('tool.call', () => ({ result: 'sent' }))
  on('clock.sleep', () => ({ value: undefined }))
  on('clock.now', () => ({ value: 1_000_000_000 }))
  on('turn.start', (_$, e) => ({ turnId: e.turnId }))
  on('turn.complete', (_$, e) => ({ text: e.answer }))
  on('tool.check', () => ({ decision: 'allow' as const }))
  await $.session.start({ cwd: '/', surface: 'mobile', isInteractive: true })
  const offerNow = (o: any) => { store = { sessions: [{ id: SESSION, view: { kind: 'offer', ...o } }] } }
  const turnEnds = async (id: string) => {
    await $.turn.start({ text: 'main', turnId: id })
    await $.turn.complete({ answer: '', durationMs: 1, isAborted: false, reason: 'answer', turnId: id })
  }

  // X is offered and shown.
  offerNow(X)
  await turnEnds('t1')
  await flush()
  expect((await tips($)).text).toBe(cardText(X))

  // A scan of X stops at its first read of the outcomes.
  hold = true
  await turnEnds('t2')
  await flush()
  armed = 1
  reads.splice(0).forEach(r => r.resolve())
  await flush()
  expect(pauses.length).toBe(1)
  hold = false

  // X is skipped while the scan waits; the scan then writes X and stops at its re-read.
  expect((await tips($, 'skip')).text).toContain('Dismissed')
  armed = 1
  pauses[0]!.resolve()
  await flush()
  expect(pauses.length).toBe(2)

  // Y arrives and is written while the old scan waits at its re-read.
  offerNow(Y)
  await turnEnds('t3')
  await flush()
  expect({ during: (await tips($)).text }).toEqual({ during: cardText(Y) })

  // The old scan's re-read sees X settled and clears X only.
  pauses[1]!.resolve()
  await flush()
  expect((await tips($)).text).toBe(cardText(Y))
})
