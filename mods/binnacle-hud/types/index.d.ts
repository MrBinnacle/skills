/** A thought kept in the Log. `at` is an ISO time; `from` is where it was typed. */
export type Thought = { text: string; at: string; from: 'phone' | 'terminal' }

/** The Memory lines a confirmed Send gave Claude, and when the append landed (epoch ms). */
export type Approved = { lines: string[]; at: number }

/** The pane's own state: where the focus ring is (0 nothing, 1 the field, 2 a button), the open strip section (0 none, 1 memory, 2 watch, 3 log), and why the last Send was refused ('' when it was not). */
export type View = { ring: 0 | 1 | 2; expand: number; failed: string }

declare module 'claude-code' {
  interface PluginState {
    'binnacle-hud': { view: View; typed: string; log: Thought[]; failed: string[]; memory: string[]; approved: Approved | null }
  }
}
