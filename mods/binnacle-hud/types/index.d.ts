export type Scene = number

/** A thought kept in the Log. `at` is an ISO time; `from` is where it was typed. */
export type Thought = { text: string; at: string; from: 'phone' | 'terminal' }

declare module 'claude-code' {
  interface PluginState {
    'binnacle-hud': { scene: Shaped<Scene>; typed: string; log: Thought[] }
  }
}
