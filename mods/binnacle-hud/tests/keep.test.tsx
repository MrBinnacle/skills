import { expect, mock, test } from 'claude-code/testing'

// Two ways a kept thought could lose something: a slow save clearing a newer
// draft, and a narrow layout dropping the phone mark. Both came from the
// independent review of #657 (2026-11-09).

const pane = (placement: 'dock' | 'inline', columns: number) => ({
  plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: placement === 'dock' ? 160 : columns + 2, rows: 40, isFullscreen: true },
  props: { title: 'Binnacle', isFocused: true, bodyColumns: columns, placement,
    scroll: { offset: 0, bodyRows: placement === 'dock' ? 32 : 8 }, view: {} },
}) as const

const setup = (on: any) => {
  on('command.register', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
}

for (const [placement, columns] of [['inline', 90], ['dock', 24], ['inline', 30]] as const) {
  test(`the phone mark shows in ${placement} at ${columns} columns`, { options: { narrow: 'strip' } }, async ($, on) => {
    setup(on)
    on('state.get', (_: unknown, e: { key: string }) => ({ value: {
      value: e.key === 'view' ? { ring: 1, expand: 3, failed: '' } : e.key === 'typed' ? ''
        : e.key === 'log' ? [{ text: 'saved from the phone', at: '2026-11-09T09:00:00.000Z', from: 'phone' },
           { text: 'saved here', at: '2026-11-09T09:01:00.000Z', from: 'terminal' }] : undefined, version: 1,
    } }))
    await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
    const tree = JSON.stringify(await (await $.ui.mount(pane(placement, columns))).drawn())
    expect(tree).toContain('saved from the phone')
    expect(tree).toContain('saved here')
    expect(tree.split('" phone"').length - 1).toBe(1)
  })
}

// Holds the Log write open, types a new draft (none when draft is null), then
// lets the write finish, or refuses it when fail is set.
const slowKeep = async ($: any, on: any, draft: string | null, fail = false) => {
  setup(on)
  const clock = mock.clock(on)
  const state: Record<string, { value: any; version: number }> = {
    view: { value: { ring: 1, expand: 0, failed: '' }, version: 1 },
    typed: { value: 'first capture', version: 1 }, log: { value: [], version: 1 },
    failed: { value: [], version: 1 },
  }
  let release = () => {}
  const gate = new Promise<void>(r => { release = r })
  let entered = () => {}
  const logPending = new Promise<void>(r => { entered = r })
  let stored = () => {}
  const draftStored = new Promise<void>(r => { stored = r })
  on('state.get', (_: unknown, e: { key: string }) => ({ value: { ...state[e.key] } }))
  on('state.set', async (_: unknown, e: { key: string; value: any }) => {
    if (e.key === 'log') { entered(); await gate; if (fail) return { deny: 'the disk is full' } }
    const version = state[e.key]!.version + 1
    state[e.key] = { value: e.value, version }
    if (e.key === 'typed' && e.value === draft) stored()
    return { value: { isSet: true, version } }
  })
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  const ui = await $.ui.mount(pane('dock', 46))
  const saving = $.ui.input({ plugin: 'binnacle-hud', key: 'thought', text: 'first capture' })
  await logPending
  const editing = draft === null ? Promise.resolve()
    : $.ui.input({ plugin: 'binnacle-hud', key: 'thought', text: draft, kind: 'change' })
  if (draft !== null) await draftStored
  release()
  await Promise.all([saving, editing])
  await clock.settle()
  return Object.assign(state, { ui }) as any
}

test('a slow keep does not clear a draft typed while it saved', async ($, on) => {
  const state = await slowKeep($, on, 'next draft')
  expect(state.log!.value.map((t: any) => t.text)).toEqual(['first capture'])
  expect(state.typed!.value).toBe('next draft')
})

test('a draft retyped to the kept text while the keep saved survives', async ($, on) => {
  const state = await slowKeep($, on, 'first capture')
  expect(state.log!.value.map((t: any) => t.text)).toEqual(['first capture'])
  expect(state.typed!.value).toBe('first capture')
})

test('a slow keep clears the field when nothing was typed while it saved', async ($, on) => {
  const state = await slowKeep($, on, null)
  expect(state.log!.value.map((t: any) => t.text)).toEqual(['first capture'])
  expect(state.typed!.value).toBe('')
})

test('a failed keep leaves the field and records what was not kept', async ($, on) => {
  const state = await slowKeep($, on, null, true)
  expect(state.log!.value).toEqual([])
  expect(state.typed!.value).toBe('first capture')
  expect(state.failed!.value.map((e: any) => e.text)).toEqual(['first capture'])
  await state.ui.unmount()
  const again = await $.ui.mount(pane('dock', 46))
  expect(JSON.stringify(await again.drawn())).toContain('Not kept, the save failed')
})

test('a failed keep after newer typing keeps both the new draft and the failed text', async ($, on) => {
  const state = await slowKeep($, on, 'next draft', true)
  expect(state.typed!.value).toBe('next draft')
  expect(state.failed!.value.map((e: any) => e.text)).toEqual(['first capture'])
})
