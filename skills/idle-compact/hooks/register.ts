import type { EngineInterface, On, PluginOptions, Timer } from 'claude-code'

import { compactInstructionsOf, joinedInstructions } from './compact-instructions.js'

const MINUTE_MS = 60_000

type Turns = {
  isRunning: boolean
}

type Settings = {
  idleMs: number
  cutoffMs: number
  minContextTokens: number
  instructionsPath: string
}

/**
 * Registers the idle compaction of the main conversation and the Compact
 * Instructions every compaction of it is handed.
 *
 * One timer per answer: a turn start cancels it, the next answer re-arms it,
 * so an idle stretch compacts at most once.
 *
 * @param on the engine's registrar
 * @param options `idleMinutes`, `cutoffMinutes`, `minContextTokens`,
 * `instructionsPath` as the manifest declares them
 */
export function register(on: On, options: PluginOptions): void {
  const settings = settingsOf(options)
  const turns: Turns = { isRunning: false }
  let idleTimer: Timer | undefined

  on('turn.start', ($, e, next) => {
    turns.isRunning = true
    idleTimer?.cancel()
    idleTimer = undefined

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)

    if (e.agentId !== undefined) {
      return result
    }

    turns.isRunning = false
    const answeredAt = await $.clock.now()
    idleTimer?.cancel()
    idleTimer = $.clock.after(settings.idleMs, () => {
      idleTimer = undefined
      void compactIfIdle($, turns, settings, answeredAt)
    })

    return result
  })

  on('session.compact', async ($, e, next) => {
    if (e.agentId !== undefined) {
      return next(e)
    }

    const section = await sectionOf($, settings.instructionsPath)

    return section === undefined
      ? next(e)
      : next({ ...e, instructions: joinedInstructions(section, e.instructions) })
  })
}

/**
 * Compacts the main conversation when it is still idle: no turn running,
 * the timer not fired past the cutoff, the context over the minimum.
 */
async function compactIfIdle(
  $: EngineInterface,
  turns: Turns,
  settings: Settings,
  answeredAt: number,
): Promise<void> {
  if (turns.isRunning) {
    return
  }

  const idleFor = (await $.clock.now()) - answeredAt

  if (idleFor > settings.cutoffMs) {
    return
  }

  const { context } = await $.session.usage()

  if ((context.tokens ?? 0) < settings.minContextTokens) {
    return
  }

  // Our own call skips our session.compact hook, so the section rides here.
  const section = await sectionOf($, settings.instructionsPath)
  const result = await $.session
    .compact(section === undefined ? undefined : { instructions: section })
    .catch((error: unknown) => {
      $.ui.log(`compaction failed: ${String(error)}`)

      return undefined
    })

  if (result?.skip !== undefined) {
    $.ui.log(`compaction skipped: ${result.skip}`)
  }

  if (result?.messages !== undefined) {
    const sizes =
      result.tokensBefore !== undefined && result.tokensAfter !== undefined
        ? ` (${result.tokensBefore} → ${result.tokensAfter} tokens)`
        : ''
    $.ui.log(`compacted after ${Math.round(idleFor / MINUTE_MS)} idle minutes${sizes}`)
  }
}

/**
 * The options as numbers and a path; a missing or non-positive value takes
 * the manifest's default.
 */
function settingsOf(options: PluginOptions): Settings {
  const positive = (value: unknown, fallback: number): number =>
    typeof value === 'number' && Number.isFinite(value) && value > 0
      ? value
      : fallback
  const path = options.instructionsPath

  return {
    idleMs: positive(options.idleMinutes, 50) * MINUTE_MS,
    cutoffMs: positive(options.cutoffMinutes, 56) * MINUTE_MS,
    minContextTokens: positive(options.minContextTokens, 30_000),
    instructionsPath: typeof path === 'string' ? path.trim() : '',
  }
}

/**
 * The Compact Instructions section of the configured file, or of the
 * person's AGENTS.md; undefined when the file or the section is missing.
 */
async function sectionOf(
  $: EngineInterface,
  configured: string,
): Promise<string | undefined> {
  const path = configured !== '' ? configured : await defaultPathOf($)

  if (path === undefined) {
    return undefined
  }

  const text = await $.fs.read(path).catch(() => undefined)

  return typeof text === 'string' ? compactInstructionsOf(text) : undefined
}

async function defaultPathOf($: EngineInterface): Promise<string | undefined> {
  const [configDir, home] = await Promise.all([
    $.env.get('CLAUDE_CONFIG_DIR'),
    $.env.get('HOME'),
  ])
  const dir = configDir ?? (home === undefined ? undefined : `${home}/.claude`)

  return dir === undefined ? undefined : `${dir}/AGENTS.md`
}
