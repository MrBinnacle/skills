import { expect, mock, test } from 'claude-code/testing'

// /clear and /resume reset session state, and no session.start follows. The
// mod reads what it may keep in session.end and writes it back once the new
// session runs, so a clear no longer erases what the operator handed the HUD.
// The approved Memory snapshot is never carried: by ruling, Memory is
// approved for one conversation.

const NOW = Date.UTC(2026, 10, 17, 20, 0)
const AT = '2026-11-17T19:00:00.000Z'
const THOUGHT = { text: 'rename the flag', at: AT, from: 'terminal' }
const LINE = { id: 'm1', text: 'ship slice 1' }
const NOTE = { line: 'Your release pin still names v4.1.1.', explanation: '' }
const SNAP = { lines: ['ship slice 1'], at: NOW - 1000 }

const seeded = () => ({
  log: [THOUGHT],
  failed: [{ id: 'f1', text: 'a keep that failed' }],
  memory: [LINE],
  typed: 'half a thought',
  approved: SNAP,
  delivered: { at: SNAP.at, since: SNAP.at },
  headsups: { waiting: [NOTE], done: ['an earlier note'] },
  view: { ring: 0, expand: 0, failed: '', missed: SNAP.at },
})

async function start($: any, on: any, store: Record<string, any>, resets = true) {
  const versions: Record<string, number> = {}
  on('command.register', (_: unknown, e: { name: string }) => ({ value: { command: e.name } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  // The engine's own reset: every key of the ending session is gone.
  on('session.end', (_: unknown, e: { sessionId: string }) => { if (resets) for (const k of Object.keys(store)) delete store[k]; return { sessionId: e.sessionId } })
  on('state.get', (_: unknown, e: { key: string }) => ({ value: { value: store[e.key], version: versions[e.key] ?? 0 } }))
  on('state.set', (_: unknown, e: { key: string; value: unknown }) => {
    store[e.key] = e.value
    versions[e.key] = (versions[e.key] ?? 0) + 1
    return { value: { isSet: true, version: versions[e.key] } }
  })
  const clock = mock.clock(on, { now: NOW })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  const end = async (reason: string, between?: () => void) => {
    await $.session.end({ reason, sessionId: 's1', resume: { id: 's1' } })
    between?.()
    await clock.advance(1)
  }
  return { end }
}

test('after /clear the heads-ups, thoughts, failed keeps, draft and field come back, and the approved Memory does not', async ($, on) => {
  const store: Record<string, any> = seeded()
  const s = await start($, on, store)
  await s.end('clear')
  expect(store.log).toEqual([THOUGHT])
  expect(store.failed).toEqual([{ id: 'f1', text: 'a keep that failed' }])
  expect(store.memory).toEqual([LINE])
  expect(store.typed).toBe('half a thought')
  expect(store.headsups).toEqual({ waiting: [NOTE], done: ['an earlier note'] })
  expect(store.approved).toBeUndefined()
  expect(store.delivered).toBeUndefined()
  expect(store.view).toBeUndefined()
})

test('after /resume the thoughts and draft come back, and the heads-ups of the old conversation do not', async ($, on) => {
  const store: Record<string, any> = seeded()
  const s = await start($, on, store)
  await s.end('resume')
  expect(store.log).toEqual([THOUGHT])
  expect(store.memory).toEqual([LINE])
  expect(store.headsups).toBeUndefined()
  expect(store.approved).toBeUndefined()
})

for (const reason of ['logout', 'prompt_input_exit', 'other']) {
  test(`a session that ends for ${reason} restores nothing`, async ($, on) => {
    const store: Record<string, any> = seeded()
    const s = await start($, on, store)
    await s.end(reason)
    expect(store).toEqual({})
  })
}

test('the restore merges into what the new session already holds, so nothing is lost or doubled', async ($, on) => {
  const store: Record<string, any> = seeded()
  const s = await start($, on, store)
  await $.session.end({ reason: 'clear', sessionId: 's1', resume: { id: 's1' } })
  // Written in the new session before the restore lands.
  const fresh = { text: 'a thought after the clear', at: '2026-11-17T20:00:01.000Z', from: 'phone' }
  store.log = [fresh]
  store.typed = 'new typing'
  store.headsups = { waiting: [{ line: 'A newer note.', explanation: '' }], done: [] }
  await s.end('clear') // a second end before the first restore ran
  expect(store.log).toEqual([THOUGHT, fresh])
  expect(store.typed).toBe('new typing')
  expect(store.memory).toEqual([LINE])
  expect(store.headsups.waiting.map((n: any) => n.line)).toEqual([NOTE.line, 'A newer note.'])
})

test('an empty session carries nothing back', async ($, on) => {
  const store: Record<string, any> = {}
  const s = await start($, on, store)
  await s.end('clear')
  expect(store).toEqual({})
})

test('text typed in the new session before the restore lands is kept', async ($, on) => {
  const store: Record<string, any> = seeded()
  const s = await start($, on, store)
  await s.end('clear', () => { store.typed = 'typed right after the clear' })
  expect(store.typed).toBe('typed right after the clear')
})

test('a heads-up sent in the new session before the restore lands is not listed again', async ($, on) => {
  const store: Record<string, any> = seeded()
  const s = await start($, on, store)
  await s.end('clear', () => { store.headsups = { waiting: [], done: [NOTE.line] } })
  expect(store.headsups.waiting).toEqual([])
  expect(store.headsups.done).toEqual(['an earlier note', NOTE.line])
})

// Whether /resume resets session state was not probed; if it does not, nothing doubles.
test('an end that leaves state in place doubles nothing', async ($, on) => {
  const store: Record<string, any> = seeded()
  const s = await start($, on, store, false)
  await s.end('resume')
  expect(store.log).toEqual([THOUGHT])
  expect(store.failed).toEqual([{ id: 'f1', text: 'a keep that failed' }])
  expect(store.memory).toEqual([LINE])
})
