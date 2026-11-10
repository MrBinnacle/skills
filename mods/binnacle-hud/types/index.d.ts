/** A thought kept in the Log. `at` is an ISO time; `from` is where it was typed. */
export type Thought = { text: string; at: string; from: 'phone' | 'terminal' }

/** The Memory lines a confirmed Send gave Claude, and when the append landed (epoch ms). */
export type Approved = { lines: string[]; at: number }

/** The pane's own state: where the focus ring is (0 nothing, 1 the field, 2 a button), the open strip section (0 none, 1 memory, 2 watch, 3 log), why the last Send was refused ('' when it was not), when a Send landed that the HUD could not record (0 when none), and what became of the last copy of a cleared draft. */
export type View = { ring: 0 | 1 | 2; expand: number; failed: string; unrecorded?: number; copied?: string }

/** A prompt-box draft that a clear emptied with no submit: its text, when (epoch ms), and the box's change count then. */
export type Lost = { text: string; at: number; moves: number; load: string }

declare module 'claude-code' {
  interface PluginState {
    'binnacle-hud': { view: View; typed: string; log: Thought[]; failed: string[]; memory: string[]; approved: Approved | null; lost: Lost | null }
  }
}
