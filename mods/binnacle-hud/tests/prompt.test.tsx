import { expect, mock, test } from 'claude-code/testing'

// What Claude reads: after a confirmed Send the approved lines join Claude
// Code's own `memory` section of the system prompt, on every request.

const NOW = Date.UTC(2026, 10, 13, 14, 2)
const hhmm = (ms: number) => new Date(ms).toTimeString().slice(0, 5)
const LINES = ['ship slice 1', 'probe step 2 decides']
const MEMORY = `Memory the operator approved at ${hhmm(NOW)}:\nship slice 1\nprobe step 2 decides`
const CORE = 'Contents of CLAUDE.md: run the tests before a commit.'

const pane = (placement: 'dock' | 'inline' = 'dock') => ({
  plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: {
    title: 'Binnacle', isFocused: true, bodyColumns: placement === 'dock' ? 46 : 90,
    placement, scroll: { offset: 0, bodyRows: 32 }, view: {},
  },
}) as const

type Store = Record<string, any>
type Opts = { answer?: string; deny?: string }

const start = async ($: any, on: any, store: Store, opts: Opts = {}) => {
  const versions: Record<string, number> = {}
  const invalidated: string[] = []
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: { key: string }) => ({ value: { value: store[e.key], version: versions[e.key] ?? 0 } }))
  on('state.set', (_: unknown, e: { key: string; value: unknown }) => {
    if (e.key === opts.deny) return { deny: 'policy says no' }
    store[e.key] = e.value
    versions[e.key] = (versions[e.key] ?? 0) + 1
    return { value: { isSet: true, version: versions[e.key] } }
  })
  on('ui.focus', () => ({ value: {} }))
  on('ui.invalidate', (_: unknown, e: { event: string }) => { invalidated.push(e.event); return { value: undefined } })
  on('prompt.section', (_: unknown, e: { text: string | null }) => ({ text: e.text }))
  on('tool.call', (_: unknown, e: any) => ({ result: { answers: { [e.questions[0].question]: opts.answer ?? 'Send' } } }))
  mock.clock(on, { now: NOW })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  return { invalidated }
}

const section = ($: any, text: string | null = CORE) => $.prompt.section({ name: 'memory', text })
const send = async ($: any) => { const ui = await $.ui.mount(pane()); await ui.press({ key: 'k-s' }); await ui.unmount() }
const shown = async ($: any, placement: 'dock' | 'inline' = 'dock') => {
  const ui = await $.ui.mount(pane(placement))
  const tree = await ui.drawn()
  await ui.unmount()
  return tree
}
const statusProps = async ($: any, words: string) => {
  const find = (n: any): any => n?.type === 'Text' && typeof n.children?.[0] === 'string' && n.children[0].startsWith(words) ? n
    : (Array.isArray(n?.children) ? n.children : []).map(find).find(Boolean)
  return find(await shown($))?.props
}

test('before any Send, the memory section is the engine\'s own and keeps the cache', async ($, on) => {
  await start($, on, { memory: LINES })
  expect(await section($)).toEqual({ text: CORE })
  expect(await section($, null)).toEqual({ text: null })
})

test('a confirmed Send adds the lines after the engine\'s text and asks the next turn for them', async ($, on) => {
  const s = await start($, on, { memory: LINES })
  await send($)
  expect(await section($)).toEqual({ text: `${CORE}\n\n${MEMORY}`, breakPromptCache: true })
  expect(await section($, null)).toEqual({ text: MEMORY, breakPromptCache: true })
  expect(s.invalidated).toEqual(['prompt.section'])
  expect(JSON.stringify(await shown($))).toContain(`In Claude's instructions since ${hhmm(NOW)}.`)
})

test('a Send leaves every other section of the prompt as the engine wrote it', async ($, on) => {
  await start($, on, { memory: LINES })
  await send($)
  expect(await $.prompt.section({ name: 'env_info_simple', text: 'Platform: win32' })).toEqual({ text: 'Platform: win32' })
})

test('Send answered Not now leaves Claude\'s prompt alone', async ($, on) => {
  const s = await start($, on, { memory: LINES }, { answer: 'Not now' })
  await send($)
  expect(await section($)).toEqual({ text: CORE })
  expect(s.invalidated).toEqual([])
})

test('an edit after Send keeps the sent version until the next Send', async ($, on) => {
  const store: Store = { memory: LINES }
  const s = await start($, on, store)
  await send($)
  store.memory = [...LINES, 'added later']
  expect((await section($)).text).toBe(`${CORE}\n\n${MEMORY}`)
  expect(JSON.stringify(await shown($))).toContain(`Changed since Send. Claude has the ${hhmm(NOW)} version.`)
  await send($)
  expect((await section($)).text).toBe(`${CORE}\n\n${MEMORY}\nadded later`)
  expect(s.invalidated).toEqual(['prompt.section', 'prompt.section'])
})

test('a Send whose snapshot write is refused gives Claude nothing and says why', async ($, on) => {
  const s = await start($, on, { memory: LINES }, { deny: 'approved' })
  await send($)
  expect(await section($)).toEqual({ text: CORE })
  expect(s.invalidated).toEqual([])
  const text = JSON.stringify(await shown($))
  expect(text).toContain('Not sent.')
  expect(text).toContain('policy says no')
})

test('the collapsed strip says a refused Send was not sent, with the reason', { options: { narrow: 'strip' } }, async ($, on) => {
  await start($, on, { memory: LINES }, { deny: 'approved' })
  await send($)
  expect(JSON.stringify(await shown($, 'inline'))).toMatch(/memory Not sent\. [^"]*policy says no/)
})

// 4.1.1 stored `view.unrecorded`; main's unreleased compaction code stored
// `attached` and drew Watch at expand 2. None of it may break the pane.
test('state an earlier version stored draws, and its Send still reaches Claude', { options: { narrow: 'strip' } }, async ($, on) => {
  await start($, on, {
    memory: LINES,
    approved: { lines: LINES, at: NOW },
    attached: { at: NOW, approvedAt: NOW, text: MEMORY, state: 'checking' },
    view: { ring: 2, expand: 2, failed: '', unrecorded: NOW },
  })
  expect(JSON.stringify(await shown($))).toContain(`In Claude's instructions since ${hhmm(NOW)}.`)
  const strip = JSON.stringify(await shown($, 'inline'))
  expect(strip).toContain('"Log"')
  expect(strip).not.toContain('could not record')
  expect((await section($)).text).toBe(`${CORE}\n\n${MEMORY}`)
})

test('Not sent is drawn quietly', async ($, on) => {
  await start($, on, { memory: ['never sent'] })
  const props = await statusProps($, 'Not sent.')
  expect(props.color).toBeUndefined()
  expect(props.dimColor).toBe(true)
})

test('a Send Claude has is drawn in the success colour', async ($, on) => {
  await start($, on, { approved: { lines: LINES, at: NOW }, memory: LINES })
  expect((await statusProps($, "In Claude's instructions")).color).toBe('success')
})

test('lines changed since Send are drawn in the board\'s light, not the success colour', async ($, on) => {
  await start($, on, { approved: { lines: LINES, at: NOW }, memory: [...LINES, 'added later'] })
  expect((await statusProps($, 'Changed since Send.')).color).toBe('#e2e0ae')
})
