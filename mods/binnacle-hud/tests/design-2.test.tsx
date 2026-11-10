import { expect, test } from 'claude-code/testing'

// Mounts the pane in every Memory state, docked and inline, with and without
// the keys, on the terminal. The one thing this proves: no tree is refused (a
// refused Pane tree closes the pane in a live session). It proves nothing
// about paint, hover or focus: only the terminal shows those.

const PANE = {
  plugin: 'binnacle-hud',
  component: 'Pane',
  requestId: 'binnacle-hud',
  surface: 'terminal',
  props: {
    title: 'Binnacle',
    isFocused: false,
    bodyColumns: 46,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 32 },
    view: {},
  },
} as const

const PLACEMENTS = [
  { placement: 'dock', bodyColumns: 46 },
  { placement: 'dock', bodyColumns: 24 },
  { placement: 'inline', bodyColumns: 90 },
] as const

const SENT = { lines: ['ship slice 1'], at: 0 }
const STATES: Record<string, Record<string, unknown>> = {
  empty: {},
  unsent: { memory: ['ship slice 1', 'probe step 2 decides'] },
  sent: { memory: ['ship slice 1'], approved: SENT },
  changed: { memory: ['ship slice 1', 'model slice 2'], approved: SENT },
  refused: { memory: ['ship slice 1'], view: { ring: 2, expand: 1, failed: 'policy says no', refusedLines: ['ship slice 1'] } },
  typing: { memory: ['ship slice 1'], typed: 'a line in the field' },
}

for (const [name, state] of Object.entries(STATES)) {
  test(`memory ${name} mounts in every placement, focused or not`, async ($, on) => {
    on('command.register', () => ({ value: { command: 'hud' } }))
    on('ui.open', () => ({ value: { isPlaced: true } }))
    on('session.start', (_, e) => ({ cwd: e.cwd }))
    // ring 2 (a button holds the ring) so the hotkey rows draw too.
    const store: Record<string, unknown> = { view: { ring: 2, expand: 0, failed: '' }, ...state }
    on('state.get', (_: unknown, e: { key: string }) => ({ value: { value: store[e.key], version: 1 } }))

    await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

    for (const place of PLACEMENTS) {
      for (const isFocused of [false, true]) {
        const ui = await $.ui.mount({ ...PANE, props: { ...PANE.props, ...place, isFocused } })
        expect((await ui.find({ type: 'Text', text: /Binnacle/ }))?.text).toContain('Binnacle')
        await ui.unmount()
      }
    }
  })
}
