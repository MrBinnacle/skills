export type Tip = { line: string; explanation: string }

// What the person did with a heads-up, keyed by its line.
export type Outcome = 'handed' | 'dismissed'

declare module 'claude-code' {
  interface PluginState {
    'tips-anywhere': {
      tip: Tip | null
      outcomes: Record<string, Outcome>
      expanded: string[]
      asked: string[]
      shown: string[]
    }
  }
}
