import type { EngineInterface, On, PluginOptions, Timer } from 'claude-code'

import { compactInstructionsOf, joinedInstructions } from './compact-instructions.js'

const MINUTE_MS = 60_000

const lastAnswer = { plugin: 'idle-compact', key: 'lastAnswer' } as const

type Idle = {
  timer: Timer | undefined
}

type Settings = {
  idleMs: number
  cutoffMs: number
  minMessageTokens: number
  instructionsPath: string
}

/**
 * Registers the idle compaction of the main conversation and the Compact
 * Instructions every compaction of it is handed.
 *
 * One timer per answer: a turn start cancels it, the next answer re-arms it,
 * so an idle stretch compacts at most once. The answer's time lives in
 * `$.state`, so a reload of this module re-arms the timer for what is left.
 *
 * @param on the engine's registrar
 * @param options `idleMinutes`, `cutoffMinutes`, `minMessageTokens`,
 * `instructionsPath` as the manifest declares them
 */
export function register(on: On, options: PluginOptions): void {
  const settings = settingsOf(options)
  const idle: Idle = { timer: undefined }

  on('session.start', async ($, e, next) => {
    const result = await next(e)
    const { value: answeredAt } = await $.state.get(lastAnswer)

    if (typeof answeredAt === 'number') {
      const idleFor = (await $.clock.now()) - answeredAt
      armIdle($, idle, settings, Math.max(0, settings.idleMs - idleFor), answeredAt)
    }

    return result
  })

  on('turn.start', async ($, e, next) => {
    idle.timer?.cancel()
    idle.timer = undefined
    await $.state.set(lastAnswer, null)

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)

    // A turn with no response (an API error, an interrupt before one) left
    // the cache where the last response did.
    if (e.agentId !== undefined || e.usage === undefined) {
      return result
    }

    const answeredAt = await $.clock.now()
    await $.state.set(lastAnswer, answeredAt)
    armIdle($, idle, settings, settings.idleMs, answeredAt)

    return result
  })

  on('session.compact', async ($, e, next) => {
    if (e.agentId !== undefined) {
      return next(e)
    }

    const section = await sectionOf($, settings.instructionsPath)
    const result = await next(
      section === undefined
        ? e
        : { ...e, instructions: joinedInstructions(section, e.instructions) },
    )

    // A precompute replaces nothing, so the idle stretch still stands.
    if (e.trigger !== 'precompute' && result.messages !== undefined) {
      idle.timer?.cancel()
      idle.timer = undefined
      await $.state.set(lastAnswer, null)
    }

    return result
  })
}

/**
 * Replaces the pending idle timer with one that tries the stretch of the
 * answer at `answeredAt` after `delayMs`.
 */
function armIdle(
  $: EngineInterface,
  idle: Idle,
  settings: Settings,
  delayMs: number,
  answeredAt: number,
): void {
  idle.timer?.cancel()
  idle.timer = $.clock.after(delayMs, () => {
    idle.timer = undefined
    void compactIfIdle($, settings, answeredAt).catch((error: unknown) => {
      $.ui.log(`idle compaction failed: ${String(error)}`)
    })
  })
}

/**
 * Compacts the main conversation when it is still idle: no turn running
 * since `answeredAt`, the timer not fired past the cutoff, the conversation
 * over the minimum. Says why when it does not.
 */
async function compactIfIdle(
  $: EngineInterface,
  settings: Settings,
  answeredAt: number,
): Promise<void> {
  const held = await $.state.get(lastAnswer)

  if (held.value !== answeredAt) {
    if (held.value === null) {
      $.ui.log('idle compaction skipped: a turn is running')
    }

    return
  }

  // Claimed before the usage read and the compaction: a reload while they run
  // finds null and re-arms nothing.
  const claim = await $.state.set(lastAnswer, null, { ifVersion: held.version })

  if (!claim.isSet) {
    return
  }

  const idleFor = (await $.clock.now()) - answeredAt
  const idleMinutes = Math.round(idleFor / MINUTE_MS)

  if (idleFor > settings.cutoffMs) {
    $.ui.log(
      `idle compaction skipped: ${idleMinutes} minutes since the last answer, past cutoffMinutes (${settings.cutoffMs / MINUTE_MS})`,
    )

    return
  }

  const messageTokens = await messageTokensOf($)

  if (messageTokens === undefined) {
    $.ui.log('idle compaction skipped: the context breakdown has no Messages row')

    return
  }

  if (messageTokens < settings.minMessageTokens) {
    $.ui.log(
      `idle compaction skipped: ${messageTokens} message tokens, under minMessageTokens (${settings.minMessageTokens})`,
    )

    return
  }

  // Our own call skips our session.compact hook, so the section rides here.
  const section = await sectionOf($, settings.instructionsPath)
  const result = await $.session.compact(
    section === undefined ? undefined : { instructions: section },
  )

  if (result.skip !== undefined) {
    $.ui.log(`compaction skipped: ${result.skip}`)
  }

  if (result.messages !== undefined) {
    const sizes =
      result.tokensBefore !== undefined && result.tokensAfter !== undefined
        ? ` (${result.tokensBefore} → ${result.tokensAfter} tokens)`
        : ''
    $.ui.log(`compacted after ${idleMinutes} idle minutes${sizes}`)
  }
}

/**
 * The options as numbers and a path; a missing or non-positive value takes
 * the manifest's default.
 */
function settingsOf(options: PluginOptions): Settings {
  const atLeast = (min: number) => (value: unknown, fallback: number): number =>
    typeof value === 'number' && Number.isFinite(value) && value >= min
      ? value
      : fallback
  const positive = atLeast(Number.MIN_VALUE)
  const path = options.instructionsPath

  return {
    idleMs: positive(options.idleMinutes, 50) * MINUTE_MS,
    cutoffMs: positive(options.cutoffMinutes, 56) * MINUTE_MS,
    minMessageTokens: atLeast(0)(options.minMessageTokens, 30_000),
    instructionsPath: typeof path === 'string' ? path.trim() : '',
  }
}

/**
 * The conversation's tokens as /context's Messages row estimates them: the
 * part a compaction shrinks, without the system prompt, tools and memory
 * files it leaves in place.
 */
async function messageTokensOf($: EngineInterface): Promise<number | undefined> {
  const { context } = await $.session.usage({ breakdown: 'summary' })

  // The row name is the only mark: no ContextCategoryKind tells messages apart.
  return context.breakdown?.categories.find(
    row => row.kind === 'used' && row.name === 'Messages',
  )?.tokens
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

  if (typeof text !== 'string') {
    $.ui.log(`compact instructions skipped: ${path} could not be read`)

    return undefined
  }

  const section = compactInstructionsOf(text)

  if (section === undefined) {
    $.ui.log(`compact instructions skipped: ${path} has no Compact Instructions section`)
  }

  return section
}

async function defaultPathOf($: EngineInterface): Promise<string | undefined> {
  const [configDir, home] = await Promise.all([
    $.env.get('CLAUDE_CONFIG_DIR'),
    $.env.get('HOME'),
  ])
  const dir = configDir ?? (home === undefined ? undefined : `${home}/.claude`)

  return dir === undefined ? undefined : `${dir}/AGENTS.md`
}
