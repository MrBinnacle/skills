/** A thought kept in the Log. `at` is an ISO time; `from` is where it was typed. */
export type Thought = { text: string; at: string; from: 'phone' | 'terminal' }

/** A Memory line or a failed keep. `id` is minted when it is saved and never changes. */
export type Entry = { id: string; text: string }

/** What a saved list holds: an entry, or a bare string saved by 4.1.0. */
export type Saved = Entry | string

/** A saved item as the pane draws it: a bare string has no id, so no key acts on it. */
export type Row = { id: string | null; text: string }

/** The Memory lines a confirmed Send gave Claude, and when the append landed (epoch ms). */
export type Approved = { lines: string[]; at: number }

/** The last main-conversation compaction that replayed a snapshot: when it ran (epoch ms), which Send it replayed (`approvedAt`), the row's exact text, and how far the check got. `waiting`: the hook handed the row up. `checking`: the boundary row was stored. `found`: the row was stored after it. `missing`: a prompt or a response was stored first. */
export type Attached = { at: number; approvedAt: number; text: string; state: 'waiting' | 'checking' | 'found' | 'missing' }

/** The pane's own state: where the focus ring is (0 nothing, 1 the field, 2 a button), the open strip section (0 none, 1 memory, 2 watch, 3 log), why the last Send was refused ('' when it was not) and the lines it carried, and when a Send landed that the HUD could not record (0 when none). */
export type View = { ring: 0 | 1 | 2; expand: number; failed: string; refusedLines?: string[]; unrecorded?: number }

declare module 'claude-code' {
  interface PluginState {
    'binnacle-hud': { view: View; typed: string; log: Thought[]; failed: Saved[]; memory: Saved[]; approved: Approved | null; attached: Attached | null }
  }
}
