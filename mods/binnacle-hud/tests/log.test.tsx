import { expect, test } from 'claude-code/testing'

// /log is the phone's way in: the question dialog draws there, and what is
// typed under Other reaches the mod without entering the conversation.

const start = async ($: any, on: any, answer: string | undefined, sets: Record<string, unknown[]>, asked: string[] = []) => {
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('state.get', (_: unknown, e: { key: string }) => ({ value: { value: e.key === 'log' ? [] : '', version: 1 } }))
  on('state.set', (_: unknown, e: { key: string; value: unknown }) => { (sets[e.key] ??= []).push(e.value); return { value: { isSet: true, version: 2 } } })
  on('tool.call', (_: unknown, e: any) => {
    asked.push(e.questions[0].question)
    return answer === undefined ? { deny: 'dismissed' } : { result: { answers: { [e.questions[0].question]: answer } } }
  })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
}

const run = ($: any, kind: 'bridge' | 'composer', args = '') =>
  $.command.run({ command: 'log', args, origin: { kind } })

test('a thought typed under Other on the phone is kept, marked phone, and not echoed', async ($, on) => {
  const sets: Record<string, unknown[]> = {}
  await start($, on, 'call the venue about the 14th', sets)
  const out = await run($, 'bridge')
  const kept = sets.log as { text: string; from: string }[][]
  expect(kept.at(-1)!.map(t => [t.text, t.from])).toEqual([['call the venue about the 14th', 'phone']])
  expect(JSON.stringify(out)).not.toContain('venue')
  expect(sets.typed).toBeUndefined()
})

test('a /log from the terminal is marked terminal', async ($, on) => {
  const sets: Record<string, unknown[]> = {}
  await start($, on, 'a terminal thought', sets)
  await run($, 'composer')
  expect((sets.log as { from: string }[][]).at(-1)![0]!.from).toBe('terminal')
})

for (const label of ['Not now', 'Cancel']) {
  test(`choosing ${label} keeps nothing`, async ($, on) => {
    const sets: Record<string, unknown[]> = {}
    await start($, on, label, sets)
    await run($, 'bridge')
    expect(sets.log).toBeUndefined()
  })
}

test('a dismissed dialog keeps nothing', async ($, on) => {
  const sets: Record<string, unknown[]> = {}
  await start($, on, undefined, sets)
  expect(JSON.stringify(await run($, 'bridge'))).toContain('Nothing kept')
  expect(sets.log).toBeUndefined()
})

test('text after /log is refused unasked and not echoed, since the command line is recorded', async ($, on) => {
  const sets: Record<string, unknown[]> = {}
  const asked: string[] = []
  await start($, on, 'x', sets, asked)
  const out = await run($, 'bridge', 'secret plan')
  expect(asked).toEqual([])
  expect(sets.log).toBeUndefined()
  expect(JSON.stringify(out)).not.toContain('secret')
})
