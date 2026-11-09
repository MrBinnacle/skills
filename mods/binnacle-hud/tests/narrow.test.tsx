import { expect, test } from 'claude-code/testing'

const pane = (placement: 'dock' | 'inline', viewport: { columns: number; rows: number; isFullscreen?: boolean }) => ({
  plugin: 'binnacle-hud',
  component: 'Pane',
  requestId: 'binnacle-hud',
  surface: 'terminal',
  viewport,
  props: {
    title: 'Binnacle', isFocused: false, bodyColumns: placement === 'dock' ? 46 : 90,
    placement, scroll: { offset: 0, bodyRows: 32 }, view: {},
  },
}) as const

const shown = async (ui: { drawn: () => Promise<unknown> }) => JSON.stringify(await ui.drawn())

const hud = (args: string, isFullscreen = true, columns = 160) =>
  ({ command: 'hud', args, origin: { kind: 'composer' }, presentation: { isFullscreen, columns } }) as const

const start = async ($: any, on: any) => {
  on('command.register', () => ({ value: { command: 'hud' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('state.get', () => ({ value: { value: { shape: 'scene-2', value: 2 }, version: 1 } }))
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
}

test('hide, narrow window: one line naming the width to reach', async ($, on) => {
  await start($, on)
  const ui = await $.ui.mount(pane('inline', { columns: 96, rows: 40, isFullscreen: true }))
  expect(await shown(ui)).toMatch(/needs 110 columns, now 96/)
  expect(await shown(ui)).not.toMatch(/"Watch"/)
})

test('hide, main screen: one line naming /tui fullscreen', async ($, on) => {
  await start($, on)
  const ui = await $.ui.mount(pane('inline', { columns: 200, rows: 40, isFullscreen: false }))
  expect(await shown(ui)).toMatch(/\/tui fullscreen/)
})

test('hide, docked: the full HUD', async ($, on) => {
  await start($, on)
  const ui = await $.ui.mount(pane('dock', { columns: 160, rows: 40, isFullscreen: true }))
  expect(await shown(ui)).toMatch(/"Watch"/)
  expect(await shown(ui)).not.toMatch(/side panel/)
})

test('strip, narrow window: the full strip above the prompt', { options: { narrow: 'strip' } }, async ($, on) => {
  await start($, on)
  const ui = await $.ui.mount(pane('inline', { columns: 96, rows: 40, isFullscreen: true }))
  expect(await shown(ui)).not.toMatch(/side panel/)
  expect(await shown(ui)).toMatch(/ . watch /)
})

test('/hud narrow strip stores the setting', async ($, on) => {
  const sets: unknown[] = []
  on('config.set', (_, e) => { sets.push(e); return { value: e.value } })
  await start($, on)
  const { text } = await $.command.run(hud('narrow strip'))
  expect(text).toContain('show as a strip above the prompt')
  expect(JSON.stringify(sets)).toContain('binnacle-hud.narrow')
})

test('/hud narrow with no value says the current choice', async ($, on) => {
  await start($, on)
  const { text } = await $.command.run(hud('narrow'))
  expect(text).toContain('will hide')
})

test('/hud in a narrow window says the width to reach', async ($, on) => {
  await start($, on)
  const { text } = await $.command.run(hud('', true, 96))
  expect(text).toContain('needs 110 columns, now 96')
})

test('/hud off fullscreen names /tui fullscreen', async ($, on) => {
  await start($, on)
  const { text } = await $.command.run(hud('', false, 200))
  expect(text).toContain('/tui fullscreen')
})

test('/hud with room to dock says it is beside the chat', async ($, on) => {
  await start($, on)
  const { text } = await $.command.run(hud('', true, 160))
  expect(text).toContain('ready to type')
})
