export type Scene = number

declare module 'claude-code' {
  interface PluginState {
    'binnacle-hud': { scene: Shaped<Scene> }
  }
}
