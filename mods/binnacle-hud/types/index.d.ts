/** A thought kept in the Log. `at` is an ISO time; `from` is where it was typed. */
export type Thought = { text: string; at: string; from: 'phone' | 'terminal' }

/** A Memory line or a failed keep. `id` is minted when it is saved and never changes. */
export type Entry = { id: string; text: string }

/** What a saved list holds: an entry, or a bare string saved by 4.1.0. */
export type Saved = Entry | string

/** A saved item as the pane draws it: a bare string has no id, so no key acts on it. */
export type Row = { id: string | null; text: string }

/** The Memory lines a confirmed Send gave Claude's system prompt, and when Send was confirmed (epoch ms). */
export type Approved = { lines: string[]; at: number }

/** The Send the memory section hook last carried (its `at`), and when the hook first carried it (epoch ms). */
export type Delivered = { at: number; since: number }

/** A note the side-note agent offered: its key (the turn id it was written with), its cleaned line and details, when it came (epoch ms), and how it reached Claude. */
export type Note = { key: string; line: string; explanation: string; at: number; how: 'own turn' | 'waiting' | 'with your message' }

/** The session's notes, oldest first, and whether a note may still take a turn of its own before the person next speaks. */
export type Notes = { list: Note[]; free: boolean }

/** The pane's own state: where the focus ring is (0 nothing, 1 the field, 2 a button), the open section (0 none, 1 memory, 2 log, 4 heads-ups; 1 and 2 on the strip only; 3 was Watch and reads as none), and why the last Send was not saved ('' when it was) with the lines it carried. */
export type View = { ring: 0 | 1 | 2; expand: number; failed: string; refusedLines?: string[] }

declare module 'claude-code' {
  interface PluginState {
    'binnacle-hud': { view: View; typed: string; log: Thought[]; failed: Saved[]; memory: Saved[]; approved: Approved | null; delivered: Delivered | null; notes: Notes }
  }
}
