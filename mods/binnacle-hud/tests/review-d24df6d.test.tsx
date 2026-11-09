import { expect, mock, test } from 'claude-code/testing'
const deferred = () => { let resolve!: () => void; const promise = new Promise<void>(r => { resolve = r }); return {promise, resolve} }
const pane = (placement = 'dock') => ({
  plugin: 'binnacle-hud', component: 'Pane', requestId: 'binnacle-hud', surface: 'terminal',
  viewport: { columns: 160, rows: 40, isFullscreen: true },
  props: { title: 'Binnacle', isFocused: true, bodyColumns: 46, placement, scroll: {offset: 0, bodyRows: 32}, view: {} },
}) as const
async function setup($: any, on: any, initial: Record<string, any>, holdDismiss = false) {
  const cells: Record<string, {value: any, version: number}> = Object.fromEntries(Object.entries(initial).map(([k,value]) => [k,{value,version:0}]))
  const cell = (k: string) => cells[k] ?? {value: undefined, version: 0}
  const clock = mock.clock(on, {now: Date.UTC(2026,10,9,14,2)})
  const entered = deferred(), release = deferred(), otherDismissed = deferred(), freshCaptured = deferred()
  let held = false, denyAppend = false
  const session = mock.session(on)
  on('command.register', () => ({value: undefined}))
  on('ui.open', () => ({value: {isPlaced: true}}))
  on('ui.focus', () => ({value: {}}))
  on('session.start', (_: any, e: any) => ({cwd: e.cwd}))
  on('state.get', (_: any, e: any) => ({value: {...cell(e.key)}}))
  on('state.set', async (_: any, e: any) => {
    if (e.key === 'approved') return {deny: 'injected approval write failure'}
    if (e.key === 'log' && holdDismiss) return {deny: 'injected keep failure'}
    if (e.key === 'failed' && holdDismiss && !held) { held = true; entered.resolve(); await release.promise }
    const old = cell(e.key)
    if (e.ifVersion !== undefined && e.ifVersion !== old.version) return {value: {isSet: false, version: old.version}}
    cells[e.key] = {value: e.value, version: old.version + 1}
    if (e.key === 'failed') {
      otherDismissed.resolve()
      if (e.value.includes('new unseen failure')) freshCaptured.resolve()
    }
    return {value: {isSet: true, version: old.version + 1}}
  })
  on('tool.call', (_: any, e: any) => ({result: {answers: {[e.questions[0].question]: 'Send'}}}))
  on('session.append', {door: 'note'}, (_: any, e: any, next: any) => denyAppend ? {deny: 'injected append refusal'} : next(e))
  await $.session.start({cwd: '/', surface: 'terminal', isInteractive: true})
  return {clock, cells, cell, entered, release, otherDismissed, freshCaptured, appends: () => session.appended().length, refuseAppend: () => {denyAppend = true}}
}
for (const placement of ['dock', 'inline']) {
  test(`review ${placement}: landed append and refused approval report success honestly`, {options: {narrow: 'strip'}}, async ($, on) => {
    const s = await setup($, on, {memory: ['approved synthetic line'], view: {ring: 2, expand: 1, failed: ''}})
    const ui = await $.ui.mount(pane(placement))
    await ui.press({key: 'k-s'}); await s.clock.settle(); await ui.unmount()
    const after = await $.ui.mount(pane(placement))
    const text = JSON.stringify(await after.drawn()); await after.unmount()
    expect(s.appends()).toBe(1)
    expect(s.cell('approved').value).toBeUndefined()
    expect(text).toContain('Claude has the lines sent at')
    expect(text).not.toContain('Not sent.')
  })
  test(`review ${placement}: a later refused send must not erase the last landed unrecorded Send`, {options: {narrow: 'strip'}}, async ($, on) => {
    const s = await setup($, on, {memory: ['first landed line'], view: {ring: 2, expand: 1, failed: ''}})
    const ui = await $.ui.mount(pane(placement))
    await ui.press({key: 'k-s'}); await s.clock.settle(); await ui.unmount()
    expect(s.appends()).toBe(1)
    expect(s.cell('view').value.unrecorded).toBeGreaterThan(0)
    s.cells.memory = {value: ['second refused line'], version: 1}
    s.refuseAppend()
    const second = await $.ui.mount(pane(placement))
    await second.press({key: 'k-s'}); await s.clock.settle(); await second.unmount()
    const final = await $.ui.mount(pane(placement))
    const text = JSON.stringify(await final.drawn()); await final.unmount()
    expect(s.appends()).toBe(1)
    expect(text).toContain('Claude has the lines sent at')
  })
}
for (const visible of ['old visible failure', 'new unseen failure']) {
test(`review: overlapping dismissals preserve fresh failure, old text=${visible}`, async ($, on) => {
  const s = await setup($, on, {failed: [visible]}, true)
  const ui = await $.ui.mount(pane())
  await ui.press({key: 'k-d'}); await s.entered.promise
  await ui.press({key: 'k-d'}); await s.otherDismissed.promise
  expect(s.cell('failed').value).toEqual([])
  // Use the real Input/keep path to append a failed capture after dismissal.
  await $.ui.input({plugin: 'binnacle-hud', key: 'thought', text: 'new unseen failure'})
  await s.freshCaptured.promise
  expect(s.cell('failed').value).toEqual(['new unseen failure'])
  s.release.resolve(); await s.clock.settle()
  await ui.unmount()
  expect(s.cell('failed').value).toEqual(['new unseen failure'])
})
}
