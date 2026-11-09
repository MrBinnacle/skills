import { expect, test } from 'claude-code/testing'

// Mounts design 2 in every scene, docked and inline, with and without the
// keys, on the terminal. The one thing this proves: no tree is refused (a
// refused Pane tree closes the pane in a live session). It proves nothing
// about paint, hover or focus: only the terminal shows those.
//
// Run from the mod folder once design-2-register.tsx is its hooks/register.tsx
// and this file sits in tests/: `claude plugin test <mod folder>`. Not run by
// the Pi session that wrote it (2026-11-08); the typecheck is the only check.

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

for (const scene of [0, 1, 2, 3, 4]) {
  test(`scene ${scene} mounts in every placement, focused or not`, async ($, on) => {
    on('command.register', () => ({ value: { command: 'hud' } }))
    on('ui.open', () => ({ value: { isPlaced: true } }))
    on('session.start', (_, e) => ({ cwd: e.cwd }))
    // ring 2 (a button holds the ring) so the hotkey rows draw too.
    on('state.get', (_: unknown, e: { key: string }) => ({ value: e.key === 'typed' ? { value: '', version: 1 } : e.key === 'log' ? { value: [], version: 1 } : { value: { shape: 'scene-2', value: scene + 2000 }, version: 1 } }))

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
