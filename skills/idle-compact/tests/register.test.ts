import type { On, SessionCompactInput } from 'claude-code'
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

/**
 * The world beneath the mod: a clock, HOME, a conversation of `tokens`, an
 * AGENTS.md, and a core compaction that records what it was told.
 */
function worldOf(on: On, tokens: number) {
  const clock = mock.clock(on)
  const compactions: SessionCompactInput[] = []
  const lines: string[] = []

  mock.env(on, { HOME: '/work/me' })
  on('turn.start', ($, e) => ({ turnId: e.turnId }))
  on('turn.complete', ($, e) => ({ text: e.answer }))
  on('fs.read', ($, e) => {
    if (e.path !== '/work/me/.claude/AGENTS.md') {
      throw new Error(`ENOENT: ${e.path}`)
    }

    return { value: AGENTS_MD }
  })
  on('session.usage', () => ({
    value: { context: { tokens, window: 1_000_000 }, rateLimits: [] },
  }))
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

async function answer($: Engine, turnId: string) {
  await $.turn.start({ text: 'hi', turnId })
  await $.turn.complete({
    answer: 'done',
    durationMs: 1,
    isAborted: false,
    turnId,
    reason: 'answer',
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
      'compacted after 50 idle minutes (70000 → 8000 tokens)',
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

  test('a conversation under minContextTokens is left alone', async ($, on) => {
    const world = worldOf(on, 29_999)

    await answer($, 't1')
    await world.clock.advance(51 * MINUTE_MS)

    expect(world.compactions).toEqual([])
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
