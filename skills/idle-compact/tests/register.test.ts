import type { On, SessionCompactInput, SessionContextBreakdown } from 'claude-code'
import type { Engine } from 'claude-code/testing'
import { describe, expect, mock, test, tier } from 'claude-code/testing'

tier('user')

const MINUTE_MS = 60_000

const SUMMARY = [{ role: 'user' as const, text: 'summary', toolUses: [] }]

const AGENTS_MD = [
  '# Global',
  '',
  '## Compact Instructions',
  '',
  'Keep the running subagents and the plan path.',
  '',
  '## Other',
  'not this',
].join('\n')

const FIXED_TOKENS = 50_000

/**
 * The /context rows of a window whose conversation is `messages` tokens over
 * a fixed part (system prompt, tools, memory files) of FIXED_TOKENS.
 */
function breakdownOf(messages: number | undefined): SessionContextBreakdown {
  const row = (name: string, tokens: number) => ({
    name,
    tokens,
    color: 'inactive',
    isDeferred: false,
    kind: 'used' as const,
  })
  const categories = [
    row('System prompt', 3_000),
    row('System tools', 20_000),
    row('Memory files', FIXED_TOKENS - 23_000),
    ...(messages === undefined ? [] : [row('Messages', messages)]),
  ]

  return { categories } as unknown as SessionContextBreakdown
}

const NOW = 1_000 * MINUTE_MS

/**
 * The world beneath the mod: a clock at NOW, HOME, a conversation of
 * `messages` tokens (no Messages row when undefined), an AGENTS.md, the
 * session's state as a reload finds it (`lastAnswer`), and a core compaction
 * that records what it was told.
 */
type WorldOptions = {
  /** The state a reload finds; unset when never written. */
  lastAnswer?: number | null
  /** AGENTS.md's text; null when the file cannot be read. */
  agentsMd?: string | null
  /** Makes `$.session.usage` fail with this message. */
  usageError?: string
}

function worldOf(on: On, messages: number | undefined, options: WorldOptions = {}) {
  const { lastAnswer, agentsMd = AGENTS_MD, usageError } = options
  const tokens = FIXED_TOKENS + (messages ?? 0)
  const clock = mock.clock(on, { now: NOW })
  const compactions: SessionCompactInput[] = []
  const lines: string[] = []
  const state = { value: lastAnswer, version: lastAnswer === undefined ? 0 : 1 }

  mock.env(on, { HOME: '/work/me' })
  on('session.start', ($, e) => ({ cwd: e.cwd }))
  on('state.get', () => ({ value: { value: state.value, version: state.version } }))
  on('state.set', ($, e) => {
    if (e.ifVersion !== undefined && e.ifVersion !== state.version) {
      return { value: { isSet: false, version: state.version } }
    }

    state.value = e.value as number | null
    state.version += 1

    return { value: { isSet: true, version: state.version } }
  })
  on('turn.start', ($, e) => ({ turnId: e.turnId }))
  on('turn.complete', ($, e) => ({ text: e.answer }))
  on('fs.read', ($, e) => {
    if (e.path !== '/work/me/.claude/AGENTS.md' || agentsMd === null) {
      throw new Error(`ENOENT: ${e.path}`)
    }

    return { value: agentsMd }
  })
  on('session.usage', ($, e) => {
    if (usageError !== undefined) {
      throw new Error(usageError)
    }

    return {
      value: {
        startedAt: 0,
        context: {
          tokens,
          window: 1_000_000,
          ...(e.breakdown === undefined ? {} : { breakdown: breakdownOf(messages) }),
        },
        rateLimits: [],
      },
    }
  })
  on('session.compact', ($, e) => {
    compactions.push(e)

    return { messages: SUMMARY, tokensBefore: tokens, tokensAfter: 8_000 }
  })
  on('ui.log', ($, e) => {
    lines.push(e.text)

    return { value: undefined }
  })

  return { clock, compactions, lines }
}

async function reload($: Engine) {
  await $.session.start({ cwd: '/work', surface: 'terminal', isInteractive: true })
}

const USAGE = {
  input_tokens: 10,
  output_tokens: 10,
  cache_read_input_tokens: 100_000,
  cache_creation_input_tokens: 0,
  model: 'claude-opus-5-5',
}

async function answer($: Engine, turnId: string) {
  await $.turn.start({ text: 'hi', turnId })
  await $.turn.complete({
    answer: 'done',
    durationMs: 1,
    isAborted: false,
    turnId,
    reason: 'answer',
    usage: USAGE,
  })
}

describe('register', () => {
  test('a large conversation idle for idleMinutes compacts once with the section', async ($, on) => {
    const world = worldOf(on, 70_000)

    await answer($, 't1')
    await world.clock.advance(49 * MINUTE_MS)

    expect(world.compactions).toEqual([])

    await world.clock.advance(1 * MINUTE_MS)
    await world.clock.advance(60 * MINUTE_MS)

    expect(world.compactions.map(c => c.instructions)).toEqual([
      'Keep the running subagents and the plan path.',
    ])
    expect(world.lines).toEqual([
      'compacted after 50 idle minutes (120000 → 8000 tokens)',
    ])
  })

  test('a new turn before idleMinutes cancels the idle compaction', async ($, on) => {
    const world = worldOf(on, 70_000)

    await answer($, 't1')
    await world.clock.advance(40 * MINUTE_MS)
    await $.turn.start({ text: 'more', turnId: 't2' })
    await world.clock.advance(20 * MINUTE_MS)

    expect(world.compactions).toEqual([])
  })

  test('a conversation under minMessageTokens is left alone', async ($, on) => {
    const world = worldOf(on, 29_999)

    await answer($, 't1')
    await world.clock.advance(51 * MINUTE_MS)

    expect(world.compactions).toEqual([])
    expect(world.lines).toEqual([
      'idle compaction skipped: 29999 message tokens, under minMessageTokens (30000)',
    ])
  })

  test('a fixed part over minMessageTokens does not count toward it', async ($, on) => {
    const world = worldOf(on, 1_000)

    await answer($, 't1')
    await world.clock.advance(51 * MINUTE_MS)

    expect(world.compactions).toEqual([])
    expect(world.lines).toEqual([
      'idle compaction skipped: 1000 message tokens, under minMessageTokens (30000)',
    ])
  })

  test('a reload re-arms for the rest of the idle stretch', async ($, on) => {
    const world = worldOf(on, 70_000, { lastAnswer: NOW - 20 * MINUTE_MS })

    await reload($)
    await world.clock.advance(29 * MINUTE_MS)

    expect(world.compactions).toEqual([])

    await world.clock.advance(1 * MINUTE_MS)

    expect(world.lines).toEqual([
      'compacted after 50 idle minutes (120000 → 8000 tokens)',
    ])
  })

  test('a reload past cutoffMinutes compacts nothing and says so', async ($, on) => {
    const world = worldOf(on, 70_000, { lastAnswer: NOW - 57 * MINUTE_MS })

    await reload($)
    await world.clock.advance(0)

    expect(world.compactions).toEqual([])
    expect(world.lines).toEqual([
      'idle compaction skipped: 57 minutes since the last answer, past cutoffMinutes (56)',
    ])
  })

  test('a reload after the stretch was tried arms nothing', async ($, on) => {
    const world = worldOf(on, 70_000)

    await answer($, 't1')
    await world.clock.advance(50 * MINUTE_MS)
    await reload($)
    await world.clock.advance(60 * MINUTE_MS)

    expect(world.compactions.length).toBe(1)
  })

  test('a reload while a turn runs arms nothing', async ($, on) => {
    const world = worldOf(on, 70_000)

    await answer($, 't1')
    await $.turn.start({ text: 'more', turnId: 't2' })
    await reload($)
    await world.clock.advance(60 * MINUTE_MS)

    expect(world.compactions).toEqual([])
    expect(world.lines).toEqual([])
  })

  test('a breakdown without a Messages row compacts nothing and says so', async ($, on) => {
    const world = worldOf(on, undefined)

    await answer($, 't1')
    await world.clock.advance(51 * MINUTE_MS)

    expect(world.compactions).toEqual([])
    expect(world.lines).toEqual([
      'idle compaction skipped: the context breakdown has no Messages row',
    ])
  })

  test('a turn that got no response arms nothing', async ($, on) => {
    const world = worldOf(on, 70_000)

    await $.turn.start({ text: 'hi', turnId: 't1' })
    await $.turn.complete({
      answer: '',
      durationMs: 1,
      isAborted: false,
      turnId: 't1',
      reason: 'error',
    })
    await world.clock.advance(60 * MINUTE_MS)

    expect(world.compactions).toEqual([])
  })

  test('an interrupted turn that got a response arms the timer', async ($, on) => {
    const world = worldOf(on, 70_000)

    await $.turn.start({ text: 'hi', turnId: 't1' })
    await $.turn.complete({
      answer: '',
      durationMs: 1,
      isAborted: true,
      turnId: 't1',
      reason: 'aborted',
      usage: USAGE,
    })
    await world.clock.advance(50 * MINUTE_MS)

    expect(world.compactions.length).toBe(1)
  })

  test('a /compact while idle ends the idle stretch', async ($, on) => {
    const world = worldOf(on, 70_000)

    await answer($, 't1')
    await world.clock.advance(10 * MINUTE_MS)
    await $.session.compact({ trigger: 'manual', messages: SUMMARY })
    await world.clock.advance(60 * MINUTE_MS)
    await reload($)
    await world.clock.advance(60 * MINUTE_MS)

    expect(world.compactions.map(c => c.trigger)).toEqual(['manual'])
    expect(world.lines).toEqual([])
  })

  test('a precompute leaves the idle stretch running', async ($, on) => {
    const world = worldOf(on, 70_000)

    await answer($, 't1')
    await $.session.compact({ trigger: 'precompute', messages: SUMMARY })
    await world.clock.advance(50 * MINUTE_MS)

    expect(world.compactions.length).toBe(2)
  })

  test('a failure inside the idle compaction is said', async ($, on) => {
    const world = worldOf(on, 70_000, { usageError: 'usage unavailable' })

    await answer($, 't1')
    await world.clock.advance(50 * MINUTE_MS)

    expect(world.compactions).toEqual([])
    expect(world.lines).toEqual([
      expect.stringMatching(/^idle compaction failed: /),
    ])
  })

  test('an instructions file without the section is said', async ($, on) => {
    const world = worldOf(on, 70_000, { agentsMd: '# Global\n' })

    await $.session.compact({ trigger: 'manual', messages: SUMMARY })

    expect(world.compactions.map(c => c.instructions)).toEqual([undefined])
    expect(world.lines).toEqual([
      'compact instructions skipped: /work/me/.claude/AGENTS.md has no Compact Instructions section',
    ])
  })

  test('an instructions file that cannot be read is said', async ($, on) => {
    const world = worldOf(on, 70_000, { agentsMd: null })

    await $.session.compact({ trigger: 'manual', messages: SUMMARY })

    expect(world.lines).toEqual([
      'compact instructions skipped: /work/me/.claude/AGENTS.md could not be read',
    ])
  })

  test('a subagent answer arms nothing', async ($, on) => {
    const world = worldOf(on, 70_000)

    await $.turn.complete({
      answer: 'sub',
      durationMs: 1,
      isAborted: false,
      turnId: 's1',
      agentId: 'agent-1',
      reason: 'answer',
    })
    await world.clock.advance(51 * MINUTE_MS)

    expect(world.compactions).toEqual([])
  })

  test('a /compact is handed the section before what was typed', async ($, on) => {
    const world = worldOf(on, 70_000)

    await $.session.compact({
      trigger: 'manual',
      messages: SUMMARY,
      instructions: 'keep the failing test names',
    })

    expect(world.compactions.map(c => c.instructions)).toEqual([
      'Keep the running subagents and the plan path.\n\nkeep the failing test names',
    ])
  })
})
