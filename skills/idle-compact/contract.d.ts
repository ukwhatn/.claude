/**
 * When the main conversation last answered, in milliseconds since the epoch,
 * while that idle stretch is still to be tried; null while a turn runs and
 * once the stretch was tried.
 */
export type IdleCompactLastAnswer = number | null

declare module 'claude-code' {
  interface PluginState {
    'idle-compact': {
      lastAnswer: IdleCompactLastAnswer
    }
  }
}
